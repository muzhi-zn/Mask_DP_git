# coding:utf-8
import hashlib
import os
import threading

from django.db import transaction
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from utilslibrary.system_constant import Constant
from infotree.models import cec
from utilslibrary.base.base import BaseService
from utilslibrary.proxy.log_db_proxy import ProxyFactory, InvocationHandler
from utilslibrary.utils.date_utils import getDateStr, getMilliSecond
from utilslibrary.utils.common_utils import getCurrentSessionName, getCurrentSessionID
from time import sleep


class cec_upload_service:

    def file_upload(self, request):
        if request.method == 'POST':
            sleep(1)
            cec_id = request.POST.get('cec_id')
            upload_file = request.FILES.get('file')
            file_name = upload_file.name
            file_exit = file_name[file_name.find('.') + 1:]

            print('cec_id ', cec_id, upload_file, file_exit)
            with transaction.atomic():
                _o = cec.objects.get(pk=cec_id)

                # server_path = 'D:/' + _o.folder_name + "/"
                server_path = Constant.CEC_PATH + _o.folder_name + "/"

                if not os.path.exists(server_path):
                    os.mkdir(server_path)

                file_path = os.path.join(server_path, file_name)
                default_storage.save(file_path, ContentFile(upload_file.read()))

                try:
                    cec.objects.filter(id=cec_id).update(is_delete=0, cec_path=server_path,
                                                         cec_name=file_name)
                    return JsonResponse({'success': True}, safe=False)
                except Exception as e:
                    print(e)
                    return JsonResponse({'success': False}, safe=False)
