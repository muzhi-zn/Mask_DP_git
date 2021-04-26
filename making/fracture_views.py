# coding=utf-8
import datetime
import json
import logging
import os
import shutil
import traceback

import paramiko
from django.shortcuts import render

from jdv.models import lot_info
from making.models import convert_status, record
from making.service.convert_status_service import convertStatusLog
from system.service.dict_service import GetValueByType
from tooling_form.service.show_tip_no_service import del_writer_ftp_file, del_fracture_file

from utilslibrary.decorators.catch_exception_decorators import catch_exception

from django.template.context_processors import request
from django.http.response import JsonResponse, FileResponse

from utilslibrary.base.base import BaseView
from making.service.fracture_service import GenerateFileService
from utilslibrary.system_constant import Constant
from django.views.decorators.csrf import csrf_exempt

from utilslibrary.utils import iems_utils
from utilslibrary.utils.common_utils import getCurrentSessionName, getCurrentSessionID
from utilslibrary.utils.iems_utils import pause_job

log = logging.getLogger('log')


class FractureReDeck(BaseView):
    @catch_exception
    @csrf_exempt
    # def post(self,request):
    def post(self, request):
        convert_status_id = request.POST.get("convert_status_id")
        lot_id = request.POST.get('lot_id')
        tip_no = request.POST.get('tip_no')
        mask_name = request.POST.get('mask_name')
        device_name = request.POST.get('device_name')
        stage_name = request.POST.get('stage_name')
        writer_status = convert_status.objects.get(mask_name=mask_name, device_name=device_name, stage='Writer',
                                                   lot_id=lot_id).status
        if writer_status == 2:
            return JsonResponse({'success': False, 'msg': 'Writer Operations is done,can not redeck or redo'})
        tool_id = lot_info.objects.get(lot_id=lot_id).info_tree_tool_id
        if tool_id:
            _s = GenerateFileService()
            # _s.recipe_deck_replacement(recipe_id=39)
            data = _s.fracture_deck(getCurrentSessionID(request), getCurrentSessionName(request), lot_id, tip_no,
                                    mask_name,
                                    device_name, stage_name, tool_id)
            result = 'success'
            message = 'FractureReDeck is OK'
            convertStatusLog().add_operation_log(convert_status_id, Constant.CONVERT_OPERATION_REDECK,
                                                 request.session[Constant.SESSION_CURRENT_USER_ID],
                                                 request.session[Constant.SESSION_CURRENT_USER_LOGINNAME],
                                                 result, message, '', '', '', '', '', '', datetime.datetime.now())
            return JsonResponse(data, safe=False)
        else:
            return JsonResponse({'success': False, 'msg': 'please define info tree tool id in writing mapping'})


