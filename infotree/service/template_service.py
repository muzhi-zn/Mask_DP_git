# coding:utf-8
from utilslibrary.proxy.log_db_proxy import ProxyFactory, InvocationHandler
from django.http.response import JsonResponse
from django.db import transaction
from utilslibrary.base.base import BaseService
from infotree.models import info_tree_template, info_tree_template_option


@ProxyFactory(InvocationHandler)
class template_service(BaseService):

    def add_template(self, temp):
        # return msg object
        data = {}
        try:
            temp.save()
            data["success"] = True
            data["msg"] = "Success"

        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    def upd_template(self, temp):
        data = {}
        try:
            temp.save()
            data["success"] = True
            data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    def del_template(self, temp):
        # return msg object
        data = {}
        data["success"] = False
        data["msg"] = "Failed"
        ids = temp.id
        if not ids:
            data["success"] = False
            data["msg"] = "Failed"
            return JsonResponse(data, safe=False)

        with transaction.atomic():
            id_list = ids.split(",")
            for id in id_list:
                if id:
                    temp_option_count = info_tree_template_option.objects.filter(temp_id=id, is_delete=0).count()
                    if temp_option_count == 0:
                        _o = info_tree_template.objects.get(id=id)
                        _o.is_delete = 1
                        _o.save()
                    else:
                        data["success"] = False
                        data["msg"] = "Failed"
                        return JsonResponse(data, safe=False)

        data["success"] = True
        data["msg"] = "Success"
        return JsonResponse(data, safe=False)


@ProxyFactory(InvocationHandler)
class template_option_service(BaseService):

    def add_template_option(self, option):
        # return msg object
        data = {}
        try:
            option.save()
            data["success"] = True
            data["msg"] = "Success"

        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    def upd_template_option(self, option):
        data = {}
        try:
            option.save()
            data["success"] = True
            data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    def del_template_option(self, option):
        # return msg object
        data = {}
        data["success"] = False
        data["msg"] = "Failed"
        ids = option.id
        if not ids:
            data["success"] = False
            data["msg"] = "Failed"
            return JsonResponse(data, safe=False)

        with transaction.atomic():
            id_list = ids.split(",")
            for id in id_list:
                if id:
                    _o = info_tree_template_option.objects.get(id=id)
                    _o.is_delete = 1
                    _o.save()

        data["success"] = True
        data["msg"] = "Success"
        return JsonResponse(data, safe=False)
