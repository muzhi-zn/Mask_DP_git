# coding:utf-8
"""system/user/ process method

"""
from utilslibrary.proxy.log_db_proxy import ProxyFactory,InvocationHandler
from django.http.response import HttpResponseRedirect, JsonResponse
from django.contrib.sessions.models import Session
from django.db.models import F,Q
from django.db import transaction
from system.models import data_rule,role_data_rule

from django.utils import timezone

from utilslibrary.system_constant import Constant
from utilslibrary.base.base import BaseService
from system.models import menu
@ProxyFactory(InvocationHandler)
class DataRuleService(BaseService):

    @transaction.atomic
    def add_data_rule(self,obj):
        #return msg object
        data = {}
        try:
            obj.save()
            data["success"]=True
            data["msg"]="Success"

        except Exception as e:
            print(e)
            data["success"]=False
            data["msg"]="Failed"

        return JsonResponse(data,safe=False)


    @transaction.atomic
    def upd_data_rule(self,data_rule):
        data = {}
        try:
            data_rule.save()
            data["success"]=True
            data["msg"]="Success"

        except Exception as e:
            print(e)
            data["success"]=False
            data["msg"]="Failed"

        return JsonResponse(data,safe=False)

    #delete menu by ids
    @transaction.atomic
    def del_data_rule(self,obj):
        #return msg object
        data = {}
        data["success"]=False
        data["msg"]="Failed"
        id = obj.id
        if not id:
            data["success"]=False
            data["msg"]="Failed"
            return JsonResponse(data,safe=False)

        try:
            _o = data_rule.objects.get(id=id)
            _o.delete()
            data["success"]=True
            data["msg"]="Success"

        except Exception as e:
            print(e)
            data["success"]=False
            data["msg"]="Failed"

        return JsonResponse(data,safe=False)

    def role_data_rule_save(self, id, dataRuleIds):
        data = {}
        data["success"] = False
        data["msg"] = "Failed"
        with transaction.atomic():
            # delete all role_id=id
            role_data_rule.objects.filter(role_id=id).delete()
            if dataRuleIds:
                m_list = dataRuleIds.split(",")
                for item in m_list:
                    # do not save top menu
                    if item == "0":
                        continue
                    _o = role_data_rule()
                    _o.role_id = id
                    _o.data_rule_id = item
                    _o.save()
            data["success"] = True
            data["msg"] = "Success"
            return JsonResponse(data, safe=False)
        return JsonResponse(data, safe=False)


def add_data_rule(flag, request, q, session_id):
    """添加数据权限"""
    print("添加数据权限")
    if flag:
        _data_rule_id_list = request.session[session_id]
        for _data_rule_id in _data_rule_id_list:
            _o = data_rule.objects.get(id=_data_rule_id)
            if _o.r_express == '=':
                q.children.append((_o.r_filed, _o.r_value))
            elif _o.r_express == '>':
                q.children.append((_o.r_filed + '__gt', _o.r_value))
            elif _o.r_express == '>=':
                q.children.append((_o.r_filed + '__gte', _o.r_value))
            elif _o.r_express == '<':
                q.children.append((_o.r_filed + '__lt', _o.r_value))
            elif _o.r_express == '<=':
                q.children.append((_o.r_filed + '__lte', _o.r_value))
            elif _o.r_express == 'contain':
                q.children.append((_o.r_filed + '__contains', _o.r_value))
    return q