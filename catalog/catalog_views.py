import ftplib
import logging
import traceback
import shutil
import os

from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from Mask_DP.settings import MES_USER
from catalog.models import tool_maintain
from infotree.models import released_info_alta, released_info
from jdv.models import lot_info, mes_blank_code
from making.models import convert_status
from tooling_form.models import product_info
from utilslibrary.base.base import BaseView
from infotree.models import cec, cd_map
from utilslibrary.mes_webservice.mes_demo.MES_LotInfoInq import lotinfo_inquery
from utilslibrary.mes_webservice.mes_utils import mes_sign_password
from utilslibrary.system_constant import Constant
from utilslibrary.utils.ssh_utils import SSHManager
from utilslibrary.mes_webservice.mes_webservice import mes_op_locate, get_wip_for_task, mes_op_start, mes_op_comp, \
    mes_op_start_cancel, mes_real_op_start, mes_real_op_start_cancel, mes_real_op_comp


log = logging.getLogger('log')


class CatalogList(BaseView):
    def get(self, request):
        tool_id = request.GET.get('tool_id')
        return render(request, 'catalog/catalog_all_info.html', {'tool_id': tool_id})

    def post(self, request):
        super().post(request)
        tool_id = request.POST.get('tool_id')
        exptool = tool_maintain.objects.get(tool_id=tool_id, is_delete=0).exptool
        query_set = lot_info.objects.filter(
            Q(mes_operation_id__contains='FTP') | Q(mes_operation_id__contains='BKP') |
            Q(Q(Q(mes_operation_id__contains='EB') | Q(mes_operation_id__contains='LB')) & ~Q(
                mes_operation_id__contains='PE')), exp_tool=exptool, is_delete=0)
        query_list = []
        for query in query_set.values():
            try:
                security = product_info.objects.get(tip_no=query['tip_no']).security_type
            except:
                security = 'Normal'
            clip, priority = lotinfo_inquery(query['lot_id'], MES_USER)
            query['clip'] = clip
            query['priority'] = priority
            query['security'] = security
            query['tool_id'] = tool_id
            query['blank'] = query['blank_code']
            query_list.append(query)
        final_list = query_list[self.startIndex: self.endIndex]
        data = {'total': len(query_list), 'rows': final_list}
        return JsonResponse(data, safe=False)


@csrf_exempt
def start_catalog(request):
    try:
        lot_info_id = request.POST.get('lot_info_id')
        lot_info.objects.filter(id=lot_info_id).update(catalog_status=1, catalog_error_message="")
        print("lot_info_id", lot_info_id)
        result = catalog_file_upload(lot_info_id).main_fun()
        print(result)
        if result['result']:
            data = {'success': True, 'message': "catalog success"}
            lot_info.objects.filter(id=lot_info_id).update(catalog_status=3, catalog_error_message="")
            return JsonResponse(data, safe=False)
        else:
            data = {'success': False, 'message': result['data']}
            lot_info.objects.filter(id=lot_info_id).update(catalog_status=2, catalog_error_message=result['data'])
            return JsonResponse(data, safe=False)
    except Exception as e:
        traceback.print_exc()
        print(e)
        if 'out of range' in str(e):
            return JsonResponse({"success": False, 'message': 'Info tree not define'})
        data = {'success': False, 'message': str(e)}
        lot_info.objects.filter(id=lot_info_id).update(catalog_status=2, catalog_error_message=str(e))
        return JsonResponse(data, safe=False)