class FractureReDo(BaseView):
    """fracture redo 操作方法"""

    def post(self, request):
        convert_status_id = request.POST.get("convert_status_id")
        lot_id = request.POST.get('lot_id')
        tip_no = request.POST.get('tip_no')
        mask_name = request.POST.get('mask_name')
        device_name = request.POST.get('device_name')
        writer_status = convert_status.objects.get(mask_name=mask_name, device_name=device_name, stage='Writer',
                                                   lot_id=lot_id).status
        if writer_status == 2:
            return JsonResponse({'success': False, 'message': 'Writer Operations is done,can not redeck or redo'})
        fracture_log_file = request.POST.get('fracture_log_file')
        writer_running = convert_status.objects.get(tip_no=tip_no, mask_name=mask_name, device_name=device_name,
                                                    stage='Writer')
        if writer_running.status == 1:
            return JsonResponse({'success': False, 'message': "writer file is uploading, can't do this"})
        c_s = convert_status.objects.get(pk=convert_status_id)
        is_running = request.POST.get('is_running')
        exec_url = GetValueByType().getValueByLabel(Constant.IEMS_SERVER_EXECUTE_CMD_URL)
        temp_no = GetValueByType().getValueByLabel(Constant.IEMS_FRACTURE_TEMPLATE_ID)
        callback_url = GetValueByType().getValueByLabel(Constant.FRACTURE_CALLBACK_URL)
        if is_running == 'true':
            record_no = c_s.record_no
            if c_s.status == Constant.CONVERT_STATUS_ON_GOING:
                iems_utils.pause_job(record_no)
                c_s.progress = '0.00%'
                c_s.save()
            else:
                c_s.progress = '0.00%'
                c_s.save()
        param = {}
        param['temp_no'] = temp_no
        param['params'] = c_s.location + ',' + c_s.file_name + ',' + fracture_log_file
        param['callback_url'] = callback_url
        submit_time = datetime.datetime.now()
        result_json = iems_utils.execute_cmd_url(exec_url, param)
        log.info(result_json)

        # 将后续站点置为wait
        search_data = {}
        search_data['mask_name'] = mask_name
        search_data['device_name'] = device_name
        stages = convert_status.objects.filter(**search_data)
        for stage in stages:
            if stage.stage != 'Fracture' and stage.stage != 'DB' and stage.stage != 'JDV' and stage.stage != 'CCD':
                stage.status = Constant.CONVERT_STATUS_WAIT
                stage.progress = '0.00%'
                stage.save()

        if result_json.get('code') == 400:
            record_no = result_json.get('data')[0] if result_json.get('data') else ''
            c_s = convert_status.objects.get(pk=convert_status_id)
            c_s.status = Constant.CONVERT_STATUS_JOB_FAIL
            c_s.operator = request.session[Constant.SESSION_CURRENT_USER_LOGINNAME]
            c_s.record_no = record_no
            c_s.save()
            result = 'failed'
            message = result_json.get('msg') or result_json.get('message')
            message = message.encode('utf-8')
            code = result_json.get('code')
            record_no = result_json.get('data')[0] if result_json.get('data') else ''
            convertStatusLog().add_operation_log(convert_status_id, Constant.CONVERT_OPERATION_REDO,
                                                 request.session[Constant.SESSION_CURRENT_USER_ID],
                                                 request.session[Constant.SESSION_CURRENT_USER_LOGINNAME],
                                                 result, message, exec_url, param, code, mask_name, device_name,
                                                 record_no,
                                                 submit_time)
            return JsonResponse({'success': False, 'message': message.decode('utf-8')})

        if result_json.get("code") == 200:
            record_no = result_json.get('data')[0] if result_json.get('data') else ''
            c_s = convert_status.objects.get(pk=convert_status_id)
            c_s.status = Constant.CONVERT_STATUS_ON_GOING
            c_s.operator = request.session[Constant.SESSION_CURRENT_USER_LOGINNAME]
            c_s.record_no = record_no
            c_s.save()
            result = 'success'
            message = result_json.get('msg').encode('utf-8')
            code = result_json.get('code')
            record_no = result_json.get('data')[0] if result_json.get('data') else ''
            convertStatusLog().add_operation_log(convert_status_id, Constant.CONVERT_OPERATION_REDO,
                                                 request.session[Constant.SESSION_CURRENT_USER_ID],
                                                 request.session[Constant.SESSION_CURRENT_USER_LOGINNAME],
                                                 result, message, exec_url, param, code, mask_name, device_name,
                                                 record_no, submit_time)
            return JsonResponse({'success': True, 'message': message.decode('utf-8')}, safe=False)
        else:
            record_no = result_json.get('data')[0] if result_json.get('data') else ''
            c_s = convert_status.objects.get(pk=convert_status_id)
            c_s.status = Constant.CONVERT_STATUS_JOB_FAIL
            c_s.operator = request.session[Constant.SESSION_CURRENT_USER_LOGINNAME]
            c_s.record_no = record_no
            c_s.save()
            record_no = result_json.get("record_no")
            result_json = iems_utils.query_result(record_no)
            print(result_json)
            result = 'failed'
            message = result_json.get('msg').encode('utf-8')
            code = result_json.get('code')
            record_no = result_json.get('data')[0] if result_json.get('data') else ''
            convertStatusLog().add_operation_log(convert_status_id, Constant.CONVERT_OPERATION_REDO,
                                                 request.session[Constant.SESSION_CURRENT_USER_ID],
                                                 request.session[Constant.SESSION_CURRENT_USER_LOGINNAME],
                                                 result, message, exec_url, param, code, mask_name, device_name,
                                                 record_no, submit_time)
            return JsonResponse({'success': False, 'message': message.decode('utf-8')}, safe=False)


