import os
import traceback

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from Mask_DP.settings import MES_USER
from catalog.models import group_maintain, tool_maintain, tool_name_route
from jdv.models import lot_info
from making.models import convert_status
from tooling_form.models import device_info, layout_info
from tooling_form.service.tooling_contrast_sync_service import move_back_lotID
from utilslibrary.base.base import BaseView
from utilslibrary.mes_webservice.mes_base_webservice import MES_TxEqpInfoInq
from django.db.models import Q

from utilslibrary.mes_webservice.mes_demo.MES_LotInfoInq import lotinfo_inquery
from utilslibrary.mes_webservice.mes_utils import mes_sign_password
from utilslibrary.mes_webservice.mes_webservice import update_exptool, mes_op_locate
from utilslibrary.system_constant import Constant
from utilslibrary.utils.ssh_utils import SSHManager

# ppt_user = {'userID': 'DP_Test', 'password': 'utfU`QE'}


# 正式环境
# ppt_user = {'userID': 'DP_SYS', 'password': 'es1xttAQ'}

class ToolStatus(BaseView):
    def get(self, request):
        return render(request, 'catalog/tool_status_list.html')

    def post(self, request):
        super().post(request)
        query_set = tool_maintain.objects.filter(is_delete=0).order_by('exptool')
        status_list = []
        bks_dict = {}
        ftp_dict = {}
        dis_dict = {}
        run_dict = {}
        wait_dict = {}
        for query in query_set:
            status_dict = {}
            lot_query_set = lot_info.objects.filter(exp_tool=query.exptool, is_delete=0)
            bks_dict[query.tool_id] = 0
            ftp_dict[query.tool_id] = 0
            dis_dict[query.tool_id] = 0
            wait_dict[query.tool_id] = 0
            run_dict[query.tool_id] = 0
            for lot_query in lot_query_set:
                print(lot_query.mask_name)
                if lot_query.mes_operation_id:
                    if "BKP" in lot_query.mes_operation_id:
                        bks_dict[query.tool_id] += 1
                    elif 'FTP' in lot_query.mes_operation_id:
                        ftp_dict[query.tool_id] += 1
                    elif 'DIS' in lot_query.mes_operation_id:
                        dis_dict[query.tool_id] += 1
                if lot_query.mes_lot_status:
                    if lot_query.mes_operation_id[3:5] in ['EB', 'LB'] and lot_query.mes_lot_status == 'Waiting':
                        wait_dict[query.tool_id] += 1
                    elif lot_query.mes_operation_id[3:5] in ['EB', 'LB'] and lot_query.mes_lot_status in ['Running',
                                                                                                          'Processing']:
                        run_dict[query.tool_id] += 1
            status_dict['tool_id'] = query.tool_id
            status_dict['bkp_num'] = bks_dict.setdefault(query.tool_id, 0)
            status_dict['ftp_num'] = ftp_dict.setdefault(query.tool_id, 0)
            status_dict['dis_num'] = dis_dict.setdefault(query.tool_id, 0)
            status_dict['run_num'] = run_dict.setdefault(query.tool_id, 0)
            status_dict['wait_num'] = wait_dict.setdefault(query.tool_id, 0)
            status_dict['tool_status'] = MES_TxEqpInfoInq(MES_USER, query.tool_id)
            status_list.append(status_dict)
        status_list = status_list[self.startIndex: self.endIndex]
        data = {'total': len(status_list), 'rows': status_list}
        return JsonResponse(data, safe=False)


class ToolRouteDetail(BaseView):
    def get(self, request):
        tool_id = request.GET.get('tool_id')
        type = request.GET.get('type')
        can_change = request.GET.get('can_change')
        return render(request, 'catalog/tool_status_detail.html',
                      {'tool_id': tool_id, 'type': type, 'can_change': can_change})

    def post(self, request):
        super().post(request)
        tool_id = request.POST.get('tool_id')
        type = request.POST.get('type')
        query_list = []
        writer_name = tool_name_route.objects.filter(catalog_tool_id=tool_id).first().writer_name
        if 'operation' in type:
            query_set = lot_info.objects.filter(exp_tool=writer_name,
                                                mes_operation_id__contains=type.split('_')[0].upper(),
                                                is_delete=0)
        if 'status' in type:
            query_set = lot_info.objects.filter(
                Q(Q(mes_operation_id__contains='EB') | Q(mes_operation_id__contains='LB')) & ~Q(
                    mes_operation_id__contains='PE'),
                exp_tool=writer_name,
                is_delete=0)
        for query in query_set.values():
            device_set = device_info.objects.filter(tip_no=query['tip_no'], mask_name=query['mask_name'], is_delete=0)
            if device_set.count() > 1:
                query['insp'] = 'DB'
            else:
                for device in device_set:
                    f_l_set = layout_info.objects.filter(tip_no=query['tip_no'], mask_name=query['mask_name'],
                                                         device_name=device.device_name,
                                                         is_delete=0)
                    if f_l_set.count() > 1:
                        query['insp'] = 'DB'
                    elif f_l_set.count() == 1:
                        query['insp'] = 'DD'
            lot_id = query['lot_id']
            clip, priority = lotinfo_inquery(lot_id, MES_USER)
            query['clip'] = clip
            query['priority'] = priority
            query['exptool'] = query["exp_tool"]
            query_list.append(query)
        rows = query_list[self.startIndex: self.endIndex]
        data = {'total': len(query_list), 'rows': rows}
        return JsonResponse(data, safe=False)