@csrf_exempt
class catalog_file_upload:
    def __init__(self, lot_info_id):
        self.lot_info_id = lot_info_id
        self.catalog_local_path = Constant.CATALOG_LOCAL_PATH
        self.catalog_ftp_server_path = Constant.CATALOG_FTP_SERVER_PATH
        self.catalog_ftp_host = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_HOST']
        self.catalog_ftp_port = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_PORT']
        self.catalog_ftp_account = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_ACCOUNT']
        self.catalog_ftp_password = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_PASSWORD']

    def main_fun(self):
        try:
            # Get lot info data
            get_info_tree_param_result = self.get_info_tree_param()
            print("1 get_info_tree_param_result = ", get_info_tree_param_result['result'])
            print("get_info_tree_param_result_msg = ", get_info_tree_param_result['data'])
            if get_info_tree_param_result['result']:
                """
                param_dict: 
                    mes_carrier_id, tip_no, product_name, mask_ name,
                    tool, node, tone, blank, grade, pattern_density, layer
                """
                param_dict = get_info_tree_param_result['data']
            else:
                return get_info_tree_param_result

            # Get released info data
            get_info_tree_group_result = self.get_info_tree_group(param_dict)
            print("2 get_info_tree_group_result = ", get_info_tree_group_result['result'])
            print("get_info_tree_group_result_msg = ", get_info_tree_group_result['data'])
            if get_info_tree_group_result['result']:
                """
                group_dict: 
                    info_tree_group, mdt_id, mdt_value, cd_map_id, cec_id
                """
                group_dict = get_info_tree_group_result['data']
            else:
                return get_info_tree_group_result

            # Get File path
            create_path_result = self.create_path(group_dict, param_dict)
            print("3 create_path_result = ", create_path_result['result'])
            # print("create_path_result_msg = ", create_path_result['data'])
            if create_path_result['result']:
                """
                path_dict: 
                    source_temp_path, source_path, temp_path,
                    ftp_server_path, layout_ini_path, layout_ini_server_path
                """
                path_dict = create_path_result['data']
            else:
                return create_path_result

            # Get cs_command
            get_info_tree_data_list_result = self.get_info_tree_data_list(param_dict, group_dict)
            print("4 get_info_tree_data_list_result = ", get_info_tree_data_list_result['result'])
            # print("get_info_tree_data_list_result_msg = ", get_info_tree_data_list_result['data'])
            if get_info_tree_data_list_result['result']:
                """
                path_dict:
                    All cs_command or item
                """
                info_data_dict = get_info_tree_data_list_result['data']
            else:
                return get_info_tree_data_list_result

            # mds
            create_mds_file_result = self.create_mds_file(param_dict, group_dict, path_dict, info_data_dict)
            print("5 create_mds_file_result = ", create_mds_file_result['result'])
            if not create_mds_file_result['result']:
                return create_mds_file_result

            # layout.ini
            change_layout_ini_layout_name_result = self.change_layout_ini_layout_name(param_dict, path_dict)
            print("6 change_layout_ini_layout_name_result = ", change_layout_ini_layout_name_result['result'])
            if not change_layout_ini_layout_name_result['result']:
                return change_layout_ini_layout_name_result

            # move_to_ftp_server
            move_to_ftp_server_result = self.move_to_ftp_server(path_dict, group_dict)
            print("move_to_ftp_server_result =", move_to_ftp_server_result['result'])
            if not move_to_ftp_server_result['result']:
                return move_to_ftp_server_result

            # move_to_machine
            move_to_machine_result = self.move_to_machine(path_dict, group_dict)
            print("move_to_machine_result =", move_to_machine_result['result'])
            if not move_to_machine_result['result']:
                return move_to_machine_result

            # esp_data_regist
            esp_data_regist_result = self.esp_data_regist()
            print("esp_data_regist_result =", esp_data_regist_result['result'])
            if not esp_data_regist_result['result']:
                return esp_data_regist_result

            return {"result": True, "data": "success"}
        except Exception as e:
            traceback.print_exc()
            print(e)
            return {"result": False, "data": str(e)}

    def get_info_tree_param(self):
        try:
            print(self.lot_info_id)
            lot_info_data = lot_info.objects.get(id=self.lot_info_id)
            print(lot_info_data)
            mes_carrier_id = lot_info_data.mes_carrier_id
            tip_no = lot_info_data.tip_no
            product_name = lot_info_data.product_name
            mask_name = lot_info_data.mask_name
            tool = lot_info_data.info_tree_tool_id
            node = lot_info_data.rule
            tone = lot_info_data.tone
            grade = lot_info_data.grade
            pattern_density = "0-100"
            layer = lot_info_data.mask_name.split("-")[1]
            print(mes_carrier_id)
            print(tip_no)
            print(product_name)
            print(mask_name)
            print(tool, node, tone, grade, pattern_density, layer)
            print(1)
            # en_list = ['A', 'B', 'C', 'D', 'E', 'D', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            #            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
            # grade_from = \
            #     mes_blank_code.objects.filter(Q(layer_name="*") | Q(layer_name=layer[0:3]), is_delete=0).order_by(
            #         'seq').first().grade_from
            # print("grade_from =", grade_from)
            # grade_to = \
            #     mes_blank_code.objects.filter(Q(layer_name="*") | Q(layer_name=layer[0:3]), is_delete=0).order_by(
            #         'seq').first().grade_to
            # print("grade_to =", grade_to)
            # grade_range = en_list[en_list.index(grade_from):en_list.index(grade_to) + 1]
            # print(grade_range)
            # print(grade in grade_range)
            blank = lot_info_data.blank_code
            print(blank)
            print(mes_carrier_id)
            print(tip_no)
            print(product_name)
            print(mask_name)
            print(tool, node, tone, grade, pattern_density, layer)

            param_dict = {}
            param_dict['mes_carrier_id'] = mes_carrier_id
            param_dict['tip_no'] = tip_no
            param_dict['product_name'] = product_name
            param_dict['mask_name'] = mask_name
            param_dict['tool'] = tool
            param_dict['node'] = node
            param_dict['tone'] = tone
            param_dict['blank'] = blank
            param_dict['grade'] = grade
            param_dict['pattern_density'] = pattern_density
            param_dict['layer'] = layer
            param_dict['mes_lot_family_id'] = lot_info_data.mes_lot_family_id

            return {"result": True, "data": param_dict}
        except Exception as e:
            print("get_info_tree_param error\n", str(e))
            return {"result": False, "data": "get_info_tree_param error\n" + str(e)}

    def get_info_tree_group(self, param_dict):
        try:
            if param_dict['tool'] == 'MS03':
                print(1)
                info_tree_group = released_info_alta.objects.filter(tool=param_dict['tool'], node=param_dict['node'],
                                                                    tone=param_dict['tone'], grade=param_dict['grade'],
                                                                    blank=param_dict['blank'],
                                                                    pattern_density=param_dict['pattern_density'],
                                                                    layer=param_dict['layer'][0:3],
                                                                    is_delete=0).values('group').distinct()[0]['group']
                print(1.1)
                mdt_data = released_info_alta.objects.get(group=info_tree_group, item='MDT')
                cd_map_id = 0
                cec_id = 0
            else:
                print(2)
                print(param_dict['tool'])
                print(param_dict['node'])
                print(param_dict['tone'])
                print(param_dict['grade'])
                print(param_dict['blank'])
                print(param_dict['pattern_density'])
                print(param_dict['layer'])
                info_tree_group = released_info.objects.filter(tool=param_dict['tool'], node=param_dict['node'],
                                                               tone=param_dict['tone'], grade=param_dict['grade'],
                                                               blank=param_dict['blank'],
                                                               pattern_density=param_dict['pattern_density'],
                                                               layer=param_dict['layer'][0:3],
                                                               is_delete=0).values('group').distinct()[0]['group']
                print(2.2)
                mdt_data = released_info.objects.get(group=info_tree_group, cs_command='MDT', is_delete=0)
                cd_map_id = released_info.objects.get(group=info_tree_group, cs_command='CS_POSITIONAL_CD_MAP',
                                                      is_delete=0).cd_map_id
                cec_id = released_info.objects.get(group=info_tree_group, cs_command='CEC_PARAM', is_delete=0).cec_id
                if cd_map_id != 0:
                    cd_map_dat_name = cd_map.objects.get(id=cd_map_id).cd_map_dat_name
                else:
                    cd_map_dat_name = ''

            group_dict = {}
            group_dict['info_tree_group'] = info_tree_group
            group_dict['mdt_id'] = mdt_data.id
            group_dict['mdt_value'] = mdt_data.value
            group_dict['cd_map_id'] = cd_map_id
            group_dict['cec_id'] = cec_id
            group_dict['cd_map_dat_name'] = cd_map_dat_name

            return {"result": True, "data": group_dict}
        except Exception as e:
            print("get_info_tree_group error\n", str(e))
            return {"result": False, "data": str(e)}

    def create_path(self, group_dict, param_dict):
        try:
            machine_folder = Constant.CATALOG_MACHINE_DICT[param_dict['tool']]

            source_temp_path = "/usr/Mask_DP_download/mds_template.mds"
            source_path = self.catalog_local_path + param_dict['mask_name'] + "/layout/level1.mds"
            source_hide_path = self.catalog_local_path + param_dict['mask_name'] + "/layout/.level1.mds"
            temp_path = self.catalog_local_path + param_dict['mask_name'] + "/layout/level1_temp.mds"
            layout_path = self.catalog_local_path + param_dict['mask_name'] + "/layout/"
            layout_ini_path = self.catalog_local_path + param_dict['mask_name'] + "/layout.ini"
            layout_ini_hide_path = self.catalog_local_path + param_dict['mask_name'] + "/.layout.ini"
            layout_cdmap_dat_path = layout_path + group_dict['cd_map_dat_name']
            layout_cdmap_index_path = layout_path + "__index.prm"

            # 中继站
            layout_ini_server_path = self.catalog_ftp_server_path + machine_folder + "/" + \
                                     param_dict['mask_name'] + "/layout.ini"
            ftp_server_mds_path = self.catalog_ftp_server_path + machine_folder + "/" + \
                                  param_dict['mask_name'] + "/layout/level1.mds"
            ftp_server_layout_path = self.catalog_ftp_server_path + machine_folder + "/" + \
                                     param_dict['mask_name'] + "/layout/"
            ftp_server_cdmap_dat_path = ftp_server_layout_path + group_dict['cd_map_dat_name']
            ftp_server_cdmap_index_path = ftp_server_layout_path + "__index.prm"

            # 机台
            _lot_info = lot_info.objects.get(id=self.lot_info_id)
            exp_tool = _lot_info.exp_tool
            tool = _lot_info.info_tree_tool_id
            print(exp_tool)
            _o = tool_maintain.objects.get(exptool=exp_tool)
            tool_maintain_path = _o.path
            machine_main_path = tool_maintain_path
            # machine_main_path = os.path.join(tool_maintain_path, Constant.CATALOG_MACHINE_DICT[tool])
            machine_main_path = os.path.join(machine_main_path, param_dict['mask_name'])

            machine_ip = _o.ip
            machine_host = 21
            machine_account = _o.account
            machine_password = _o.password
            machine_ini_path = os.path.join(machine_main_path, "layout.ini")
            machine_mds_path = os.path.join(machine_main_path, "layout/level1.mds")
            machine_layout_path = os.path.join(machine_main_path, "layout/")
            machine_cdmap_dat_path = os.path.join(machine_layout_path, group_dict['cd_map_dat_name'])
            machine_cdmap_index_path = os.path.join(machine_layout_path, "__index.prm")

            path_dict = {'source_temp_path': source_temp_path,
                         'source_path': source_path,
                         'source_hide_path': source_hide_path,
                         'temp_path': temp_path,
                         'ftp_server_mds_path': ftp_server_mds_path,
                         'ftp_server_layout_path': ftp_server_layout_path,
                         'layout_path': layout_path,
                         'layout_ini_path': layout_ini_path,
                         'layout_ini_hide_path': layout_ini_hide_path,
                         'layout_ini_server_path': layout_ini_server_path,
                         'layout_cdmap_dat_path': layout_cdmap_dat_path,
                         'layout_cdmap_index_path': layout_cdmap_index_path,
                         'ftp_server_cdmap_dat_path': ftp_server_cdmap_dat_path,
                         'ftp_server_cdmap_index_path': ftp_server_cdmap_index_path,
                         'machine_ip': machine_ip,
                         'machine_host': machine_host,
                         'machine_account': machine_account,
                         'machine_password': machine_password,
                         'machine_ini_path': machine_ini_path,
                         'machine_mds_path': machine_mds_path,
                         'machine_layout_path': machine_layout_path,
                         'machine_cdmap_dat_path': machine_cdmap_dat_path,
                         'machine_cdmap_index_path': machine_cdmap_index_path}

            for pp in path_dict:
                print(pp, " = ", path_dict[pp])

            return {"result": True, "data": path_dict}
        except Exception as e:
            print("create_path error\n", str(e))
            return {"result": False, "data": str(e)}

    def get_info_tree_data_list(self, param_dict, group_dict):
        try:
            if param_dict['tool'] == "MS03":
                released_info_alta_data = released_info.objects.filter(group=group_dict['info_tree_group'],
                                                                       is_delete=0).values('item', 'value')
                released_info_alta_data_list = {}
                for data in released_info_alta_data:
                    released_info_alta_data_list[data['item']] = data['value']

                return {"result": True, "data": released_info_alta_data_list}
            else:
                released_info_data = released_info.objects.filter(group=group_dict['info_tree_group'],
                                                                  is_delete=0).values('cs_command', 'value')
                released_info_data_list = {}
                for data in released_info_data:
                    released_info_data_list[data['cs_command']] = data['value']

                return {"result": True, "data": released_info_data_list}
        except Exception as e:
            print("get_info_tree_data_list error\n", str(e))
            return {"result": False, "data": str(e)}

    def create_mds_file(self, param_dict, group_dict, path_dict, info_data_dict):
        try:
            f_1 = open(path_dict['source_hide_path'], "r", encoding="utf-8")
            f_1_data = f_1.readlines()
            f_1.close()

            f_2 = open(path_dict['source_path'], "w+", encoding="utf-8")
            print(f_1_data)
            for i in f_1_data:
                if 'layout_name="' in i:
                    f_2.write('layout_name="' + param_dict['mask_name'] + '-' + param_dict['mes_lot_family_id'] + '";\n')
                elif '{{ lot_id_xx }}' in i:
                    f_2.write(i.replace('{{ lot_id_xx }}', param_dict['mes_carrier_id']))
                elif 'CS_SYSTEM_PARAM="X"' in i:
                    if info_data_dict['CS_SYSTEM_PARAM'] == 'NA':
                        f_2.write(i.replace('CS_SYSTEM_PARAM="X"', '//CS_SYSTEM_PARAM="X"'))
                    else:
                        f_2.write(i.replace('CS_SYSTEM_PARAM="X"',
                                            'CS_SYSTEM_PARAM="' + info_data_dict['CS_SYSTEM_PARAM'] + '"'))
                elif 'CS_MASK_PARAM="X"' in i:
                    if info_data_dict['CS_MASK_PARAM'] == 'NA':
                        f_2.write(i.replace('CS_MASK_PARAM="X"', '//CS_MASK_PARAM="X"'))
                    else:
                        f_2.write(i.replace('CS_MASK_PARAM="X"',
                                            'CS_MASK_PARAM="' + info_data_dict['CS_MASK_PARAM'] + '"'))
                elif 'CS_COLUMN_PARAM="X"' in i:
                    if info_data_dict['CS_COLUMN_PARAM']:
                        f_2.write(i.replace('CS_COLUMN_PARAM="X"',
                                            'CS_COLUMN_PARAM="' + info_data_dict['CS_COLUMN_PARAM'] + '"'))
                    else:
                        f_2.write(i.replace('CS_COLUMN_PARAM="X"', '//CS_COLUMN_PARAM="X"'))
                elif 'CS_STRIPE_LAYER_COUNT=X' in i:
                    if info_data_dict['CS_STRIPE_LAYER_COUNT']:
                        f_2.write(i.replace('CS_STRIPE_LAYER_COUNT=X',
                                            'CS_STRIPE_LAYER_COUNT=' + info_data_dict['CS_STRIPE_LAYER_COUNT']))
                    else:
                        f_2.write(i.replace('CS_STRIPE_LAYER_COUNT=X', '//CS_STRIPE_LAYER_COUNT=X'))
                elif 'CS_SOAKING=X' in i:
                    if info_data_dict['CS_SOAKING'] == 'NA':
                        f_2.write(i.replace('CS_SOAKING=X', '//CS_SOAKING=X'))
                    else:
                        f_2.write(i.replace('CS_SOAKING=X',
                                            'CS_SOAKING=' + info_data_dict['CS_SOAKING']))
                elif 'CS_W_CH_SOAK' in i:
                    if info_data_dict['CS_W_CH_SOAK'] == 'NA':
                        f_2.write(i.replace('CS_W_CH_SOAK=X', '//CS_W_CH_SOAK=X'))
                    else:
                        f_2.write(i.replace('CS_W_CH_SOAK=X',
                                            'CS_W_CH_SOAK=' + info_data_dict['CS_W_CH_SOAK']))
                elif 'CS_IO_CH_WAIT' in i:
                    if info_data_dict['CS_IO_CH_WAIT']:
                        f_2.write(i.replace('CS_IO_CH_WAIT="X"',
                                            'CS_IO_CH_WAIT="' + info_data_dict['CS_IO_CH_WAIT'] + '"'))
                    else:
                        f_2.write(i.replace('CS_IO_CH_WAIT="X"', '//CS_IO_CH_WAIT="X"'))
                elif 'CS_PROX' in i:
                    if info_data_dict['CS_PROX']:
                        f_2.write(i.replace('CS_PROX="X"',
                                            'CS_PROX="' + info_data_dict['CS_PROX'] + '"'))
                    else:
                        f_2.write(i.replace('CS_PROX="X"', '//CS_PROX="X"'))
                elif 'CS_BASE_DOSE' in i:
                    if info_data_dict['CS_BASE_DOSE']:
                        f_2.write(i.replace('CS_BASE_DOSE=X',
                                            'CS_BASE_DOSE=' + info_data_dict['CS_BASE_DOSE']))
                    else:
                        f_2.write(i.replace('CS_BASE_DOSE=X', '//CS_BASE_DOSE=X'))
                elif 'CS_SIGMA1' in i:
                    if info_data_dict['CS_SIGMA1']:
                        f_2.write(i.replace('CS_SIGMA1=X',
                                            'CS_SIGMA1=' + info_data_dict['CS_SIGMA1']))
                    else:
                        f_2.write(i.replace('CS_SIGMA1=X', '//CS_SIGMA1=X'))
                elif 'CS_ETA1' in i:
                    if info_data_dict['CS_ETA1']:
                        f_2.write(i.replace('CS_ETA1=X',
                                            'CS_ETA1=' + info_data_dict['CS_ETA1']))
                    else:
                        f_2.write(i.replace('CS_ETA1=X', '//CS_ETA1=X'))
                elif 'CS_GCD_MESH_SIZE' in i:
                    if info_data_dict['CS_GCD_MESH_SIZE'] == 'NA':
                        f_2.write(i.replace('CS_GCD_MESH_SIZE=X', '//CS_GCD_MESH_SIZE=X'))
                    else:
                        f_2.write(i.replace('CS_GCD_MESH_SIZE=X',
                                            'CS_GCD_MESH_SIZE=' + info_data_dict['CS_GCD_MESH_SIZE']))
                elif 'CS_KBR_PRX_MESH_SIZE' in i:
                    if info_data_dict['CS_KBR_PRX_MESH_SIZE'] == 'NA':
                        f_2.write(i.replace('CS_KBR_PRX_MESH_SIZE=X', '//CS_KBR_PRX_MESH_SIZE=X'))
                    else:
                        f_2.write(i.replace('CS_KBR_PRX_MESH_SIZE=X',
                                            'CS_KBR_PRX_MESH_SIZE=' + info_data_dict['CS_KBR_PRX_MESH_SIZE']))
                elif 'CS_KBR_SW' in i:
                    if info_data_dict['CS_KBR_SW'] == 'NA':
                        f_2.write(i.replace('CS_KBR_SW=X', '//CS_KBR_SW=X'))
                    else:
                        f_2.write(i.replace('CS_KBR_SW=X',
                                            'CS_KBR_SW=' + info_data_dict['CS_KBR_SW']))
                elif 'CS_FEC_MODE' in i:
                    if info_data_dict['CS_FEC_MODE'] == 'NA':
                        f_2.write(i.replace('CS_FEC_MODE=X', '//CS_FEC_MODE=X'))
                    else:
                        f_2.write(i.replace('CS_FEC_MODE=X',
                                            'CS_FEC_MODE=' + info_data_dict['CS_FEC_MODE']))
                elif 'CS_THETA1' in i:
                    if info_data_dict['CS_THETA1'] == 'NA':
                        f_2.write(i.replace('CS_THETA1=X', '//CS_THETA1=X'))
                    else:
                        f_2.write(i.replace('CS_THETA1=X',
                                            'CS_THETA1=' + info_data_dict['CS_THETA1']))
                elif 'CS_SIGMAF1' in i:
                    if info_data_dict['CS_SIGMAF1'] == 'NA':
                        f_2.write(i.replace('CS_SIGMAF1=X', '//CS_SIGMAF1=X'))
                    else:
                        f_2.write(i.replace('CS_SIGMAF1=X',
                                            'CS_SIGMAF1=' + info_data_dict['CS_SIGMAF1']))
                elif 'CS_LEC_MODE' in i:
                    if info_data_dict['CS_LEC_MODE'] == 'NA':
                        f_2.write(i.replace('CS_LEC_MODE=X', '//CS_LEC_MODE=X'))
                    else:
                        f_2.write(i.replace('CS_LEC_MODE=X',
                                            'CS_LEC_MODE=' + info_data_dict['CS_LEC_MODE']))
                elif 'CS_GAMMA1' in i:
                    if info_data_dict['CS_GAMMA1'] == 'NA':
                        f_2.write(i.replace('CS_GAMMA1=X', '//CS_GAMMA1=X'))
                    else:
                        f_2.write(i.replace('CS_GAMMA1=X',
                                            'CS_GAMMA1=' + info_data_dict['CS_GAMMA1']))
                elif 'CS_SIGMAL1' in i:
                    if info_data_dict['CS_SIGMAL1'] == 'NA':
                        f_2.write(i.replace('CS_SIGMAL1=X', '//CS_SIGMAL1=X'))
                    else:
                        f_2.write(i.replace('CS_SIGMAL1=X',
                                            'CS_SIGMAL1=' + info_data_dict['CS_SIGMAL1']))
                elif 'CS_TEC_MODE' in i:
                    if info_data_dict['CS_TEC_MODE'] == 'NA':
                        f_2.write(i.replace('CS_TEC_MODE=X', '//CS_TEC_MODE=X'))
                    else:
                        f_2.write(i.replace('CS_TEC_MODE=X',
                                            'CS_TEC_MODE=' + info_data_dict['CS_TEC_MODE']))
                elif 'CS_TEC_COEF_DC0' in i:
                    if info_data_dict['CS_TEC_COEF_DC0'] == 'NA':
                        f_2.write(i.replace('CS_TEC_COEF_DC0=X', '//CS_TEC_COEF_DC0=X'))
                    else:
                        f_2.write(i.replace('CS_TEC_COEF_DC0=X',
                                            'CS_TEC_COEF_DC0=' + info_data_dict['CS_TEC_COEF_DC0']))
                elif 'CS_GCDPARAM_CD1' in i:
                    if info_data_dict['CS_GCDPARAM_CD1'] == 'NA':
                        f_2.write(i.replace('CS_GCDPARAM_CD1=X', '//CS_GCDPARAM_CD1=X'))
                    else:
                        f_2.write(i.replace('CS_GCDPARAM_CD1=X',
                                            'CS_GCDPARAM_CD1=' + info_data_dict['CS_GCDPARAM_CD1']))
                elif 'CS_GCDPARAM_CD2' in i:
                    if info_data_dict['CS_GCDPARAM_CD2'] == 'NA':
                        f_2.write(i.replace('CS_GCDPARAM_CD2=X', '//CS_GCDPARAM_CD2=X'))
                    else:
                        f_2.write(i.replace('CS_GCDPARAM_CD2=X',
                                            'CS_GCDPARAM_CD2=' + info_data_dict['CS_GCDPARAM_CD2']))
                elif 'CS_GCDPARAM_CD3' in i:
                    if info_data_dict['CS_GCDPARAM_CD3'] == 'NA':
                        f_2.write(i.replace('CS_GCDPARAM_CD3=X', '//CS_GCDPARAM_CD3=X'))
                    else:
                        f_2.write(i.replace('CS_GCDPARAM_CD3=X',
                                            'CS_GCDPARAM_CD3=' + info_data_dict['CS_GCDPARAM_CD3']))
                elif 'CS_GCDPARAM_BASEDOSE1' in i:
                    if info_data_dict['CS_GCDPARAM_BASEDOSE1'] == 'NA':
                        f_2.write(i.replace('CS_GCDPARAM_BASEDOSE1=X', '//CS_GCDPARAM_BASEDOSE1=X'))
                    else:
                        f_2.write(i.replace('CS_GCDPARAM_BASEDOSE1=X',
                                            'CS_GCDPARAM_BASEDOSE1=' + info_data_dict['CS_GCDPARAM_BASEDOSE1']))
                elif 'CS_GCDPARAM_BASEDOSE2' in i:
                    if info_data_dict['CS_GCDPARAM_BASEDOSE2'] == 'NA':
                        f_2.write(i.replace('CS_GCDPARAM_BASEDOSE2=X', '//CS_GCDPARAM_BASEDOSE2=X'))
                    else:
                        f_2.write(i.replace('CS_GCDPARAM_BASEDOSE2=X',
                                            'CS_GCDPARAM_BASEDOSE2=' + info_data_dict['CS_GCDPARAM_BASEDOSE2']))
                elif 'CS_GCDPARAM_BASEDOSE3' in i:
                    if info_data_dict['CS_GCDPARAM_BASEDOSE3'] == 'NA':
                        f_2.write(i.replace('CS_GCDPARAM_BASEDOSE3=X', '//CS_GCDPARAM_BASEDOSE3=X'))
                    else:
                        f_2.write(i.replace('CS_GCDPARAM_BASEDOSE3=X',
                                            'CS_GCDPARAM_BASEDOSE3=' + info_data_dict['CS_GCDPARAM_BASEDOSE3']))
                elif 'CS_GCDPARAM_ETA1' in i:
                    if info_data_dict['CS_GCDPARAM_ETA1'] == 'NA':
                        f_2.write(i.replace('CS_GCDPARAM_ETA1=X', '//CS_GCDPARAM_ETA1=X'))
                    else:
                        f_2.write(i.replace('CS_GCDPARAM_ETA1=X',
                                            'CS_GCDPARAM_ETA1=' + info_data_dict['CS_GCDPARAM_ETA1']))
                elif 'CS_GCDPARAM_ETA2' in i:
                    if info_data_dict['CS_GCDPARAM_ETA2'] == 'NA':
                        f_2.write(i.replace('CS_GCDPARAM_ETA2=X', '//CS_GCDPARAM_ETA2=X'))
                    else:
                        f_2.write(i.replace('CS_GCDPARAM_ETA2=X',
                                            'CS_GCDPARAM_ETA2=' + info_data_dict['CS_GCDPARAM_ETA2']))
                elif 'CS_GCDPARAM_ETA3' in i:
                    if info_data_dict['CS_GCDPARAM_ETA3'] == 'NA':
                        f_2.write(i.replace('CS_GCDPARAM_ETA3=X', '//CS_GCDPARAM_ETA3=X'))
                    else:
                        f_2.write(i.replace('CS_GCDPARAM_ETA3=X',
                                            'CS_GCDPARAM_ETA3=' + info_data_dict['CS_GCDPARAM_ETA3']))
                elif 'CS_POSITIONAL_CD_MAP' in i:
                    if param_dict['tool'] == 'MS03' or group_dict['cd_map_id'] == 0:
                        f_2.write("//" + i)
                    else:
                        f_2.write(i.replace('CS_POSITIONAL_CD_MAP="X"',
                                            'CS_POSITIONAL_CD_MAP="' +
                                            group_dict['cd_map_dat_name'].replace(".dat", "") + '"'))

                        cd_map_data = cd_map.objects.get(id=group_dict['cd_map_id'])
                        cd_map_path = cd_map_data.path + cd_map_data.cd_map_dat_name
                        index_path = cd_map_data.path + cd_map_data.index_prm_name

                        new_cd_map_path = path_dict['layout_path'] + group_dict['cd_map_dat_name']
                        shutil.copyfile(cd_map_path, new_cd_map_path)
                        new_index_path = path_dict['layout_path'] + "__index.prm"
                        shutil.copyfile(index_path, new_index_path)
                elif 'CEC=' in i:
                    if param_dict['tool'] == 'MS03' or group_dict['cec_id'] == 0:
                        f_2.write(i.replace('CEC="X"', '//CEC="X"'))
                    else:
                        cec_data_list = cec.objects.get(id=group_dict['cec_id'])
                        cec_path = cec_data_list.cec_path + cec_data_list.cec_name
                        cec_file = open(cec_path, "r")
                        cec_data = cec_file.readlines()
                        cec_data[-1] = cec_data[-1] + '\n'
                        f_2.writelines(cec_data)
                else:
                    f_2.write(i)
            f_2.close()

            return {"result": True, "data": "success"}
        except Exception as e:
            print("create_mds_file error\n", str(e))
            return {"result": False, "data": str(e)}

    def change_layout_ini_layout_name(self, param_dict, path_dict):
        try:
            f_layout_ini_data_1 = open(path_dict['layout_ini_hide_path'], "r", encoding="utf-8")
            layout_ini_data = f_layout_ini_data_1.readlines()
            f_layout_ini_data_1.close()

            f_layout_ini = open(path_dict['layout_ini_path'], "w+", encoding="utf-8")
            for ini_data in layout_ini_data:
                if 'layout_name' in ini_data:
                    layout_name_val = 'layout_name = "' + param_dict['mask_name'] + \
                                      '-' + param_dict['mes_lot_family_id'] + '";\n'
                    f_layout_ini.write(layout_name_val)
                else:
                    f_layout_ini.write(ini_data)
            f_layout_ini.close()

            return {"result": True, "data": "success"}
        except Exception as e:
            print("change_layout_ini_layout_name error\n", str(e))
            return {"result": False, "data": str(e)}

    def move_to_ftp_server(self, path_dict, group_dict):
        try:
            source_path = path_dict['source_path']
            ftp_server_mds_path = path_dict['ftp_server_mds_path']
            layout_ini_path = path_dict['layout_ini_path']
            layout_ini_server_path = path_dict['layout_ini_server_path']
            layout_cdmap_dat_path = path_dict['layout_cdmap_dat_path']
            layout_cdmap_index_path = path_dict['layout_cdmap_index_path']
            ftp_server_cdmap_dat_path = path_dict['ftp_server_cdmap_dat_path']
            ftp_server_cdmap_index_path = path_dict['ftp_server_cdmap_index_path']

            ftp = ftplib.FTP
            host = self.catalog_ftp_host
            ftp_port = self.catalog_ftp_port
            username = self.catalog_ftp_account
            password = self.catalog_ftp_password

            f = ftp()
            f.encoding = "utf-8"
            f.connect(host, ftp_port)
            f.login(username, password)
            f.set_pasv(0)
            bufsize = 1024

            # mds
            fp = open(source_path, 'rb')
            f.storbinary('STOR ' + ftp_server_mds_path, fp, bufsize)  # 上传文件
            fp.close()

            # layout_ini
            fp_2 = open(layout_ini_path, 'rb')
            f.storbinary('STOR ' + layout_ini_server_path, fp_2, bufsize)  # 上传文件
            fp_2.close()

            # cd_map dat & index
            if group_dict['cd_map_id'] != 0:
                fp_3 = open(layout_cdmap_dat_path, 'rb')
                f.storbinary('STOR ' + ftp_server_cdmap_dat_path, fp_3, bufsize)  # 上传文件
                fp_3.close()

                fp_4 = open(layout_cdmap_index_path, 'rb')
                f.storbinary('STOR ' + ftp_server_cdmap_index_path, fp_4, bufsize)  # 上传文件
                fp_4.close()

            f.set_debuglevel(0)
            f.quit
            return {"result": True, "data": "success"}
        except Exception as e:
            traceback.print_exc()
            print("move_to_ftp_server failed\n", str(e))
            return {"result": False, "data": "move_to_ftp_server failed\n" + str(e)}

    def move_to_machine(self, path_dict, group_dict):
        try:
            source_path = path_dict['source_path']
            layout_ini_path = path_dict['layout_ini_path']
            layout_cdmap_dat_path = path_dict['layout_cdmap_dat_path']
            layout_cdmap_index_path = path_dict['layout_cdmap_index_path']

            machine_ip = path_dict['machine_ip']
            machine_host = path_dict['machine_host']
            machine_account = path_dict['machine_account']
            machine_password = path_dict['machine_password']

            machine_ini_path = path_dict['machine_ini_path']
            machine_mds_path = path_dict['machine_mds_path']
            machine_cdmap_dat_path = path_dict['machine_cdmap_dat_path']
            machine_cdmap_index_path = path_dict['machine_cdmap_index_path']

            print(1)
            # ftp = ftplib.FTP
            host = machine_ip
            # ftp_port = machine_host
            username = machine_account
            password = machine_password

            print(2)
            f_2 = SSHManager(host, username, password)
            # f_2.encoding = "utf-8"
            # f_2.connect(host, ftp_port)
            # f_2.login(username, password)
            # f_2.set_pasv(0)
            # bufsize = 1024

            print(3)
            # mds
            print('mds path =' + machine_mds_path)
            # fp = open(source_path, 'rb')
            # f_2.storbinary('STOR ' + machine_mds_path, fp, bufsize)  # 上传文件
            # fp.close()
            f_2._upload_file(source_path, machine_mds_path)

            print(4)
            # layout_ini
            # fp_2 = open(layout_ini_path, 'rb')
            # f_2.storbinary('STOR ' + machine_ini_path, fp_2, bufsize)  # 上传文件
            # fp_2.close()
            f_2._upload_file(layout_ini_path, machine_ini_path)

            print(5)
            # cd_map dat & index
            if group_dict['cd_map_id'] != 0:
                # fp_3 = open(layout_cdmap_dat_path, 'rb')
                # f_2.storbinary('STOR ' + machine_cdmap_dat_path, fp_3, bufsize)  # 上传文件
                # fp_3.close()
                f_2._upload_file(layout_cdmap_dat_path, machine_cdmap_dat_path)

                # fp_4 = open(layout_cdmap_index_path, 'rb')
                # f_2.storbinary('STOR ' + machine_cdmap_index_path, fp_4, bufsize)  # 上传文件
                # fp_4.close()
                f_2._upload_file(layout_cdmap_index_path, machine_cdmap_index_path)

            print(6)
            f_2.__del__()
            return {"result": True, "data": "success"}
        except Exception as e:
            print("move_to_machine failed\n", str(e))
            traceback.print_exc()
            return {"result": False, "data": "move_to_machine failed\n" + str(e)}

    def esp_data_regist(self):
        try:
            _lot_info = lot_info.objects.get(id=self.lot_info_id)
            exp_tool = _lot_info.exp_tool
            tool = _lot_info.info_tree_tool_id

            _tool_maintain = tool_maintain.objects.get(exptool=exp_tool)
            tool_maintain_path = _tool_maintain.path
            catalog_machine_path = tool_maintain_path + '/'
            # catalog_machine_path = os.path.join(tool_maintain_path, Constant.CATALOG_MACHINE_DICT[tool]) + '/'
            print(tool_maintain_path, catalog_machine_path)

            machine_server_path = os.path.join(tool_maintain_path, _lot_info.mask_name)
            print("machine_server_path =", machine_server_path)

            host = _tool_maintain.ip
            username = _tool_maintain.account
            password = _tool_maintain.password

            _o_2 = SSHManager(host, username, password)

            # 　注册指令
            chk_path = os.path.join(machine_server_path, "chk.txt")
            cmd_data = "Esp_DataRegist -ln " + \
                       _lot_info.mask_name + "-" + _lot_info.mes_lot_family_id + " > " + chk_path
            # cd_path = '/QYIC/' + Constant.CATALOG_MACHINE_DICT[tool] + '/' + _lot_info.mask_name
            cd_path = tool_maintain_path + _lot_info.mask_name
            print(cmd_data)
            print(cd_path)
            _o_2.ssh_exec_cmd(cmd_data, path=cd_path)
            _o_2.__del__()

            return {"result": True, "data": "success"}
        except Exception as e:
            print("esp_data_regist failed\n", str(e))
            return {"result": False, "data": "esp_data_regist failed\n" + str(e)}


