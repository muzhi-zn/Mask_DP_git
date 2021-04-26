from django.db import transaction
from django.http import JsonResponse

from making.models import fracture_callback
from utilslibrary.base.base import BaseService
from utilslibrary.proxy.log_db_proxy import ProxyFactory, InvocationHandler


@ProxyFactory(InvocationHandler)
class FractureCallBackService(BaseService):

    def del_callback(self,obj):
        data = {}
        data["success"] = False
        data["msg"] = "Failed"
        ids = obj.id
        if not ids:
            data["success"] = False
            data["msg"] = "Failed"
            return JsonResponse(data, safe=False)

        with transaction.atomic():
            id_list = ids.split(",")
            for id in id_list:
                if id :
                    callback_count = fracture_callback.objects.filter(id=id).values().count()
                    if callback_count == 1:
                        _o = fracture_callback.objects.get(id=id)
                        _o.is_delete = 1
                        _o.save()
                    else:
                        data["success"] = False
                        data["msg"] = "Failed,Please confirm whether all data of fracture call back have been deleted"

        data["success"] = True
        data["msg"] = "Success"
        return JsonResponse(data,safe=False)

    def addCallbackLog(self,obj):
        try:

            obj.save()
            data = {'code': 200, 'msg': 'success'}

        except Exception as e:
            print(e)
            data = {'code': 400, 'msg': str(e)}
        return JsonResponse(data, safe=False)