class FractureReDeckAndDo(BaseView):
    """fracture re deck&do 操作"""

    def post(self, request):
        ### redeck
        convert_status_id = request.POST.get("convert_status_id")
        lot_id = request.POST.get('lot_id')
        tip_no = request.POST.get('tip_no')
        mask_name = request.POST.get('mask_name')
        device_name = request.POST.get('device_name')
        stage_name = request.POST.get('stage_name')
        c_s = convert_status.objects.get(pk=convert_status_id)
        writer_status = convert_status.objects.get(mask_name=mask_name, device_name=device_name, stage='Writer',
                                                   lot_id=lot_id).status
        if writer_status == 2:
            return JsonResponse({'success': False, 'msg': 'Writer Operations is done,can not redeck or redo'})
        tool_id = lot_info.objects.get(lot_id=lot_id).info_tree_tool_id
        try:
            if tool_id:
                _s = GenerateFileService()
                # _s.recipe_deck_replacement(recipe_id=39)
                data = _s.fracture_deck(getCurrentSessionID(request), getCurrentSessionName(request), lot_id, tip_no,
                                        mask_name,
                                        device_name, stage_name, tool_id)
                result = 'success'
                message = 'FractureReDeck is OK'
                convertStatusLog().add_operation_log(convert_status_id, Constant.CONVERT_OPERATION_REDECK,
                                                     request.session[Constant.SESSION_CURRENT_USER_ID],
                                                     request.session[Constant.SESSION_CURRENT_USER_LOGINNAME],
                                                     result, message, '', '', '', '', '', '', datetime.datetime.now())
                # return JsonResponse(data, safe=False)
            else:
                return JsonResponse({'success': False, 'msg': 'please define info tree tool id in writing mapping'})
        except:
            c_s.status = Constant.CONVERT_STATUS_JOB_FAIL
            c_s.operator = request.session[Constant.SESSION_CURRENT_USER_LOGINNAME]
            c_s.save()
            return JsonResponse({'success': False, 'msg': 'fracture redeck failed'}, safe=False)
        ### redo
        fracture_log_file = request.POST.get('fracture_log_file')
        writer_running = convert_status.objects.get(tip_no=tip_no, mask_name=mask_name, device_name=device_name,
                                                    stage='Writer')
        if writer_running.status == 1:
            return JsonResponse({'success': False, 'msg': "writer file is uploading, can't do this"})
        is_running = request.POST.get('is_running')
        exec_url = GetValueByType().getValueByLabel(Constant.IEMS_SERVER_EXECUTE_CMD_URL)
        temp_no = GetValueByType().getValueByLabel(Constant.IEMS_FRACTURE_TEMPLATE_ID)
        callback_url = GetValueByType().getValueByLabel(Constant.FRACTURE_CALLBACK_URL)
        if is_running == 'true':
            record_no = c_s.record_no
            if c_s.status == Constant.CONVERT_STATUS_ON_GOING:
                iems_utils.pause_job(record_no)
                c_s.progress = '0.00%'
                c_s.save()
            else:
                c_s.progress = '0.00%'
                c_s.save()
        param = {}
        param['temp_no'] = temp_no
        param['params'] = c_s.location + ',' + c_s.file_name + ',' + fracture_log_file
        param['callback_url'] = callback_url
        submit_time = datetime.datetime.now()
        result_json = iems_utils.execute_cmd_url(exec_url, param)
        log.info(result_json)

        # 将后续站点置为wait
        search_data = {}
        search_data['mask_name'] = mask_name
        search_data['device_name'] = device_name
        stages = convert_status.objects.filter(**search_data)
        for stage in stages:
            if stage.stage != 'Fracture' and stage.stage != 'DB' and stage.stage != 'JDV' and stage.stage != 'CCD':
                stage.status = Constant.CONVERT_STATUS_WAIT
                stage.progress = '0.00%'
                stage.save()

        if result_json.get('code') == 400:
            record_no = result_json.get('data')[0] if result_json.get('data') else ''
            c_s = convert_status.objects.get(pk=convert_status_id)
            c_s.status = Constant.CONVERT_STATUS_JOB_FAIL
            c_s.operator = request.session[Constant.SESSION_CURRENT_USER_LOGINNAME]
            c_s.record_no = record_no
            c_s.save()
            result = 'failed'
            message = result_json.get('msg') or result_json.get('message')
            message = message.encode('utf-8')
            code = result_json.get('code')
            record_no = result_json.get('data')[0] if result_json.get('data') else ''
            convertStatusLog().add_operation_log(convert_status_id, Constant.CONVERT_OPERATION_REDO,
                                                 request.session[Constant.SESSION_CURRENT_USER_ID],
                                                 request.session[Constant.SESSION_CURRENT_USER_LOGINNAME],
                                                 result, message, exec_url, param, code, mask_name, device_name,
                                                 record_no,
                                                 submit_time)
            return JsonResponse({'success': False, 'msg': message.decode('utf-8')})

        if result_json.get("code") == 200:
            record_no = result_json.get('data')[0] if result_json.get('data') else ''
            c_s = convert_status.objects.get(pk=convert_status_id)
            c_s.status = Constant.CONVERT_STATUS_ON_GOING
            c_s.operator = request.session[Constant.SESSION_CURRENT_USER_LOGINNAME]
            c_s.record_no = record_no
            c_s.save()
            result = 'success'
            message = result_json.get('msg').encode('utf-8')
            code = result_json.get('code')
            record_no = result_json.get('data')[0] if result_json.get('data') else ''
            convertStatusLog().add_operation_log(convert_status_id, Constant.CONVERT_OPERATION_REDO,
                                                 request.session[Constant.SESSION_CURRENT_USER_ID],
                                                 request.session[Constant.SESSION_CURRENT_USER_LOGINNAME],
                                                 result, message, exec_url, param, code, mask_name, device_name,
                                                 record_no, submit_time)
            return JsonResponse({'success': True, 'msg': message.decode('utf-8')}, safe=False)
        else:
            record_no = result_json.get('data')[0] if result_json.get('data') else ''
            c_s.status = Constant.CONVERT_STATUS_JOB_FAIL
            c_s.operator = request.session[Constant.SESSION_CURRENT_USER_LOGINNAME]
            c_s.record_no = record_no
            c_s.save()
            record_no = result_json.get("record_no")
            result_json = iems_utils.query_result(record_no)
            print(result_json)
            result = 'failed'
            message = result_json.get('msg').encode('utf-8')
            code = result_json.get('code')
            record_no = result_json.get('data')[0] if result_json.get('data') else ''
            convertStatusLog().add_operation_log(convert_status_id, Constant.CONVERT_OPERATION_REDO,
                                                 request.session[Constant.SESSION_CURRENT_USER_ID],
                                                 request.session[Constant.SESSION_CURRENT_USER_LOGINNAME],
                                                 result, message, exec_url, param, code, mask_name, device_name,
                                                 record_no, submit_time)
            return JsonResponse({'success': False, 'msg': message.decode('utf-8')}, safe=False)


