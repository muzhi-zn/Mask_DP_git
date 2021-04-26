# coding=utf-8
import logging
import os
import shutil
import time
import traceback

from django.db import transaction
from django.shortcuts import render
from django.template.context_processors import request
from django.http.response import JsonResponse, FileResponse
from django.db.models.query_utils import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from Mask_DP.settings import MES_USER
from catalog.models import tool_name_route, tool_maintain
from infotree.models import tree, tree_option
from jdv.models import lot_info, email_group, lot_trail
from django.core import serializers
from datetime import datetime

from jdv.service.jdv_service import jdvService
from making.service.convert_status_service import stageService, convertStatusLog
from tooling_form.models import product_info, import_list, tapeout_info, device_info
from tooling_form.service.show_tip_no_service import del_fracture_file
from utilslibrary.base.base import BaseView
from utilslibrary.decorators.catch_exception_decorators import catch_exception
from utilslibrary.decorators.gen_trail_decorators import gen_trail
from utilslibrary.mes_webservice.mes_demo.MES_LotInfoInq import lotinfo_inquery
from utilslibrary.mes_webservice.mes_utils import mes_sign_password
from utilslibrary.mes_webservice.mes_webservice import update_exptool, mes_op_start, mes_op_comp, mes_op_start_cancel, \
    get_wip_for_task, mes_op_process, change_blank_pellicle, insert_blank_pellicle, mes_op_locate
from utilslibrary.system_constant import Constant
from system.models import template
from making.models import convert_status, convert_status_stage, convert_operate_log
from utilslibrary.utils import iems_utils
from utilslibrary.utils.file_utils import get_fracture_log_file_name, get_fracture_xor_log_file_name, \
    get_fracture_file_name
from system.service.dict_service import GetValueByType
from utilslibrary.utils.ssh_utils import SSHManager

log = logging.getLogger('log')


class enginnerLotList(BaseView):
    """工程师查看lot"""

    def get(self, request):
        """页面跳转"""
        return render(request, 'jdv_enginner_lot_list.html')

    def post(self, request):
        """页面数据组装"""
        super().post(request)
        q = Q()
        q.connector = 'and'
        q.children.append(('is_delete', 0))
        q.children.append(('mes_operation_number__lt', '300.100'))
        product_name = request.POST.get('product_name')  # 产品名
        if product_name:
            q.children.append(('product_name', product_name))
        tip_no = request.POST.get('tip_no')
        if tip_no:
            q.children.append(('tip_no', tip_no))
        lot_id = request.POST.get('lot_id')
        if lot_id:
            q.children.append(('lot_id', lot_id))
        mes_step = request.POST.get('mes_step')
        if mes_step:
            q.children.append(('mes_operation_id', mes_step))
        query_date = request.POST.get('query_date')
        if query_date:
            start_date = datetime.strptime(query_date.split(' - ')[0], '%Y-%m-%d %H:%M:%S')
            end_date = datetime.strptime(query_date.split(' - ')[1], '%Y-%m-%d %H:%M:%S')
            q.children.append(('ready_date__gte', start_date))
            q.children.append(('ready_date__lte', end_date))
        lot_list = lot_info.objects.filter(~Q(mes_lot_status="SCRAPPED") & q).order_by('mes_due_timestamp').values()[self.startIndex: self.endIndex]
        for lot in lot_list:
            ds_stamp_time = lot['mes_due_timestamp'].replace(".", ":", 2).replace("-", ' ').replace(' ', '-', 2)
            t = datetime.strptime(ds_stamp_time, "%Y-%m-%d %H:%M:%S.%f").timetuple()
            ds_timeStamp = int(time.mktime(t))
            now_timeStamp = int(time.time())
            clip = int((ds_timeStamp - now_timeStamp) / 3600)
            lot['clip'] = clip
        data = {}
        data['total'] = lot_info.objects.filter(~Q(mes_lot_status="SCRAPPED") & q).count()
        data['rows'] = list(lot_list)
        return JsonResponse(data, safe=False)


