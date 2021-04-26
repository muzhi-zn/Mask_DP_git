# coding:utf-8
from utilslibrary.proxy.log_db_proxy import ProxyFactory, InvocationHandler
from django.http.response import JsonResponse
from utilslibrary.base.base import BaseService
from django.db import transaction
from infotree.models import tree, tree_option, unreleased_info


@ProxyFactory(InvocationHandler)
class tree_service(BaseService):
    def add_tree(self, _tree):
        # return msg object
        data = {}
        try:
            _tree.save()
            data["success"] = True
            data["msg"] = "Success"

        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    def upd_tree(self, _tree):
        data = {}
        try:
            _tree.save()
            data["success"] = True
            data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    def del_tree(self, _tree):
        data = {}
        data["success"] = False
        data["msg"] = "Failed"
        ids = _tree.id
        if not ids:
            data["success"] = False
            data["msg"] = "Failed"
            return JsonResponse(data, safe=False)

        with transaction.atomic():
            id_list = ids.split(",")
            for id in id_list:
                if id:
                    tree_option_count = tree_option.objects.filter(id=id, is_delete=0).count()
                    if tree_option_count == 0:
                        _o = tree.objects.get(id=id)
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
class tree_option_service(BaseService):
    def add_tree_option(self, tree_op):
        # return msg object
        data = {}
        try:
            tree_op.save()
            data["success"] = True
            data["msg"] = "Success"

        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    def upd_tree_option(self, tree_op):
        data = {}
        try:
            tree_op.save()
            data["success"] = True
            data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    def del_tree_option(self, tree_op):
        try:
            data = {}
            data["success"] = False
            data["msg"] = "Failed"
            ids = tree_op.id
            if not ids:
                data["success"] = False
                data["msg"] = "Failed"
                return JsonResponse(data, safe=False)

            with transaction.atomic():
                id_list = ids.split(",")
                for id in id_list:
                    if id:
                        _o = tree_option.objects.get(id=id)

                        _tree = tree.objects.get(id=_o.tree_id)

                        # print(_tree.name.lower())

                        # unreleased
                        unreleased_sql = "select * from infotree_unreleased_info " \
                                         "where binary " + _tree.name.lower() + " = '" + _o.value + "' and is_delete = 0"
                        unreleased_data = unreleased_info.objects.raw(unreleased_sql)

                        # unreleased_alta
                        unreleased_alta_sql = "select * from infotree_unreleased_info_alta " \
                                              "where binary " + _tree.name.lower() + " = '" + _o.value + "' and is_delete = 0"
                        unreleased_alta_data = unreleased_info.objects.raw(unreleased_alta_sql)

                        # release
                        released_sql = "select * from infotree_released_info " \
                                       "where binary " + _tree.name.lower() + " = '" + _o.value + "' and is_delete = 0"
                        released_data = unreleased_info.objects.raw(released_sql)

                        # released_alta
                        released_alta_sql = "select * from infotree_released_info_alta " \
                                            "where binary " + _tree.name.lower() + " = '" + _o.value + "' and is_delete = 0"
                        released_alta_data = unreleased_info.objects.raw(released_alta_sql)

                        if unreleased_data.__len__() != 0 and unreleased_alta_data.__len__() != 0 and \
                                released_data.__len__() != 0 and released_alta_data.__len__() != 0:
                            data["success"] = False
                            data["msg"] = "There are data in maintain, please do not delete !"
                            return JsonResponse(data, safe=False)

                        _o.is_delete = 1
                        _o.save()

            data["success"] = True
            data["msg"] = "Success"
            return JsonResponse(data, safe=False)
        except Exception as e:
            print(e)

            data["success"] = False
            data["msg"] = "Failed"
            return JsonResponse(data, safe=False)
