# coding:utf-8
"""system/office/ process method

"""
from utilslibrary.proxy.log_db_proxy import ProxyFactory,InvocationHandler
from django.http.response import HttpResponseRedirect, JsonResponse
from django.contrib.sessions.models import Session
from django.db.models import F,Q
from django.db import transaction


from django.utils import timezone

from utilslibrary.system_constant import Constant
from utilslibrary.base.base import BaseService
from system.models import office
@ProxyFactory(InvocationHandler)
class OfficeService(BaseService):
    def add_office(self,office):
        #return msg object
        data = {}
        try:
            office.save()
            data["success"]=True
            data["msg"]="Success"
        except Exception as e:
            print(e)
            data["success"]=False
            data["msg"]="Failed" 
        
        return JsonResponse(data,safe=False)
    
    
    def que_office(self,request,office):
        print('{} que data:{}')    
    
    def upd_office(self,office):
        data = {}
        try:
            office.save()
            data["success"]=True
            data["msg"]="Success"
        except Exception as e:
            print(e)
            data["success"]=False
            data["msg"]="Failed" 
        
        return JsonResponse(data,safe=False)    
    #del_
    #upd_ 
    
    
    #delete office by ids
    def del_office(self,obj):  
        #return msg object  
        data = {}
        data["success"]=False
        data["msg"]="Failed"
        id = obj.id
        if not id:
            data["success"]=False
            data["msg"]="Failed" 
            return JsonResponse(data,safe=False)
        
        with transaction.atomic():
            _o = office.objects.get(id=id)
            if _o:
                #logic delete
                _o.is_delete = 1
                _o.save()
                        
                data["success"]=True
                data["msg"]="Success"
                return JsonResponse(data,safe=False)    
            return JsonResponse(data,safe=False)
        