class ExptoolChange(BaseView):
    """修改lot的dispatch信息"""

    def get(self, request):
        id = request.GET.get('id')
        default_exptool = lot_info.objects.get(pk=id).exp_tool
        return render(request, 'exptool_change_form.html', {'id': id, 'default_exptool': default_exptool})

    def post(self, request):
        """修改lot_info的dispatch信息"""
        id = request.POST.get('id')
        machine_id = request.POST.get('machine_id')  # exptool
        exp_tool = request.POST.get('exp_tool')
        dispatch_flag = request.POST.get('dispatch_flag')
        mm_username = request.POST.get("mm_username")
        mm_password = request.POST.get("mm_password")
        mm_user = {'userID': mm_username, 'password': mes_sign_password(mm_password)}
        _machine = tool_name_route.objects.get(writer_name=machine_id, is_delete=0)
        machine = tool_maintain.objects.get(exptool=machine_id).id
        with transaction.atomic():
            s1 = transaction.savepoint()
            _lot_info = lot_info.objects.get(pk=id)
            # ----------------------------------------------------------------------------
            if _lot_info.ftp_upload_status == 1:
                transaction.savepoint_rollback(s1)
                return JsonResponse({'success': False, 'msg': 'file is uploading'})
                # TODO DIS站点之后进行change_exptool操作需要将lot拉回FTP站点
            if _lot_info.mes_operation_number > '100.700':  # 如果文件已经上机台
                # 先取消机台注册
                if _lot_info.register_status == 5:
                    old_exp_tool = _lot_info.exp_tool
                    tool = _lot_info.info_tree_tool_id
                    _tool_maintain = tool_maintain.objects.get(exptool=old_exp_tool)
                    tool_maintain_path = _tool_maintain.path
                    catalog_machine_path = tool_maintain_path + '/'
                    # catalog_machine_path = os.path.join(tool_maintain_path, Constant.CATALOG_MACHINE_DICT[tool]) + '/'
                    print(tool_maintain_path, catalog_machine_path)

                    machine_server_path = os.path.join(tool_maintain_path, _lot_info.mask_name)
                    print("machine_server_path =", machine_server_path)

                    host = _tool_maintain.ip
                    username = _tool_maintain.account
                    password = _tool_maintain.password

                    _o = SSHManager(host, username, password)

                    # 　取消注册指令
                    chk_path = os.path.join(machine_server_path, "chk.txt")
                    del_path = os.path.join(machine_server_path, "reg_del.txt")
                    cmd_data = "Esp_DataDelete -ln " + \
                               _lot_info.mask_name + "-" + _lot_info.mes_lot_family_id + " -yes > " + del_path
                    print(cmd_data)
                    _o.ssh_exec_cmd(cmd_data)
                    if _o.ssh_exec_cmd("find " + machine_server_path + " -name reg_del.txt"):
                        cat_file = _o.ssh_exec_cmd("cat " + del_path)
                        result = cat_file.split("\n")
                        if "Error Detail" in result[0]:
                            print("  ", _lot_info.mask_name, "Reg_del fail", cat_file)
                            transaction.savepoint_rollback(s1)
                            return JsonResponse({'success': False, 'msg': 'Esp_DataDelete Fail: ' + str(cat_file)})
                # 删除机台文件
                if _lot_info.ftp_upload_status == 3:  # 文件上传完成
                    flag, message = del_fracture_file(_lot_info.lot_id, True)
                    if not flag:
                        transaction.savepoint_rollback(s1)
                        return JsonResponse({'success': False, 'msg': 'delete tool flie fail: ' + str(message)})
                # 站点拉回FTP
                flag, message = mes_op_locate(_lot_info.lot_id, 'MCDFTP.1', '100.700', 'exptool change')
                if not flag:
                    transaction.savepoint_rollback(s1)
                    return JsonResponse({'success': False, 'msg': 'Op Locate Fail: ' + str(message)})
                # 删除本地文件
                mask_name = _lot_info.mask_name
                catalog_local_path = os.path.join(Constant.CATALOG_LOCAL_PATH, mask_name)
                if os.path.exists(catalog_local_path):
                    shutil.rmtree(catalog_local_path)
                # 更改状态
                query_set = convert_status.objects.filter(lot_id=lot_info.lot_id, stage='Writer')
                for query in query_set:
                    query.status = 1
                    query.progress = '0.00%'
                    query.err_message = ''
                    query.save()
                _lot_info.writer_create_file_status = 0
                _lot_info.writer_create_file_error_message = ''
                _lot_info.ftp_upload_status = 0
                _lot_info.ftp_upload_error_message = ''
                _lot_info.catalog_status = 0
                _lot_info.catalog_error_message = ''
                _lot_info.register_status = 0
                _lot_info.register_error_message = ''
                _lot_info.register_del_status = 0
                _lot_info.register_del_error_message = ''
                _lot_info.move_back_status = 0
                _lot_info.move_back_error_message = ''
                _lot_info.writer_op_status = 0
                _lot_info.writer_op_error_message = ''
            # -----------------------------------------------------------------------------------------------------
            # if _lot_info.mes_operation_number >= Constant.MES_OPERATION_NUM_DIS:  # dis站点之后就不可以操作
            #     transaction.savepoint_rollback(s1)
            #     return JsonResponse({'success': False, 'msg': _lot_info.lot_id + ' in ' +
            #                                                   _lot_info.mes_operation_id + '站点, 不允许操作'})
            # if _lot_info.release_status != 1:
            #     transaction.savepoint_rollback(s1)
            #     return JsonResponse({'success': False, 'msg': "请先执行JDV Release"})
            # if modify machine_id,reget fracture_file_name
            if _lot_info.machine_id != machine_id:
                device_list = device_info.objects.filter(tip_no=_lot_info.tip_no, mask_name=_lot_info.mask_name,
                                                         is_delete=0)
                _product_info = product_info.objects.get(tip_no=_lot_info.tip_no, is_delete=0)

            for device in device_list:
                file_name = get_fracture_file_name(_product_info.product, _lot_info.mask_name[-5:],
                                                   device.device_name,
                                                   _machine.machine_type)
                convert_status.objects.filter(tip_no=_lot_info.tip_no, mask_name=_lot_info.mask_name,
                                              device_name=device.device_name,
                                              stage=Constant.MAKING_CONVERT_STATUS_STAGE_NAME_FRACTURE) \
                    .update(file_name=file_name)

            _lot_info.machine_id = machine
            _lot_info.exp_tool = exp_tool
            info_tree_tool_id = _machine.info_tree_name
            _lot_info.info_tree_tool_id = info_tree_tool_id
            _lot_info.dispatch_flag = dispatch_flag
            _lot_info.save()
            if not update_exptool(mm_user, _lot_info.tip_no, _lot_info.mask_name, _lot_info.lot_id, _lot_info.exp_tool):
                # transaction.rollback()
                transaction.savepoint_rollback(s1)
                return JsonResponse({'success': False, 'msg': 'Notice MES Error'})
            # if not mes_op_process(_lot_info.lot_id, 'MCDDIS.1'):
            #     transaction.savepoint_rollback(s1)
            #     return JsonResponse({'success': False, 'msg': 'Pass Station Error'})
        return JsonResponse({'success': True, 'msg': 'EXPTOOL Change Success'})