class catalog_error_list(BaseView):
    def get(self, request):
        lot_info_id = request.GET.get('lot_info_id')
        _o = lot_info.objects.get(id=lot_info_id)
        return render(request, 'catalog/catalog_error_list.html', {'lot_info': _o})


class catalot_op_operation(BaseView):

    def get(self, request):
        lot_info_id = request.GET.get('lot_info_id')
        operation = request.GET.get('operation')
        return render(request, 'catalog/input_mes_user.html', {'lot_info_id': lot_info_id, 'operation': operation})

    def post(self, request):
        lot_info_id = request.POST.get('lot_info_id')
        operation = request.POST.get('operation')
        mes_user = request.POST.get('mes_user')
        mes_pwd = request.POST.get('mes_pwd')
        mm_user = {'userID': mes_user, 'password': mes_sign_password(mes_pwd)}
        if operation == 'start':
            data = self.catalog_op_start(mm_user, lot_info_id)
        elif operation == 'comp':
            data = self.catalog_op_comp(mm_user, lot_info_id)
        else:
            data = self.catalog_op_cancel(mm_user, lot_info_id)
        if data['success']:
            return JsonResponse(data, safe=False)
        else:
            return JsonResponse(data, safe=False)

    def catalog_op_start(self, mm_user, lot_info_id):
        try:
            _o = lot_info.objects.get(id=lot_info_id)
            print(_o.lot_id, _o.mes_operation_id)
            op_start_200_200_result = mes_real_op_start(mm_user, _o.lot_id, _o.mes_operation_id)
            print("op_start_200_200_result =", op_start_200_200_result)
            get_wip_for_task()

            if op_start_200_200_result[0]:
                _o.writer_op_status = 1
                _o.writer_op_error_message = ''
            else:
                _o.writer_op_error_message = op_start_200_200_result[1]
            _o.save()

            data = {'success': True, 'message': "Success"}
            return data
        except Exception as e:
            print(e)
            data = {'success': False, 'message': str(e)}
            return data

    def catalog_op_cancel(self, mm_user, lot_info_id):
        try:
            _o = lot_info.objects.get(id=lot_info_id)

            mes_op_start_cancel_200_200_result = mes_real_op_start_cancel(mm_user, _o.lot_id, _o.mes_operation_id)
            print("mes_op_start_cancel_200_200_result =", mes_op_start_cancel_200_200_result)
            get_wip_for_task()

            if mes_op_start_cancel_200_200_result[0]:
                _o.writer_op_status = 0
                _o.writer_op_error_message = ''
            else:
                _o.writer_op_error_message = mes_op_start_cancel_200_200_result[1]
            _o.save()

            data = {'success': True, 'message': "Success"}
            return data
        except Exception as e:
            print(e)
            data = {'success': False, 'message': str(e)}
            return data

    def catalog_op_comp(self, mm_user, lot_info_id):
        try:
            _o = lot_info.objects.get(id=lot_info_id)

            mes_op_comp_200_200_result = mes_real_op_comp(mm_user, _o.lot_id, _o.mes_operation_id)
            print("mes_op_comp_200_200_result =", mes_op_comp_200_200_result)
            get_wip_for_task()

            if mes_op_comp_200_200_result[0]:
                _o.writer_op_status = 3
                _o.writer_op_error_message = ''
            else:
                _o.writer_op_error_message = mes_op_comp_200_200_result[1]
            _o.save()

            data = {'success': True, 'message': "Success"}
            return data
        except Exception as e:
            print(e)
            data = {'success': False, 'message': str(e)}
            return data