class FractureXORReDeck(BaseView):
    @catch_exception
    @csrf_exempt
    # def post(self,request):
    def post(self, request):
        lot_id = request.POST.get('lot_id')
        mask_name = request.POST.get('mask_name')
        device_name = request.POST.get('device_name')
        writer_status = convert_status.objects.get(mask_name=mask_name, device_name=device_name, stage='Writer',
                                                   lot_id=lot_id).status
        if writer_status == 2:
            return JsonResponse({'success': False, 'msg': 'Writer Operations is done,can not redeck or redo'})
        convert_status_id = request.POST.get('convert_status_id')
        _s = GenerateFileService()
        data = _s.fracture_xor_deck(getCurrentSessionID(request), getCurrentSessionName(request), lot_id, device_name)
        if data.get('success'):
            result = 'success'
            message = 'FractureXORReDeck is OK'
            convertStatusLog().add_operation_log(convert_status_id, 3,
                                                 request.session[Constant.SESSION_CURRENT_USER_ID],
                                                 request.session[Constant.SESSION_CURRENT_USER_LOGINNAME],
                                                 result, message, '', '', '', '', '', '', datetime.datetime.now())
        return JsonResponse(data, safe=False)


class FractureXORReDo(BaseView):
    def post(self, request):
        id = request.POST.get("convert_status_id")
        lot_id = request.POST.get('lot_id')
        tip_no = request.POST.get('tip_no')
        mask_name = request.POST.get('mask_name')
        device_name = request.POST.get('device_name')
        writer_status = convert_status.objects.get(mask_name=mask_name, device_name=device_name, stage='Writer',
                                                   lot_id=lot_id).status
        if writer_status == 2:
            return JsonResponse({'success': False, 'message': 'Writer Operations is done,can not redeck or redo'})
        fracture_xor_log_file = request.POST.get('fracture_xor_log_file')
        writer_running = convert_status.objects.get(tip_no=tip_no, mask_name=mask_name, device_name=device_name,
                                                    stage='Writer')
        if writer_running.status == 1:
            return JsonResponse({'success': False, 'message': "writer file is uploading, can't do this"})
        submit_time = datetime.datetime.now()
        c_s = convert_status.objects.get(pk=id)
        is_running = request.POST.get('is_running')
        exec_url = GetValueByType().getValueByLabel(Constant.IEMS_SERVER_EXECUTE_CMD_URL)
        temp_no = GetValueByType().getValueByLabel(Constant.IEMS_FRACTURE_XOR_TEMPLATE_ID)
        callback_url = GetValueByType().getValueByLabel(Constant.FRACTURE_XOR_CALLBACK_URL)
        if is_running == 'true':
            record_no = c_s.record_no
            if c_s.status == Constant.CONVERT_STATUS_ON_GOING:
                iems_utils.pause_job(record_no)
                c_s.progress = '0.00%'
                c_s.save()
            else:
                c_s.progress = '0.00%'
                c_s.save()
        param = {}
        param['temp_no'] = temp_no
        param['params'] = c_s.location + ',' + 'mrcexe_lsf.sh' + ',' + c_s.file_name + ',' + fracture_xor_log_file
        param['callback_url'] = callback_url
        result_json = iems_utils.execute_cmd_url(exec_url, param)
        print(result_json)
        XORRemoveFile(c_s.location, c_s.file_name)
        if result_json.get('code') == 200:
            record_no = result_json.get('data')[0] if result_json.get('data') else ''
            c_s = convert_status.objects.get(pk=id)
            c_s.status = Constant.CONVERT_STATUS_ON_GOING
            c_s.operator = request.session[Constant.SESSION_CURRENT_USER_LOGINNAME]
            c_s.record_no = record_no
            c_s.save()
            code = result_json.get('code')
            result = 'success'
            message = result_json.get('msg').encode('utf-8')
            record_no = result_json.get('data')[0] if result_json.get('data') else ''
            convertStatusLog().add_operation_log(id, Constant.CONVERT_OPERATION_REDO,
                                                 request.session[Constant.SESSION_CURRENT_USER_ID],
                                                 request.session[Constant.SESSION_CURRENT_USER_LOGINNAME],
                                                 result, message, exec_url, param, code, mask_name, device_name,
                                                 record_no, submit_time)
            return JsonResponse({'success': True, 'message': 'Fracture XOR re do success'})
        else:
            record_no = result_json.get('data')[0] if result_json.get('data') else ''
            c_s = convert_status.objects.get(pk=id)
            c_s.status = Constant.CONVERT_STATUS_JOB_FAIL
            c_s.operator = request.session[Constant.SESSION_CURRENT_USER_LOGINNAME]
            c_s.record_no = record_no
            c_s.save()
            code = result_json.get('code')
            result = 'failed'
            log.info('XOR result code ==400')
            message = result_json.get('msg').encode('utf-8')
            record_no = result_json.get('data')[0] if result_json.get('data') else ''
            convertStatusLog().add_operation_log(id, Constant.CONVERT_OPERATION_REDO,
                                                 request.session[Constant.SESSION_CURRENT_USER_ID],
                                                 request.session[Constant.SESSION_CURRENT_USER_LOGINNAME],
                                                 result, message, exec_url, param, code, mask_name, device_name,
                                                 record_no, submit_time)
            return JsonResponse({'success': False, 'message': message.decode('utf-8')})