class BlankPellicleChange(BaseView):
    """修改MES的blank或pellicle"""

    def get(self, request):
        id = request.GET.get('id')
        default_blank_code = lot_info.objects.get(pk=id).blank_code
        default_pellicle_code = lot_info.objects.get(pk=id).pellicle_code
        return render(request, 'balnk_pellicle_change_form.html', {'id': id, 'default_blank_code': default_blank_code,
                                                                   'default_pellicle_code': default_pellicle_code})

    def post(self, request):
        b = None
        p = None
        id = request.POST.get('id')
        blank_code = request.POST.get('blank_code')
        pellicle_code = request.POST.get('pellicle_code')
        mm_username = request.POST.get("mm_username")
        mm_password = request.POST.get("mm_password")
        mm_user = {'userID': mm_username, 'password': mes_sign_password(mm_password)}
        if pellicle_code or blank_code:
            with transaction.atomic():
                s1 = transaction.savepoint()
                lot = lot_info.objects.get(pk=id)
                if blank_code:
                    lot.blank_code = blank_code
                    b = blank_code
                if pellicle_code:
                    lot.pellicle_code = pellicle_code
                    p = pellicle_code
                lot.save()
                if not change_blank_pellicle(mm_user, lot.tip_no, lot.mask_name, lot.lot_id, b, p):
                    transaction.savepoint_rollback(s1)
                    return JsonResponse({'success': False, 'msg': 'Notice MES Error'})
                return JsonResponse({'success': True, 'msg': 'Blank&Pellicle Change Success'})

        else:
            return JsonResponse({'success': False, 'msg': 'Nothing Changed'})