@csrf_exempt
@transaction.atomic()
def catalog_move_back(request):
    try:
        lot_info_id = request.POST.get('lot_info_id')

        _lot_info = lot_info.objects.get(id=lot_info_id)

        exp_tool = _lot_info.exp_tool
        tool = _lot_info.info_tree_tool_id

        _tool_maintain = tool_maintain.objects.get(exptool=exp_tool)
        tool_maintain_path = _tool_maintain.path
        # catalog_machine_path = tool_maintain_path + '/'
        # catalog_machine_path = os.path.join(tool_maintain_path, Constant.CATALOG_MACHINE_DICT[tool]) + '/'
        # print(tool_maintain_path, catalog_machine_path)

        machine_server_path = os.path.join(tool_maintain_path, _lot_info.mask_name)
        print("machine_server_path =", machine_server_path)
        chk_path = os.path.join(machine_server_path, "chk.txt")
        del_path = os.path.join(machine_server_path, "reg_del.txt")
        print(chk_path, del_path)
        host = _tool_maintain.ip
        username = _tool_maintain.account
        password = _tool_maintain.password

        _o = SSHManager(host, username, password)
        if _o.ssh_exec_cmd("find " + tool_maintain_path + " -name chk.txt"):
            cat_file = _o.ssh_exec_cmd("cat " + chk_path)
            result = cat_file.split("\n")
            print('result=' + result[0])
            if "DataID" not in result[0]:
                _lot_info.catalog_status = 0
                _lot_info.catalog_error_message = ''
                _o.ssh_exec_cmd("rm " + chk_path)
                _o.ssh_exec_cmd("rm " + del_path)
                data = {'success': True, 'message': 'Success'}
            else:
                cmd_data = "Esp_DataDelete -ln " + \
                           _lot_info.mask_name + "-" + _lot_info.mes_lot_family_id + " -yes > " + del_path
                log.info(cmd_data)
                _o.ssh_exec_cmd(cmd_data)

                if _o.ssh_exec_cmd("find " + tool_maintain_path + " -name reg_del.txt"):
                    cat_file = _o.ssh_exec_cmd("cat " + del_path)
                    result = cat_file.split("\n")
                    if "Error Detail" in result[0]:
                        print("  ", _lot_info.mask_name, "Reg_del fail", cat_file)
                        data = {'success': False, 'message': 'move back failed\n' + str(cat_file)}
                    else:
                        print("  ", _lot_info.mask_name, "Reg_del success")
                        _lot_info.catalog_status = 0
                        _lot_info.catalog_error_message = ''
                        _o.ssh_exec_cmd("rm " + chk_path)
                        _o.ssh_exec_cmd("rm " + del_path)
                        data = {'success': True, 'message': 'Success'}
                else:
                    print("  ", _lot_info.mask_name, "Not found reg_del.txt")
                    data = {'success': False, 'message': 'move back failed, Not found reg_del.txt'}
        else:
            _lot_info.catalog_status = 0
            _lot_info.catalog_error_message = ''
            data = {'success': True, 'message': 'success'}
        _o.__del__()
        _lot_info.save()

        return JsonResponse(data, safe=False)
    except Exception as e:
        print(e)
        data = {'success': False, 'message': str(e)}
        return JsonResponse(data, safe=False)


