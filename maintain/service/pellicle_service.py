from django.db import transaction
from django.http import JsonResponse
import traceback

from maintain.models import pellicle_mapping
from utilslibrary.base.base import BaseService
from utilslibrary.proxy.log_db_proxy import ProxyFactory, InvocationHandler


# @ProxyFactory(InvocationHandler)
class PellicleService(BaseService):
    def add_pellicle(self, p_m):
        data = {}
        try:
            p_m.save()
            data['success'] = True
            data['message'] = 'Pellicle Add Success'
            return JsonResponse(data, safe=False)
        except Exception as e:
            traceback.print_exc()
            data['success'] = False
            data['message'] = str(e)
            return JsonResponse(data, safe=False)

    def edit_pellicle(self, p_m):
        data = {}
        try:
            p_m.save()
            data['success'] = True
            data['message'] = 'Pellicle Edit Success'
            return JsonResponse(data, safe=False)
        except Exception as e:
            traceback.print_exc()
            data['success'] = False
            data['message'] = str(e)
            return JsonResponse(data, safe=False)

    def del_pellicle(self, p_m):
        data = {}
        try:
            ids = p_m.id
            id_list = ids.split(',')
            with transaction.atomic():
                for id in id_list:
                    pellicle = pellicle_mapping.objects.get(id=id)
                    pellicle.is_delete = 1
                    pellicle.save()
            data['success'] = True
            data['msg'] = 'Delete Pellicle Success'
            return JsonResponse(data, safe=False)

        except Exception as e:
            traceback.print_exc()
            data['success'] = False
            data['msg'] = str(e)
            return JsonResponse(data, safe=True)
