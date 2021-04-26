# coding:utf-8
"""system/role/ process method

"""
from utilslibrary.proxy.log_db_proxy import ProxyFactory, InvocationHandler
from django.http.response import HttpResponseRedirect, JsonResponse
from django.contrib.sessions.models import Session
from django.db import transaction
from django.db import transaction

from utilslibrary.base.base import BaseService
from system.models import sgd_user, sgd_pdf_log, sgd_email_log


@ProxyFactory(InvocationHandler)
class SGDService(BaseService):
    # add
    def add_sgd_user(self, sgd_user):
        data = {}
        try:
            sgd_user.save()
            data["success"] = True
            data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    # lock
    def lock_sgd_user(self, sgd_user):
        data = {}
        try:
            sgd_user.save()
            data["success"] = True
            data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    # unlock
    def unlock_sgd_user(self, sgd_user):
        data = {}
        try:
            sgd_user.save()
            data["success"] = True
            data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    # extension
    def extension_sgd_user(self, sgd_user):
        data = {}
        try:
            sgd_user.save()
            data["success"] = True
            data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    # pdf
    def upd_pdf_sgd_user(self, sgd_pdf_log):
        data = {}
        try:
            sgd_pdf_log.save()
            data["success"] = True
            data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    # del
    def del_sgd_user(self, obj):
        data = {}
        data["success"] = False
        data["msg"] = "Failed"
        ids = obj.id
        print('ids', ids)
        if not ids:
            data["success"] = False
            data["msg"] = "Failed"
            return JsonResponse(data, safe=False)

        with transaction.atomic():
            id_list = ids.split(",")
            for id in id_list:
                if id:
                    _o = sgd_user.objects.get(id=id)
                    _o.is_delete = 1
                    _o.save()
                    # _o = sgd_user.objects.get(id=id)
                    # _o.delete()

        data["success"] = True
        data["msg"] = "Success"
        return JsonResponse(data, safe=False)

    # send
    def upd_send_sgd_user(self, sgd_email_log):
        data = {}
        try:
            sgd_email_log.save()
            data["success"] = True
            data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)