class InsertBlankAndPellicle(BaseView):
    """插入blank和pellicle"""

    def get(self, request):
        return render(request, 'balnk_pellicle_insert_form.html')

    def post(self, request):
        b = None
        p = None
        lot_id = request.POST.get('lot_id')
        lot_type = request.POST.get('type')
        mm_username = request.POST.get("mm_username")
        mm_password = request.POST.get("mm_password")
        mm_user = {'userID': mm_username, 'password': mes_sign_password(mm_password)}
        print(lot_type)
        if not lot_id:
            return JsonResponse({'success': False, 'msg': 'lot_id is null'})
        blank_code = request.POST.get('blank_code')
        pellicle_code = request.POST.get('pellicle_code')
        if pellicle_code or blank_code:
            if blank_code:
                b = blank_code
            if pellicle_code:
                p = pellicle_code
            if not insert_blank_pellicle(mm_user, lot_type, lot_id, b, p):
                return JsonResponse({'success': False, 'msg': 'Notice MES Error'})
            return JsonResponse({'success': True, 'msg': 'Blank&Pellicle Change Success'})

        else:
            return JsonResponse({'success': False, 'msg': 'Nothing Changed'})


class PassStation(BaseView):
    """过站操作"""

    def post(self, request):
        """执行过站操作"""
        id = request.POST.get("id")
        lot = lot_info.objects.get(pk=id)
        lot_id = lot.lot_id
        op_id = lot.mes_operation_id
        if mes_op_process(lot_id, op_id):
            get_wip_for_task()  # 执行状态查询
            return JsonResponse({'success': True, 'msg': '过站成功'}, safe=False)
        else:
            return JsonResponse({'success': False, 'msg': '过站失败'}, safe=False)
        # if mes_op_start(lot_id, op_id):
        #     if mes_op_comp(lot_id, op_id):
        #         get_wip_for_task()  # 执行状态查询
        #         return JsonResponse({'success': True, 'msg': '过站成功'}, safe=False)
        #     else:
        #         mes_op_start_cancel(lot_id, op_id)
        #         return JsonResponse({'success': False, 'msg': 'op_comp执行失败，过站失败'}, safe=False)
        # else:
        #     return JsonResponse({'success': False, 'msg': 'op_start执行失败，过站失败'}, safe=False)


@require_POST
def pass_rfl(request):
    """过RFL站点"""
    id = request.POST.get("id")
    lot = lot_info.objects.get(pk=id)
    if lot.mes_operation_id != Constant.MES_OPERATION_ID_RFL:
        return JsonResponse({'success': False, 'msg': 'lot当前站点不为RFL'}, safe=False)
    else:
        if mes_op_start(lot.lot_id, lot.mes_operation_id):
            if mes_op_comp(lot.lot_id, lot.mes_operation_id):
                get_wip_for_task()  # 执行状态查询
                return JsonResponse({'success': True, 'msg': 'RFL过站成功'}, safe=False)
            else:
                mes_op_start_cancel(lot.lot_id, lot.mes_operation_id)
                return JsonResponse({'success': False, 'msg': 'op_comp执行失败，过站失败'}, safe=False)
        else:
            return JsonResponse({'success': False, 'msg': 'op_start执行失败，过站失败'}, safe=False)


