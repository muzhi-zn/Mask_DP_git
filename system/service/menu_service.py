# coding:utf-8
"""system/user/ process method

"""
from utilslibrary.proxy.log_db_proxy import ProxyFactory,InvocationHandler
from django.http.response import HttpResponseRedirect, JsonResponse
from django.contrib.sessions.models import Session
from django.db.models import F,Q
from django.db import transaction


from django.utils import timezone

from utilslibrary.system_constant import Constant
from utilslibrary.base.base import BaseService
from system.models import menu
@ProxyFactory(InvocationHandler)
class MenuService(BaseService):
    
    @transaction.atomic
    def add_menu(self,obj):
        #return msg object
        data = {}
        try:
            obj.save()
            obj.sort = obj.id
            obj.save()
            #if type=1,set parent menu has_children=true
            if obj.type=="1" and obj.parent_id!="0":
                _o_parent_menu = menu.objects.get(id=obj.parent_id)
                _o_parent_menu.has_children = "true"
                _o_parent_menu.save()
            data["success"]=True
            data["msg"]="Success"
            menu_json = {}
            menu_json["id"] = obj.id
            menu_json["parent_id"] = obj.parent_id
            menu_json["parent_ids"] = obj.parent_ids
            body = {}
            body["menu"] = menu_json
            data["body"] = body
        except Exception as e:
            print(e)
            data["success"]=False
            data["msg"]="Failed" 
        
        return JsonResponse(data,safe=False)
    
    
    @transaction.atomic
    def upd_menu(self,menu):
        data = {}
        try:
            menu.save()
            data["success"]=True
            data["msg"]="Success"
            menu_json = {}
            menu_json["id"] = menu.id
            menu_json["parent_id"] = menu.parent_id
            menu_json["parent_ids"] = menu.parent_ids
            body = {}
            body["menu"] = menu_json
            data["body"] = body
        except Exception as e:
            print(e)
            data["success"]=False
            data["msg"]="Failed" 
        
        return JsonResponse(data,safe=False)    
    
    #delete menu by ids
    @transaction.atomic
    def del_menu(self,obj):  
        #return msg object  
        data = {}
        data["success"]=False
        data["msg"]="Failed"
        id = obj.id
        if not id:
            data["success"]=False
            data["msg"]="Failed" 
            return JsonResponse(data,safe=False)
        _o_list = menu.objects.filter(parent_id=id)
        if _o_list.count()>0:
            data["success"]=False
            data["msg"]="Has sub menu!" 
            return JsonResponse(data,safe=False)        
            
        try:
            _o = menu.objects.get(id=id)
            _o_list = menu.objects.filter(parent_id=_o.parent_id,type=1)
            if _o_list.count()==1:
                #set parent menu haschildren=false
                _o_parent_menu = menu.objects.get(id=_o.parent_id)
                _o_parent_menu.has_children = "false"
                _o_parent_menu.save()
            _o.delete()
            
            #if has children menu count=1
                
            data["success"]=True
            data["msg"]="Success"
            
        except Exception as e:
            print(e)
            data["success"]=False
            data["msg"]="Failed" 
        
        return JsonResponse(data,safe=False)   
    
    @transaction.atomic  
    def sort(self,id1,sort1,id2,sort2):
        #return msg object  
        data = {}
        data["success"]=False
        data["msg"]="Failed"
        with transaction.atomic():
            _o1 = menu.objects.get(id=id1)
            _o1.sort = sort1
            _o2 = menu.objects.get(id=id2)
            _o2.sort = sort2
            _o1.save()
            _o2.save()
            data["success"]=True
            data["msg"]="Success"
            return JsonResponse(data,safe=False)    
        return JsonResponse(data,safe=False)
        
    @transaction.atomic
    def generate_sub_menu(self,obj):  
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
            _o_parent = menu.objects.get(id=id)
            if _o_parent.base_href =='':
                data["success"]=False
                data["msg"]="Base Href empty!" 
                return JsonResponse(data,safe=False)
            if _o_parent.type ==2:
                data["success"]=False
                data["msg"]="Button cannot generate sub menu!" 
                return JsonResponse(data,safe=False)
            _o_parent.has_children = "true"
            _o_parent.save()
            _o = menu()
            _o.parent_id = _o_parent.id
            _o.parent_ids =_o_parent.parent_ids+str(_o_parent.id)+","
            _o.has_children = "false"
            _o.icon = ""
            _o.is_show = 0
            _o.type = 2
            _o.name = "add"
            _o.href = _o_parent.base_href+"add/"
            _o.save()
            
            _o = menu()
            _o.parent_id = _o_parent.id
            _o.parent_ids =_o_parent.parent_ids+str(_o_parent.id)+","
            _o.has_children = "false"
            _o.icon = ""
            _o.is_show = 0
            _o.type = 2
            _o.name = "edit"
            _o.href = _o_parent.base_href+"edit/"
            _o.save()
            
            _o = menu()
            _o.parent_id = _o_parent.id
            _o.parent_ids =_o_parent.parent_ids+str(_o_parent.id)+","
            _o.has_children = "false"
            _o.icon = ""
            _o.is_show = 0
            _o.type = 2
            _o.name = "del"
            _o.href = _o_parent.base_href+"del/"
            _o.save()
            
            _o = menu()
            _o.parent_id = _o_parent.id
            _o.parent_ids =_o_parent.parent_ids+str(_o_parent.id)+","
            _o.has_children = "false"
            _o.icon = ""
            _o.is_show = 0
            _o.type = 2
            _o.name = "list"
            _o.href = _o_parent.base_href+"list/"
            _o.save()
            
            _o = menu()
            _o.parent_id = _o_parent.id
            _o.parent_ids =_o_parent.parent_ids+str(_o_parent.id)+","
            _o.has_children = "false"
            _o.icon = ""
            _o.is_show = 0
            _o.type = 2
            _o.name = "view"
            _o.href = _o_parent.base_href+"view/"
            _o.save()
            
            #if has children menu count=1
                
            data["success"]=True
            data["msg"]="Success"
            menu_json = {}
            menu_json["id"] = _o.id
            menu_json["parent_id"] = _o.parent_id
            menu_json["parent_ids"] = _o.parent_ids
            body = {}
            body["menu"] = menu_json
            data["body"] = body
            
        except Exception as e:
            print(e)
            data["success"]=False
            data["msg"]="Failed" 
        
        return JsonResponse(data,safe=False)   
        

        