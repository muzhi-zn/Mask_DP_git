# coding:utf-8
"""system/role/ process method

"""
from tooling_form.models import setting, upload_error_msg
from utilslibrary.proxy.log_db_proxy import ProxyFactory, InvocationHandler
from django.http.response import HttpResponseRedirect, JsonResponse
from django.contrib.sessions.models import Session
from django.db import transaction

from django.db.models import F, Q
from django.db import transaction

from django.utils import timezone

from utilslibrary.system_constant import Constant
from utilslibrary.base.base import BaseService


@ProxyFactory(InvocationHandler)
class ImportSetService(BaseService):

    def add_import_set(self, import_set):
        # return msg object
        data = {}
        try:
            import_set.save()
            data["success"] = True
            data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    def upd_import_set(self, import_set):
        data = {}
        try:
            import_set.save()
            data["success"] = True
            data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    def del_import_set(self, obj):
        # return msg object
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
                if id:
                    # _o = mdt_cad_layer.objects.get(id=id)
                    # _o.is_delete = 1
                    # _o.save()
                    _o = setting.objects.get(id=id)
                    _o.delete()

        data["success"] = True
        data["msg"] = "Success"
        return JsonResponse(data, safe=False)


@ProxyFactory(InvocationHandler)
class ErrorMsgService(BaseService):

    def add_error_msg(self, upload_error_msg):
        # return msg object
        data = {}
        try:
            upload_error_msg.save()
            data["success"] = True
            data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    def upd_error_msg(self, upload_error_msg):
        data = {}
        try:
            upload_error_msg.save()
            data["success"] = True
            data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    def del_error_msg(self, obj):
        # return msg object
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
                if id:
                    # _o = mdt_cad_layer.objects.get(id=id)
                    # _o.is_delete = 1
                    # _o.save()
                    _o = upload_error_msg.objects.get(id=id)
                    _o.delete()

        data["success"] = True
        data["msg"] = "Success"
        return JsonResponse(data, safe=False)