class compileLotList(BaseView):
    """编锅页面相关"""

    def get(self, request):
        return render(request, 'jdv_compile_lot_list.html')

    def post(self, request):
        super().post(request)
        cl_list = lot_info.objects.filter(is_delete=0, payment_status=1, release_status=1).values()[
                  self.startIndex: self.endIndex]
        data = {'total': lot_info.objects.filter(is_delete=0, payment_status=1, release_status=1).count(),
                'rows': list(cl_list)}
        return JsonResponse(data, safe=False)


class convertOptions(BaseView):
    """获取device的信息类"""

    @catch_exception
    @csrf_exempt
    def get_mask_name_list(self, request):
        """根据product获取mask_name_list"""
        product = request.POST.get("product")
        _data_list = product_info.objects.filter(product=product, is_delete=0)
        if _data_list.count() > 0:
            tip_no = _data_list.first().tip_no
            if import_list.objects.filter(tip_no=tip_no, is_delete=0).first().status >= 7:
                tapeout_list = tapeout_info.objects.values().filter(tip_no=tip_no, t_o='Y', is_delete=0)
                return JsonResponse({"success": True, "tip_no": tip_no, "mask_list": list(tapeout_list)}, safe=False)
            else:
                return JsonResponse({'success': False, 'message': True})
        else:
            return JsonResponse({"success": False}, safe=False)

    @catch_exception
    @csrf_exempt
    def get_device_by_mask_name(self, request):
        """根据mask_name获取device"""
        data = {}
        tip_no = request.POST.get("tip_no")
        mask_name = request.POST.get("mask_name")
        data['mask_name'] = mask_name
        lot_set = lot_info.objects.filter(mask_name=mask_name, tip_no=tip_no)
        for lot in lot_set:
            if lot.lot_id:
                lot_id = lot.lot_id
                data['lot_id'] = lot_id
                data['success'] = True
        device_list = device_info.objects.values('device_type', 'device_name').filter(tip_no=tip_no,
                                                                                      ).order_by('-device_type')
        data['device_list'] = list(device_list)
        return JsonResponse(data, safe=False)

    @catch_exception
    @csrf_exempt
    def get_device_by_lot_id(self, request):
        """根据lot_id获取相关的device"""
        data = {}
        lot_id = request.POST.get("lot_id")
        lot_list = lot_info.objects.filter(lot_id=lot_id)
        if lot_list.count() > 0:
            lot = lot_list[0]

            data['tip_no'] = lot.tip_no
            data['mask_name'] = lot.mask_name
            lot_id = lot_info.objects.get(mask_name=lot.mask_name).lot_id
            data['lot_id'] = lot_id
            device_list = device_info.objects.values('device_type', 'device_name').filter(tip_no=lot.tip_no,
                                                                                          mask_name=lot.mask_name,
                                                                                          is_delete=0
                                                                                          ).order_by('-device_type')
            data['device_list'] = list(device_list)
            data['success'] = True
            return JsonResponse(data, safe=False)
        else:
            data['success'] = False
            return JsonResponse(data, safe=False)