@csrf_exempt
def gen_exptool(request):
    exp_tool = request.POST.get('exp_tool')
    group = tool_maintain.objects.filter(exptool=exp_tool, is_delete=0)
    if group:
        group_name = group.first().group_name
    else:
        return JsonResponse({'success': False, 'exptool_list': ['No exptool matched']}, safe=False)
    query_set = tool_maintain.objects.filter(group_name=group_name, is_delete=0)
    exptool_list = []
    for query in query_set:
        if query.exptool not in exptool_list:
            exptool_list.append(query.exptool)
    return JsonResponse({'success': True, 'exptool_list': exptool_list}, safe=False)


class ChangeExptool(BaseView):
    def get(self, request):
        id = request.GET.get('id')
        default_exptool = lot_info.objects.get(pk=id).exp_tool
        return render(request, 'catalog/change_exptool.html', {'id': id, 'default_exptool': default_exptool})

    def post(self, request):
        id = request.POST.get('id')
        exp_tool = request.POST.get('exp_tool')
        mes_user = request.POST.get('mes_user')
        mes_pwd = request.POST.get('mes_pwd')
        infotree_tool = tool_name_route.objects.get(writer_name=exp_tool).info_tree_name
        mm_user = {'userID': mes_user, 'password': mes_sign_password(mes_pwd)}
        query = lot_info.objects.get(pk=id)
        lot_id = query.lot_id
        PDID = query.mes_operation_id
        lot_status = query.mes_lot_status
        if 'FTP' in PDID or lot_status != 'Waiting':
            return JsonResponse({'success': False, 'msg': 'lot status is not waiting or stage is on FTP'}, safe=False)
        else:
            if 'BKP' in PDID:
                with transaction.atomic():
                    query.writer_create_file_status = 0
                    query.ftp_upload_status = 0
                    query.catalog_status = 0
                    query.register_status = 0
                    query.register_del_status = 0
                    query.change_status = 0
                    query.writer_op_status = 0
                    query.move_back_status = 0
                    query.info_tree_tool_id = infotree_tool
                    # data = move_back_lotID(id)
                    # if data['success']:
                    if not update_exptool(mm_user, query.tip_no, query.mask_name, query.lot_id, exp_tool):
                        return JsonResponse({"success": False, 'msg': 'mes exptool change failed'}, safe=False)
                    else:
                        flag, message = mes_op_locate(query.lot_id, 'MCDFTP.1', '100.700',
                                                      'tool status change exptool, pull the site back')
                        if flag:
                            query_set = convert_status.objects.filter(lot_id=lot_id, stage_id=5)
                            for c_s in query_set:

                                c_s.status = 1
                                c_s.progress = '0.00%'
                                c_s.save()
                            query.exp_tool = exp_tool
                            query.save()
                            return JsonResponse({"success": True, 'msg': 'change success'}, safe=False)
                        else:
                            return JsonResponse({"success": False, 'msg': 'pull site back error'}, safe=False)
                    # else:
                    #     return JsonResponse({"success": False, 'msg': 'change failed'}, safe=False)
            else:
                if not update_exptool(mm_user, query.tip_no, query.mask_name, query.lot_id, exp_tool):
                    return JsonResponse({"success": False, 'msg': 'mes exptool change failed'}, safe=False)
                query.exp_tool = exp_tool
                query.save()
                return JsonResponse({"success": True, 'msg': 'change success'}, safe=False)


class upload_progress(BaseView):
    def get(self, request):
        id = request.GET.get('id')
        lot_info_query = lot_info.objects.get(id=id)
        mask_name = lot_info_query.mask_name
        machine_id = lot_info_query.machine_id
        machine_query = tool_maintain.objects.get(id=machine_id)
        catalog_local_path = Constant.CATALOG_LOCAL_PATH
        catalog_local_path = os.path.join(catalog_local_path, mask_name)
        all_num = len(os.listdir(catalog_local_path))
        print('all_num = ' + str(all_num))
        catalog_ftp_server_path = Constant.CATALOG_FTP_SERVER_PATH
        catalog_ftp_server_path = '/DTS/test' + os.path.join(catalog_ftp_server_path,
                                                             Constant.CATALOG_MACHINE_DICT[
                                                                 lot_info_query.info_tree_tool_id],
                                                             mask_name)
        host = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_HOST']
        username = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_ACCOUNT']
        password = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_PASSWORD']
        _ftp = SSHManager(host, username, password)
        cmd = 'll -l | wc -l'
        try:
            ftp_num = _ftp.ssh_exec_cmd(cmd=cmd, path=catalog_ftp_server_path)
            print('ftp_num = ' + ftp_num)
            print('catalog_ftp_server_path = ' + catalog_ftp_server_path)
            ftp_progress = round(int(ftp_num) / all_num) * 100
        except:
            traceback.print_exc()
            ftp_progress = '0'
        writer_path = os.path.join('/san/stor0/usr/ebm9500', machine_query.path,
                                   Constant.CATALOG_MACHINE_DICT[lot_info_query.info_tree_tool_id], mask_name)
        writer_host = machine_query.ip
        writer_account = machine_query.account
        writer_pwd = machine_query.password
        _writer = SSHManager(writer_host, writer_account, writer_pwd)
        try:
            writer_num = _writer.ssh_exec_cmd(cmd=cmd, path=writer_path)
            print('writer_num = ' + writer_num)
            print('writer_path = ' + writer_path)
            writer_progress = round(int(writer_num) / all_num)
        except:
            traceback.print_exc()
            writer_progress = '0'
        return render(request, 'catalog/upload_progress.html',
                      {"ftp_upload_progress": str(ftp_progress) + '%',
                       'writer_upload_progress': str(writer_progress) + '%'})
