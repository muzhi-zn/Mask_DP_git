from django.db import transaction
from django.http import JsonResponse

from utilslibrary.base.base import BaseService
from utilslibrary.proxy.log_db_proxy import InvocationHandler, ProxyFactory
from tooling.models import ip_authorize_info


@ProxyFactory(InvocationHandler)
class IPService(BaseService):
    def addIP(self,ip):
        data = {}
        try:
            ip.save()
            data["success"] = True
            data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        # 获取所有log日志
        # ip_list_all = []
        # ip_list = []
        # log_list_all = log.object.filter();
        # if log_list_all and log_list_all._len_() > 0:
        #     # 获取每条log中的ip
        #     log_list_o = log_list_all[0]
        #     ip_o = log_list_o.ip
        #     # print(ip_o)
        #     for i in ip_list_all:
        #         if i == ip_o:
        #             print(ip_o)
        #             ip_list_all.append(ip_o)

        return JsonResponse(data, safe = False)


    def delIP(self,ip):
        data = {}
        data["success"] = False
        data["msg"] = "Failed"
        ids = ip.id
        if not ids:
            data["success"] = False
            data["msg"] = "Failed"
            return JsonResponse(data, self = False)
        with transaction.atomic():
            id_list = ids.split(",")
            for id in id_list:
                if id:
                    _o = ip_authorize_info.objects.get(id = id)
                    if _o:
                        _o.delete()

        data["success"] = True
        data["msg"] = "Success"
        return JsonResponse(data,safe = False)

    def updateIP(self,ip):
        data = {}
        try:
            ip.save()
            data["success"]=True
            data["msg"]="Success"
        except Exception as e:
            print(e)
            data["success"]=False
            data["msg"]="Failed"
        return  JsonResponse(data,safe = False)