@csrf_exempt
@transaction.atomic()
def catalog_change(request):
    try:
        lot_info_id = request.POST.get('lot_info_id')

        _o = lot_info.objects.get(id=lot_info_id)

        result = mes_op_locate(_o.lot_id, "MCDFTP.1", "100.700", "writer move back")
        get_wip_for_task()
        if result[0]:

            query_set = convert_status.objects.filter(tip_no=_o.tip_no, stage='Writer')
            for query in query_set:
                query.status = 1
                query.progress = '0.00%'
                query.err_message = ''
                query.save()
            mask_name = _o.mask_name
            catalog_local_path = os.path.join(Constant.CATALOG_LOCAL_PATH, mask_name)
            if os.path.exists(catalog_local_path):
                shutil.rmtree(catalog_local_path)
            _o.writer_create_file_status = 0
            _o.writer_create_file_error_message = ''
            _o.ftp_upload_status = 0
            _o.ftp_upload_error_message = ''
            _o.catalog_status = 0
            _o.catalog_error_message = ''
            _o.register_status = 0
            _o.register_error_message = ''
            _o.register_del_status = 0
            _o.register_del_error_message = ''
            _o.move_back_status = 0
            _o.move_back_error_message = ''
            _o.writer_op_status = 0
            _o.writer_op_error_message = ''
            _o.save()

            data = {'success': True, 'message': 'Success'}
        else:
            data = {'success': False, 'message': 'Change failed\n' + str(result[1])}
            _o.change_error_message = str(result[1])
            _o.save()
        return JsonResponse(data, safe=False)
    except Exception as e:
        print(e)
        data = {'success': False, 'message': str(e)}
        return JsonResponse(data, safe=False)


