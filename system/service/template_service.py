# coding:utf-8
"""system/template/ process method

"""
from utilslibrary.proxy.log_db_proxy import ProxyFactory,InvocationHandler
from django.http.response import HttpResponseRedirect, JsonResponse
from django.contrib.sessions.models import Session
from django.db import transaction

from django.db.models import F,Q
from django.db import transaction


from django.utils import timezone

from utilslibrary.system_constant import Constant
from utilslibrary.base.base import BaseService
from system.models import template

@ProxyFactory(InvocationHandler)
class TemplateService(BaseService):
    def add_template(self,template):
        #return msg object
        data = {}
        try:
            template.save()
            data["success"]=True
            data["msg"]="Success"
        except Exception as e:
            print(e)
            data["success"]=False
            data["msg"]="Failed" 
        
        return JsonResponse(data,safe=False)
    
    
    def que_template(self,request,template):
        print('{} que data:{}')    
    
    def upd_template(self,template):
        data = {}
        try:
            template.save()
            data["success"]=True
            data["msg"]="Success"
        except Exception as e:
            print(e)
            data["success"]=False
            data["msg"]="Failed" 
        
        return JsonResponse(data,safe=False)    
    #del_
    #upd_ 
    
    
    #delete template by ids
    def del_template(self,obj):  
        #return msg object  
        data = {}
        data["success"]=False
        data["msg"]="Failed"
        ids = obj.id
        if not ids:
            data["success"]=False
            data["msg"]="Failed" 
            return JsonResponse(data,safe=False)
        
        with transaction.atomic():
            id_list=ids.split(",")
            for id in id_list:
                if id:
                    _o = template.objects.get(id=id)
                    _o.is_delete = 1
                    _o.save()
                    
        data["success"]=True
        data["msg"]="Success"
        return JsonResponse(data,safe=False) 
   