class FractureXORReDeckAndDo(BaseView):
    def post(self, request):
        ###redeck
        lot_id = request.POST.get('lot_id')
        mask_name = request.POST.get('mask_name')
        device_name = request.POST.get('device_name')
        writer_status = convert_status.objects.get(mask_name=mask_name, device_name=device_name, stage='Writer',
                                                   lot_id=lot_id).status
        if writer_status == 2:
            return JsonResponse({'success': False, 'msg': 'Writer Operations is done,can not redeck or redo'})
        convert_status_id = request.POST.get('convert_status_id')
        _s = GenerateFileService()
        data = _s.fracture_xor_deck(getCurrentSessionID(request), getCurrentSessionName(request), lot_id, device_name)
        if data.get('success'):
            result = 'success'
            message = 'FractureXORReDeck is OK'
            convertStatusLog().add_operation_log(convert_status_id, 3,
                                                 request.session[Constant.SESSION_CURRENT_USER_ID],
                                                 request.session[Constant.SESSION_CURRENT_USER_LOGINNAME],
                                                 result, message, '', '', '', '', '', '', datetime.datetime.now())
        # return JsonResponse(data, safe=False)
        ###redo
        id = request.POST.get("convert_status_id")
        tip_no = request.POST.get('tip_no')
        fracture_xor_log_file = request.POST.get('fracture_xor_log_file')
        writer_running = convert_status.objects.get(tip_no=tip_no, mask_name=mask_name, device_name=device_name,
                                                    stage='Writer')
        if writer_running.status == 1:
            return JsonResponse({'success': False, 'msg': "writer file is uploading, can't do this"})
        submit_time = datetime.datetime.now()
        c_s = convert_status.objects.get(pk=id)
        is_running = request.POST.get('is_running')
        exec_url = GetValueByType().getValueByLabel(Constant.IEMS_SERVER_EXECUTE_CMD_URL)
        temp_no = GetValueByType().getValueByLabel(Constant.IEMS_FRACTURE_XOR_TEMPLATE_ID)
        callback_url = GetValueByType().getValueByLabel(Constant.FRACTURE_XOR_CALLBACK_URL)
        if is_running == 'true':
            record_no = c_s.record_no
            if c_s.status == Constant.CONVERT_STATUS_ON_GOING:
                iems_utils.pause_job(record_no)
                c_s.progress = '0.00%'
                c_s.save()
            else:
                c_s.progress = '0.00%'
                c_s.save()
        param = {}
        param['temp_no'] = temp_no
        param['params'] = c_s.location + ',' + 'mrcexe_lsf.sh' + ',' + c_s.file_name + ',' + fracture_xor_log_file
        param['callback_url'] = callback_url
        result_json = iems_utils.execute_cmd_url(exec_url, param)
        print(result_json)
        XORRemoveFile(c_s.location, c_s.file_name)
        if result_json.get('code') == 200:
            record_no = result_json.get('data')[0] if result_json.get('data') else ''
            c_s = convert_status.objects.get(pk=id)
            c_s.status = Constant.CONVERT_STATUS_ON_GOING
            c_s.operator = request.session[Constant.SESSION_CURRENT_USER_LOGINNAME]
            c_s.record_no = record_no
            c_s.save()
            code = result_json.get('code')
            result = 'success'
            message = result_json.get('msg').encode('utf-8')
            record_no = result_json.get('data')[0] if result_json.get('data') else ''
            convertStatusLog().add_operation_log(id, Constant.CONVERT_OPERATION_REDO,
                                                 request.session[Constant.SESSION_CURRENT_USER_ID],
                                                 request.session[Constant.SESSION_CURRENT_USER_LOGINNAME],
                                                 result, message, exec_url, param, code, mask_name, device_name,
                                                 record_no, submit_time)
            return JsonResponse({'success': True, 'msg': 'Fracture XOR re do success'})
        else:
            record_no = result_json.get('data')[0] if result_json.get('data') else ''
            c_s = convert_status.objects.get(pk=id)
            c_s.status = Constant.CONVERT_STATUS_JOB_FAIL
            c_s.operator = request.session[Constant.SESSION_CURRENT_USER_LOGINNAME]
            c_s.record_no = record_no
            c_s.save()
            code = result_json.get('code')
            result = 'failed'
            log.info('XOR result code ==400')
            message = result_json.get('msg').encode('utf-8')
            record_no = result_json.get('data')[0] if result_json.get('data') else ''
            convertStatusLog().add_operation_log(id, Constant.CONVERT_OPERATION_REDO,
                                                 request.session[Constant.SESSION_CURRENT_USER_ID],
                                                 request.session[Constant.SESSION_CURRENT_USER_LOGINNAME],
                                                 result, message, exec_url, param, code, mask_name, device_name,
                                                 record_no, submit_time)
            return JsonResponse({'success': False, 'msg': message.decode('utf-8')})