class regist_check_job:

    @transaction.atomic()
    def regist_check(self):
        print("regist_check =====================")
        _o = lot_info.objects.filter(catalog_status=3)
        print("Reg Checking Count =", _o.count())
        for lot in _o:
            exp_tool = lot.exp_tool
            tool = lot.info_tree_tool_id

            _tool_maintain = tool_maintain.objects.get(exptool=exp_tool)
            tool_maintain_path = _tool_maintain.path
            catalog_machine_path = tool_maintain_path + '/'
            # catalog_machine_path = os.path.join(tool_maintain_path, Constant.CATALOG_MACHINE_DICT[tool]) + '/'
            print(tool_maintain_path, catalog_machine_path)

            machine_server_path = os.path.join(tool_maintain_path, lot.mask_name)
            print("machine_server_path =", machine_server_path)

            host = _tool_maintain.ip
            username = _tool_maintain.account
            password = _tool_maintain.password

            _o_2 = SSHManager(host, username, password)

            # 　注册指令
            chk_path = os.path.join(machine_server_path, "chk.txt")
            print('chk_path = ' + chk_path)
            print('machine_server_path = ' + machine_server_path)
            if _o_2.ssh_exec_cmd("find " + machine_server_path + " -name chk.txt"):
                cat_file = _o_2.ssh_exec_cmd("cat " + chk_path)
                result = cat_file.split("\n")
                _li = lot_info.objects.get(id=lot.id)
                if "DataID" in result[0]:
                    print("  ", lot.mask_name, "True", result[0])
                    _li.catalog_status = 5
                else:
                    print("  ", lot.mask_name, "False")
                    _li.catalog_status = 4

                _li.catalog_error_message = cat_file
                _li.save()
            else:
                print("  ", lot.mask_name, "Not found")

            _o_2.__del__()

        print("regist_check =====================")
