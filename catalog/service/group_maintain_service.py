from django.db import transaction
from django.http import JsonResponse

from catalog.models import group_maintain
from utilslibrary.base.base import BaseService
from utilslibrary.proxy.log_db_proxy import ProxyFactory, InvocationHandler


@ProxyFactory(InvocationHandler)
class group_maintain_service(BaseService):
    def add_group_maintain(self, t_m):
        # return msg object
        data = {}
        try:
            t_m.save()
            data["success"] = True
            data["msg"] = "Success"

        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    def updt_group_maintain(self, t_m):
        data = {}
        try:
            t_m.save()
            data["success"] = True
            data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    def del_group_maintain(self, t_m):
        data = {}
        data["success"] = False
        data["msg"] = "Failed"
        ids = t_m.id
        if not ids:
            data["success"] = False
            data["msg"] = "Failed"
            return JsonResponse(data, safe=False)

        with transaction.atomic():
            id_list = ids.split(",")
            for id in id_list:
                if id:
                    r_t_m = group_maintain.objects.filter(id=id, is_delete=0).count()
                    if r_t_m != 0:
                        _o = group_maintain.objects.get(id=id)
                        _o.is_delete = 1
                        _o.save()
                    else:
                        data["success"] = False
                        data["msg"] = "Failed"
                        return JsonResponse(data, safe=False)

        data["success"] = True
        data["msg"] = "Success"
        return JsonResponse(data, safe=False)