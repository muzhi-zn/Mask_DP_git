# coding:utf-8
from utilslibrary.proxy.log_db_proxy import ProxyFactory, InvocationHandler
from django.http.response import JsonResponse
from utilslibrary.base.base import BaseService
from django.db import transaction
from infotree.models import maintain_table_mdt


@ProxyFactory(InvocationHandler)
class maintain_table_service(BaseService):

    def upd_maintain_table(self, _maintain_table):
        data = {}
        try:
            _maintain_table.save()
            data["success"] = True
            data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)


@ProxyFactory(InvocationHandler)
class maintain_table_mdt_service(BaseService):

    def add_mdt(self, mdt):
        data = {}
        try:
            mdt.save()
            data["success"] = True
            data["msg"] = "Success"

        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    def upd_mdt(self, mdt):
        data = {}
        try:
            mdt.save()
            data["success"] = True
            data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    def del_mdt(self, mdt):
        data = {}
        try:
            ids = mdt.id
            id_list = ids.split(',')
            with transaction.atomic():
                for id in id_list:
                    _o = maintain_table_mdt.objects.get(id=id)
                    _o.is_delete = 1
                    _o.save()
            data['success'] = True
            data['msg'] = 'Delete Success'
            return JsonResponse(data, safe=False)
        except Exception as e:
            print(e)
            data['success'] = False
            data['msg'] = e
            return JsonResponse(data, safe=True)
