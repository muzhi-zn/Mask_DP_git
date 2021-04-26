# coding:utf-8
"""system/dictionary/ process method

"""
from utilslibrary.proxy.log_db_proxy import ProxyFactory,InvocationHandler
from django.http.response import HttpResponseRedirect, JsonResponse
from django.db import transaction
from utilslibrary.system_constant import Constant
from utilslibrary.base.base import BaseService
from system.models import dict

@ProxyFactory(InvocationHandler)
class DictService(BaseService):
    
    #add dictionary
    def add_dict(self,dict):
        #return msg object
        data = {}
        try:
            dict.save()
            data["success"]=True
            data["msg"]="Success"
        except Exception as e:
            print(e)
            data["success"]=False
            data["msg"]="Failed" 
        
        return JsonResponse(data,safe=False)
    
    
    #dictionary update
    def upd_dict(self,obj):
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
    
    
    #delete dictionary by ids
    def del_dict(self,obj):  
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
                    dict.objects.filter(id=id).delete()
        data["success"]=True
        data["msg"]="Success"
        return JsonResponse(data,safe=False)    
    
    
    #dictionary update
    def upd_dict_value(self,obj):
        data = {}
        try:
            dict_o = dict.objects.get(id=obj.id)
            dict_o.label = obj.label
            dict_o.value = obj.value
            dict_o.sort = obj.sort
            dict_o.save()
            data["success"]=True
            data["msg"]="Success"
        except Exception as e:
            print(e)
            data["success"]=False
            data["msg"]="Failed" 
        
        return JsonResponse(data,safe=False)

class DictToSet():
    
    #query Cell dict to set
    def cellDictToSet(self):
        dict_set = ([])
        type_list = dict.objects.filter(description='MASK_DP_CELL')  
        for type in type_list:
            kv_list = dict.objects.filter(parent_id=type.id)
            for kv in kv_list:
                
                dict_set.append(type.type+'_'+kv.value)
        print(dict_set)
        return dict_set

class GetValueByType(BaseService):

    def getValue(self,type):
        dict.objects.filter(type=type)
    def getValueByLabel(self,label):
        _o_list = dict.objects.filter(label=label)
        if _o_list.count()>0:
            return _o_list[0].value
        return ''