class IsRunning(BaseView):

    def post(self, request):
        id = request.POST.get('convert_status_id')
        c_s = convert_status.objects.get(pk=id)
        if c_s.status == Constant.CONVERT_STATUS_ON_GOING or c_s.status == Constant.CONVERT_STATUS_DONE or c_s.status == Constant.CONVERT_STATUS_NO_CLEAN \
                or c_s.status == Constant.CONVERT_STATUS_JOB_FAIL:
            return JsonResponse({'success': True, 'msg': 'running'})
        else:
            return JsonResponse({'success': False, 'msg': 'failed'})


def XORRemoveFile(path, file_name):
    for parent, dirs, files in os.walk(path):
        for file in files:
            log.info(file)
            log.info(file_name)
            if file != file_name and file != 'mrcexe_lsf.sh':
                log.info(parent + '/' + file)
                os.remove(parent + '/' + file)
        for dir in dirs:
            shutil.rmtree(parent + '/' + dir)


class WriterRedo(BaseView):
    def post(self, request):
        lot_id = request.POST.get('lot_id')
        tip_no = request.POST.get('tip_no')
        lot_query = lot_info.objects.get(lot_id=lot_id)
        if lot_query.writer_create_file_status == 1 or lot_query.writer_create_file_status == 3:
            return JsonResponse({"success": False,
                                 'message': 'The file is uploading please do not operate'}, safe=False)
        else:
            try:
                precondition_set = convert_status.objects.filter(stage__in=['Fracture', 'XOR'], lot_id=lot_id)
                for precondition in precondition_set:
                    if precondition.status != 2:
                        if precondition.operation_status != 1:
                            return JsonResponse({"success": False, 'message': precondition.device_name + ',' +
                                                                              precondition.stage +
                                                                              ' have not been completed, please wait'},
                                                safe=False)
                query_set = convert_status.objects.filter(lot_id=lot_id, stage='Writer')
                for query in query_set:
                    query.status = 1
                    query.progress = '0.00%'
                    query.err_message = ''
                    query.save()
                lot_query.writer_create_file_status = 0
                lot_query.writer_create_file_error_message = ''
                lot_query.ftp_upload_status = 0
                lot_query.ftp_upload_error_message = ''
                lot_query.save()
                return JsonResponse({'success': True}, safe=False)
            except Exception as e:
                traceback.print_exc()
                return JsonResponse({"success": False, 'message': 'Failed'}, safe=False)


class FTPRedo(BaseView):
    def post(self, request):
        lot_id = request.POST.get('lot_id')
        lot_query = lot_info.objects.get(lot_id=lot_id)
        if lot_query.ftp_upload_status == 1 or lot_query.ftp_upload_status == 3:
            return JsonResponse({"success": False,
                                 'message': 'The file is uploading please do not operate'}, safe=False)
        else:
            try:
                result, msg = del_fracture_file(lot_id, True)
                if result:
                    lot_query.ftp_upload_status = 0
                    lot_query.ftp_upload_error_message = ''
                    lot_query.save()
                    return JsonResponse({'success': True}, safe=False)
                else:
                    return JsonResponse({"success": False, 'message': msg}, safe=False)
            except Exception as e:
                print(e)
                traceback.print_exc()
                return JsonResponse({"success": False, 'message': str(e)}, safe=False)
