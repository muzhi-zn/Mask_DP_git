from catalog.models import tool_maintain
from maintain.models import maintain_change_log
from utilslibrary.proxy.log_db_proxy import ProxyFactory, InvocationHandler
from django.http.response import JsonResponse
from utilslibrary.base.base import BaseService
from django.db import transaction
from infotree.models import tree, tree_option, unreleased_info
from utilslibrary.utils.common_utils import getCurrentSessionName


@ProxyFactory(InvocationHandler)
class tool_maintain_service(BaseService):
    def add_tool_maintain(self, t_m, c_l):
        # return msg object
        data = {}
        try:
            t_m.save()
            c_l.data_id = t_m.id
            c_l.save()
            data["success"] = True
            data["msg"] = "Success"

        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    def updt_tool_maintain(self, t_m):
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

    def del_tool_maintain(self, t_m, request):
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
                    r_t_m = tool_maintain.objects.filter(id=id, is_delete=0).count()
                    if r_t_m != 0:
                        _o = tool_maintain.objects.get(id=id)
                        old_data = {}
                        old_data['tool_id'] = _o.tool_id
                        old_data['group_name'] = _o.group_name
                        old_data['exptool'] = _o.exptool
                        old_data['ip'] = _o.ip
                        old_data['account'] = _o.account
                        old_data['password'] = _o.password
                        old_data['tool_type'] = _o.tool_type
                        old_data['path'] = _o.path
                        c_l = maintain_change_log()
                        c_l.data_id = _o.id
                        c_l.old_data = old_data
                        c_l.change_user = getCurrentSessionName(request)
                        c_l.operation = 'Delete'
                        c_l.table = 'Tool Maintain'
                        c_l.save()
                        _o.is_delete = 1
                        _o.save()
                    else:
                        data["success"] = False
                        data["msg"] = "Failed"
                        return JsonResponse(data, safe=False)

        data["success"] = True
        data["msg"] = "Success"
        return JsonResponse(data, safe=False)