class convertStatus(BaseView):
    """convert_status相关方法"""

    @catch_exception
    @csrf_exempt
    def get_device_stages(self, request):
        """获取device类型的站点"""
        data = {}
        tip_no = request.POST.get("tip_no")  # tip_no
        mask_name = request.POST.get("mask_name")  # mask_name
        device_name = request.POST.get("device_name")  # device_name
        stage_list = convert_status_stage.objects.values().order_by('order').filter(type=1, device_type="Main")
        for stage in stage_list:
            c_s = convert_status.objects.values().filter(tip_no=tip_no, mask_name=mask_name, device_name=device_name,
                                                         stage_id=stage['id']).first()
            stage['device_info'] = c_s
        data["stage_list"] = list(stage_list)
        return JsonResponse(data, safe=False)

    @catch_exception
    @csrf_exempt
    def get_frame_stages(self, request):
        """获取Frame类型的站点"""
        data = {}
        tip_no = request.POST.get("tip_no")  # tip_no
        mask_name = request.POST.get("mask_name")  # mask_name
        device_name = request.POST.get("device_name")  # device_name
        stage_list = convert_status_stage.objects.values().filter(type=1)
        for stage in stage_list:
            c_s = convert_status.objects.values().filter(tip_no=tip_no, mask_name=mask_name, device_name=device_name,
                                                         stage_id=stage['id']).first()
            stage['device_info'] = c_s
        data["stage_list"] = list(stage_list)
        return JsonResponse(data, safe=False)

    @catch_exception
    def stage_operation_form(self, request):
        """跳转stage的操作表单页面"""
        data = {}
        stage_id = request.GET.get("stage_id")
        device_info_id = request.GET.get("device_info_id")
        stage = convert_status_stage.objects.values().get(pk=stage_id)
        data['stage'] = stage
        device = convert_status.objects.values().get(pk=device_info_id)
        data['device'] = device
        pre_device = convert_status.objects.filter(tip_no=device['tip_no'], mask_name=device['mask_name'],
                                                   lot_id=device['lot_id'], device_name=device['device_name'],
                                                   stage=stage['pre_stage']).first()
        if pre_device:
            pre_stage_file = str(pre_device.location) + str(pre_device.file_name)
            data['pre_stage_file'] = pre_stage_file
        pre_stage = convert_status_stage.objects.values().filter(stage_name=stage['pre_stage']).first()
        if pre_stage:
            data['pre_stage'] = pre_stage
        operations = stage['operation'].split(',')
        data['operations'] = operations
        logs = convert_operate_log.objects.values('operation_user_name', 'operation', 'operation_time'). \
            order_by('-operation_time').filter(convert_status_id=device['id'])
        data['logs'] = list(logs)
        if convert_operate_log.objects.filter(convert_status_id=device['id']).order_by('-operation_time'). \
                first():
            data['operator'] = convert_operate_log.objects.filter(convert_status_id=device['id']).order_by(
                '-operation_time'). \
                first().operation_user_name
        # package log_file_name
        _fracture_log_file = get_fracture_log_file_name(device['mask_name'][0:6], device['mask_name'][-5:],
                                                        device['device_name'])
        data['fracture_log_file'] = _fracture_log_file
        _fracture_xor_log_file = get_fracture_xor_log_file_name(device['mask_name'][0:6], device['mask_name'][-5:],
                                                                device['device_name'])
        data['fracture_xor_log_file'] = _fracture_xor_log_file

        # query IEMS_SERVER_EXECUTE_CMD_URL from dictionary
        data[Constant.IEMS_SERVER_EXECUTE_CMD_URL] = GetValueByType().getValueByLabel(
            Constant.IEMS_SERVER_EXECUTE_CMD_URL)
        data[Constant.IEMS_FRACTURE_TEMPLATE_ID] = GetValueByType().getValueByLabel(Constant.IEMS_FRACTURE_TEMPLATE_ID)
        data[Constant.IEMS_FRACTURE_XOR_TEMPLATE_ID] = GetValueByType().getValueByLabel(
            Constant.IEMS_FRACTURE_XOR_TEMPLATE_ID)
        data[Constant.FRACTURE_CALLBACK_URL] = GetValueByType().getValueByLabel(Constant.FRACTURE_CALLBACK_URL)
        if stage['flow'] == 'PD' and stage['stage_name'] != 'Writer':
            _flow = 'Fracture'
        elif stage['flow'] == 'QA':
            _flow = 'XOR'
        else:
            _flow = stage['stage_name']

        # ftp_upload_error_message
        if stage['stage_name'] == 'Writer':
            data['ftp_upload_error_message'] = lot_info.objects.get(lot_id=device['lot_id']).ftp_upload_error_message
            print(data['ftp_upload_error_message'])
            
        # return render(request, "making_" + stage['stage_name'] + "_operation_form.html", data)
        return render(request, "making_" + _flow + "_operation_form.html", data)

    def convert_status_operate(self, request):
        """rework操作"""
        id = request.POST.get("convert_status_id")
        stage_name = request.POST.get("stage_name")
        rework = request.POST.get("rework")
        operation = request.POST.get("operation")
        if operation:
            cs = convert_status.objects.get(id=id)
            if int(
                    operation) == Constant.CONVERT_OPERATION_SKIP and cs.status == Constant.CONVERT_STATUS_ON_GOING:  # skip状态
                record_no = cs.record_no
                if record_no:
                    result = iems_utils.kill_lsf_job(record_no)  # 执行bkill job的操作
            cs.operation_status = operation
            cs.save()
            convertStatusLog().add_operation_log(id, int(operation), request.session[Constant.SESSION_CURRENT_USER_ID],
                                                 request.session[Constant.SESSION_CURRENT_USER_LOGINNAME],
                                                 '', '', '', '', '', '', '', '', datetime.now())
        if rework:
            if int(rework) == 1:
                stageService().rework_mode1(id, stage_name)
            elif int(rework) == 2:
                stageService().rework_mode2(id, stage_name)
            elif int(rework) == 3:
                stageService().rework_mode3(id, stage_name)
            convertStatusLog().add_rework_log(id, int(rework), request.session[Constant.SESSION_CURRENT_USER_ID],
                                              request.session[Constant.SESSION_CURRENT_USER_LOGINNAME])
        return JsonResponse({"success": True, "msg": "success"}, safe=False)


