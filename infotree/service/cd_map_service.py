# coding:utf-8
import hashlib
import os
from django.db import transaction
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from utilslibrary.system_constant import Constant
from infotree.models import cd_map


class cd_map_upload_service:

    def file_upload(self, request):
        if request.method == 'POST':
            cd_map_id = request.POST.get('cd_map_id')
            upload_file = request.FILES.get('file')
            file_name = upload_file.name
            file_exit = file_name[file_name.find('.') + 1:]

            print('cd_map_id ', cd_map_id, upload_file, file_exit)
            with transaction.atomic():
                _o = cd_map.objects.get(pk=cd_map_id)

                # server_path = 'D:/' + _o.folder_name + "/"
                server_path = Constant.CD_MAP_PATH + _o.folder_name + "/"
                try:
                    if not os.path.exists(server_path):
                        os.mkdir(server_path)
                except OSError as e:
                    print(e)
                    pass

                file_path = os.path.join(server_path, file_name)
                default_storage.save(file_path, ContentFile(upload_file.read()))
                try:
                    if file_exit == 'dat':
                        cd_map.objects.filter(id=cd_map_id).update(is_delete=0,
                                                                   path=server_path,
                                                                   cd_map_dat_name=file_name)
                    elif file_exit == 'prm':
                        cd_map.objects.filter(id=cd_map_id).update(is_delete=0,
                                                                   path=server_path,
                                                                   index_prm_name=file_name)
                    return JsonResponse({'success': True}, safe=False)
                except Exception as e:
                    print(e)
                return JsonResponse({'success': False}, safe=False)
