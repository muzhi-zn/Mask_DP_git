import json
from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render


# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from iems.models import iems_execute_result
import logging

log = logging.getLogger('log')

class IEMSCallback:
    """IEMS callback方法"""

    @csrf_exempt
    def callback(self, request):
        """回调方法"""
        param = request.body.decode('utf-8')
        log.info(param)
        param_json = json.loads(param)
        code = param_json.get('code')
        success = param_json.get('success')
        record_no = param_json.get('record_no')
        callback_result = param_json.get('result')
        i_e_r = iems_execute_result.objects.get(record_no=record_no, status=1)
        if i_e_r:
            if param_json.get("is_process_callback"):
                i_e_r.process_result = param_json.get("process_result")
                i_e_r.save()
            else:
                i_e_r.execute_end_time = datetime.now()
                if success:
                    i_e_r.status = 3
                else:
                    i_e_r.status = 4
                i_e_r.execute_result = callback_result
                i_e_r.save()
            return JsonResponse({'success': True}, safe=False)
        else:
            return JsonResponse({'success': False}, safe=False)