class convert_log(BaseView):
    """convert的操作记录"""

    def get(self, request):
        """跳转log页面"""
        convert_status_id = request.GET.get("convert_status_id")
        return render(request, "making_convert_log_list.html", {"convert_status_id": convert_status_id})

    def post(self, request):
        """获取log数据"""
        convert_status_id = request.POST.get("convert_status_id")
        super().post(request)
        logs = convert_operate_log.objects.values().filter(convert_status_id=convert_status_id).order_by(
            "-operation_time")
        data = {}
        data['total'] = convert_operate_log.objects.filter(convert_status_id=convert_status_id).count()
        data['rows'] = list(logs)[self.startIndex: self.endIndex]
        return JsonResponse(data, safe=False)


@csrf_exempt
def compile_lot(request):
    """编锅操作"""
    # TODO 编锅操作
    id = request.GET.get('id')
    status = request.GET.get('compile_status')
    query_set = lot_info.objects.get(id=id)
    # 修改编锅状态
    query_set.compile_status = status
    query_set.save()
    file_order = 'start'
    return file_order


# 编锅文件创建
# need  .ini文件及sigma等参数获取方式
@csrf_exempt
def file_create():
    file_order = compile_lot()
    if file_order == 'start':
        print('创建文件开始')
    else:
        pass


class convertOptionLogView(BaseView):
    def get(self, request):
        id = request.GET.get('id')
        log = convert_operate_log.objects.get(id=id).order_by('-operation_time')
        return render(request, 'making_convert_log_view.html', {'log': log})


class GenStage(BaseView):
    def post(self, request):
        tool_id_set = tree_option.objects.filter(tree_id=1, is_delete=0)
        tool_id_list = []
        for tool_id in tool_id_set:
            if tool_id.value not in tool_id_list:
                tool_id_list.append(tool_id.value)
        return JsonResponse({"success": True, "tool_id": tool_id_list}, safe=False)


class GenLotID(BaseView):
    def post(self, request):
        tip_no = request.POST.get('tip_no')
        mask_name = request.POST.get('mask_name')
        lot_set = lot_info.objects.filter(tip_no=tip_no, mask_name=mask_name, is_delete=0)
        lot_id_list = []
        data = {}
        for lot in lot_set:
            if lot.lot_id:
                lot_id_list.append(lot.lot_id)
        data['success'] = True
        data['lot_id_list'] = lot_id_list
        return JsonResponse(data, safe=False)