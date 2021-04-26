import logging
import re
import time
import paramiko
import os
import shutil
import ftplib
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
import json
from making.models import fracture_callback, convert_status
from making.service.call_back_service import FractureCallBackService
from utilslibrary.base.base import BaseView
from utilslibrary.system_constant import Constant
from utilslibrary.utils.date_utils import getMilliSecond, getDateStr
from jdv.models import lot_info

log = logging.getLogger('log')


class CallBackLogList(BaseView):
    def get(self, request):
        return render(request, 'callback_log.html')

    def post(self, request):
        super().post(request)
        data_id = request.POST.get('data_id')
        query_date = request.POST.get('query_date')
        query_set = fracture_callback.objects.filter(is_delete=0).order_by("-id")
        if query_date:
            time_list = query_date.split(' ', 3)
            time_to = time_list[-1]
            time_from_list = []
            time_from_list.append(time_list[0])
            time_from_list.append(time_list[1])
            from_time = ' '.join(time_from_list)
            timeArray = time.strptime(time_to, "%Y-%m-%d %H:%M:%S")
            timeStamp_to = int(time.mktime(timeArray))
            timeArray = time.strptime(from_time, "%Y-%m-%d %H:%M:%S")
            timeStamp_from = int(time.mktime(timeArray))
            query_set = query_set.filter(callback_time__range=(timeStamp_from, timeStamp_to))
        if data_id:
            query_set = query_set.filter(data_id=data_id)
        data = {}
        data['total'] = query_set.count()
        data['rows'] = list(query_set[self.startIndex:self.endIndex].values())
        print(data)
        return JsonResponse(data, safe=False)


class CallBackDel(BaseView):

    def get(self, request):
        data = {}
        ids = request.GET.get("ids")
        data["success"] = True
        data["msg"] = "Success"
        _o = fracture_callback()
        _o.id = ids
        _s = FractureCallBackService()

        return _s.del_callback(_o)


class CallBackView(BaseView):

    def get(self, request):
        id = request.GET.get('id')
        if not id:
            return render(request, 'making_fracture_callback_form.html')
        else:
            _o = fracture_callback.objects.get(id=id)
            return render(request, 'making_fracture_callback_form.html', {'i_o': _o})


class CallBackLogProgressHistory(BaseView):

    def get(self, request):
        id = request.GET.get('id')
        return render(request, 'convert_status_progress_history.html', {'id': id})

    def post(self, request):
        super().post(request)
        id = request.POST.get('id')
        record_no = convert_status.objects.get(pk=id).record_no
        query_set = fracture_callback.objects.filter(record_no=record_no).order_by('-callback_time').values()
        data = {}
        data['total'] = query_set.count()
        data['rows'] = list(query_set[self.startIndex:self.endIndex])
        return JsonResponse(data, safe=False)


@csrf_exempt
def callback_log(request):
    print("============================ callback_log =================================")
    param = request.body.decode('utf-8')
    param_json = json.loads(param)
    log.info(param_json)
    code = param_json.get('code')
    msg = param_json.get('msg')
    record_no = param_json.get('record_no')
    # print('record_no= '+record_no+ ' id = '+ id +' code = '+str(code) + ' msg=' + msg);

    _o = fracture_callback()
    _o.record_no = record_no
    _o.result_code = code
    _o.result_content = msg
    _o.callback_date = getDateStr()
    _o.callback_time = getMilliSecond()
    _o.create_time = getMilliSecond()
    _o.create_date = getDateStr()
    _o.callback_return_status = 1
    _s = FractureCallBackService()
    c_s = convert_status.objects.filter(record_no=record_no).first()
    if c_s:
        if code == 104 and msg != 'nonclean':
            c_s.status = Constant.CONVERT_STATUS_DONE
            c_s.progress = '100.00%'
            c_s.save()

        elif code == 102:
            c_s.status = Constant.CONVERT_STATUS_ON_GOING
            pattern = r'\d+%' if c_s.stage == 'XOR' else r'\d+.\d+%'
            if re.search(pattern=pattern, string=msg):
                c_s.progress = re.search(pattern=pattern, string=msg).group()
                c_s.progress_history = c_s.progress_history + ',' + re.search(pattern=pattern, string=msg).group()
            c_s.save()
        elif code == 103 or msg == 'read log error':
            c_s.status = Constant.CONVERT_STATUS_JOB_FAIL
            c_s.err_message = msg
            c_s.save()
        elif msg == 'nonclean':
            c_s.status = Constant.CONVERT_STATUS_NO_CLEAN
            c_s.progress = '100.00%'
            c_s.save()
        elif code == 0 and c_s.stage == 'XOR':
            try:
                c_s.status = Constant.CONVERT_STATUS_JOB_FAIL
                c_s.err_message = msg
                c_s.save()
            except:
                c_s.status = Constant.CONVERT_STATUS_JOB_FAIL
                c_s.err_message = 'Too many errors, please check for yourself'
                c_s.save()
        else:
            try:
                c_s.status = Constant.CONVERT_STATUS_JOB_FAIL
                c_s.err_message = msg
                c_s.save()
            except:
                c_s.status = Constant.CONVERT_STATUS_JOB_FAIL
                c_s.err_message = 'Too many errors, please check for yourself'
                c_s.save()
    return _s.addCallbackLog(_o)
