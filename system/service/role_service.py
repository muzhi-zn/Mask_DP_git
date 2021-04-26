# coding:utf-8
"""system/role/ process method

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
from system.models import role,user_role,role_menu,menu

@ProxyFactory(InvocationHandler)
class RoleService(BaseService):
    def add_role(self,role):
        #return msg object
        data = {}
        try:
            role.save()
            data["success"]=True
            data["msg"]="Success"
        except Exception as e:
            print(e)
            data["success"]=False
            data["msg"]="Failed" 
        
        return JsonResponse(data,safe=False)
    
    
    def que_role(self,request,role):
        print('{} que data:{}')    
    
    def upd_role(self,role):
        data = {}
        try:
            role.save()
            data["success"]=True
            data["msg"]="Success"
        except Exception as e:
            print(e)
            data["success"]=False
            data["msg"]="Failed" 
        
        return JsonResponse(data,safe=False)    
    #del_
    #upd_ 
    
    
    #delete role by ids
    def del_role(self,obj):  
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
                    _o = role.objects.get(id=id)
                    _o.delete()
                    role_menu.objects.filter(role_id=id).delete()    
                    
        data["success"]=True
        data["msg"]="Success"
        return JsonResponse(data,safe=False) 
    
#assign user role
    @transaction.atomic
    def assgin_user_role(self,id,ids):
        if ids:
            user_id_list = ids.split(',')
            for user_id in user_id_list:
                #query by user_id role_id
                _o_list = user_role.objects.filter(user_id=user_id,role_id=id)
                #if user_id role_id exists
                if _o_list.count()==0:
                    _o = user_role()
                    _o.user_id = user_id
                    _o.role_id = id
                    _o.save()   
    def assgin_role_menu(self,id,menuIds):
        data = {}
        data["success"]=False
        data["msg"]="Failed"
        with transaction.atomic():
            #delete all role_id=id
            role_menu.objects.filter(role_id=id).delete()
            if menuIds:
                m_list = menuIds.split(",")
                for item in m_list:
                    #do not save top menu
                    if item =="0":
                        continue
                    #do not save if exists
                    #_o_temp = role_menu.objects.filter(role_id=id,menu_id=item)
                    #if _o_temp.count()>0:
                    #    continue
                    #do not save when has sub menu
                    _o = role_menu()
                    _o_menu = menu.objects.get(id=item)
                    _o.type = 1
                    #if _o_menu.has_children=="true":
                    #    _o.type = 0
                    if _o_menu.type==1:
                        _o.type = 0
                    
                    
                    _o.role_id = id
                    _o.menu_id = item
                    _o.save()
            data["success"]=True
            data["msg"]="Success" 
            return JsonResponse(data,safe=False)
        return JsonResponse(data,safe=False)        