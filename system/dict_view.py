#--coding:utf-8 --
"""dictionary manage

"""
from django.shortcuts import render
from django.db import transaction
from django.http.response import HttpResponseRedirect, JsonResponse

from system.service.data_rule_service import add_data_rule
from utilslibrary.system_constant import Constant
from django.http import HttpResponse
from django.db.models import F, Q
from system.models import dict,data_rule
from django.conf import settings


from django.core import serializers
import json
from django.template.context_processors import request
from utilslibrary.utils.date_utils import getDateStr,getMilliSecond

from utilslibrary.base.base import BaseView
from system.service.dict_service import DictService
from utilslibrary.decorators.auth_decorators import AuthCheck
from django.utils.decorators import method_decorator
from utilslibrary.middleware.auth_check_middleware import AuthCheckMiddleWare

# Create your views here.
class DictList(BaseView):
    
    def get(self,request):
        type = request.GET.get("type")
        return render(request, 'system_dict_list.html',{"type":type})
    
    
    def post(self,request):
        #-----------------------------
        #需要获得翻页参数时添加
        #代码中使用self.startIndex和self.endIndex获取相应范围的记录
        #------------------------------
        super().post(request)
        
        
        #接收查询参数---与页面上要查询的条件匹配
        type = request.POST.get('type','')
        desc = request.POST.get('description','')
        """query by where1"""
        #添加查询条件，设置为逻辑与查询
        q = Q()
        q.connector = 'and '
        q.children.append(('parent_id',''))
        if type:
            q.children.append(('type__contains',type))
        if desc:
            q.children.append(('description__contains',desc))

        #query role data rule
        q = add_data_rule(settings.DATA_RULE_DICT_ENABLE, request, q, Constant.SESSION_CURRENT_USER_PERMISSION_DICT_DATARULE_ID_LIST)
        #get user role list


        #执行查询
        d_list = dict.objects.filter(q).order_by('-id')[self.startIndex:self.endIndex].values()     
        
        
        
        #组装JSON数据
        data = {}
        #设置总记录数
        data["total"] = dict.objects.filter(q).count()
        data["rows"] = list(d_list)
        print(data)
        
        return JsonResponse(data,safe=False)

class DictAdd(BaseView):
    
    def get(self,request):
        return render(request, 'system_dict_form.html',{"method":"add"})
    
    def post(self,request):
        data = {}
        
        id = request.POST.get('id')
        type = request.POST.get('type','')
        description = request.POST.get('description','')
        if type =='':
            data["success"]=False
            data["msg"]="Failed" 
            return JsonResponse(data,safe=False)
        
        #insert data
            
        #check the record has exist
        dict_o = dict.objects.filter(type=type)
        if dict_o:
            data["success"]=False
            data["msg"]="type name exists!" 
            return JsonResponse(data,safe=False)
        dict_o = dict()
        dict_o.type = type
        dict_o.description = description
        dict_service = DictService()
            
        return dict_service.add_dict(dict_o)

class DictView(BaseView):
    
    def get(self,request):
        id = request.GET.get("id")
        print(id)
        if not id:
            return render(request, 'system_dict_form.html')
        else:
            d_o = dict.objects.get(id=id)
            return render(request, 'system_dict_form.html',{"id" : d_o.id,"type" : d_o.type, "description" : d_o.description})
        

class DictEdit(BaseView):
    
    def get(self,request):
        id = request.GET.get("id")
        print(id)
        if not id:
            return render(request, 'system_dict_form.html',{"method":"edit"})
        else:
            d_o = dict.objects.get(id=id)
            return render(request, 'system_dict_form.html',{"id" : d_o.id,"type" : d_o.type, "description" : d_o.description,"method":"edit"})
    def post(self,request):
        data = {}
        
        id = request.POST.get('id')
        type = request.POST.get('type','')
        description = request.POST.get('description','')
        if type =='':
            data["success"]=False
            data["msg"]="Failed" 
            return JsonResponse(data,safe=False)
        
        if id :
            #update data
            dict_o = dict()
            dict_o = dict.objects.get(id=id)
            dict_o.type = type
            dict_o.description = description
            dict_service = DictService()
            return dict_service.upd_dict( dict_o)
        
#dictionary delete
class DictDel(BaseView):
    
    def get(self,request):
        data = {}
        ids=request.GET.get("ids")
        data["success"]=True
        data["msg"]="Success" 
        d_o = dict()
        d_o.id = ids
        d_s = DictService()
        
        return d_s.del_dict( d_o)  
    
#dictionary form ,update or view    
class DictValueForm(BaseView):
    
    def get(self,request):
        dictTypeid = request.GET.get('dictTypeId')
        dictValueid = request.GET.get('dictValueId')
        label = ''
        value = ''
        sort = ''
        if dictValueid:
            dict_o = dict.objects.get(id=dictValueid)
            label = dict_o.label
            value = dict_o.value
            sort = dict_o.sort
            return render(request, 'system_dict_value_form.html',{"dictTypeId" : dictTypeid,"dictValueId":dictValueid,"label":label,"value":value,"sort":sort})
        print(dictTypeid)
        return render(request, 'system_dict_value_form.html',{"dictTypeId" : dictTypeid})
    def post(self,request):
        data = {}
        
        dictTypeId = request.POST.get('dictTypeId')
        dictValueId = request.POST.get('dictValueId')
        label = request.POST.get('label','')
        value = request.POST.get('value','')
        sort = request.POST.get('sort')
        id = request.POST.get('id')
        if type =='':
            data["success"]=False
            data["msg"]="Failed" 
            return JsonResponse(data,safe=False)
        print("id=",id)
        if dictValueId :
            #update data
            dict_o = dict()
            dict_o.id = dictValueId
            dict_o.label = label
            dict_o.value = value
            dict_o.sort = sort
            dict_service = DictService()
            return dict_service.upd_dict_value( dict_o)
        else :
            #insert data
            
            #check the record has exist
            dict_o = dict.objects.filter(label=label,parent_id=dictTypeId)
            if dict_o:
                data["success"]=False
                data["msg"]="type name exists!" 
                return JsonResponse(data,safe=False)
            dict_o = dict()
            dict_o.parent_id = dictTypeId
            dict_o.label = label
            dict_o.value = value
            dict_o.sort = sort
            dict_o.create_date = getDateStr()
            dict_o.create_time = getMilliSecond()
            dict_service = DictService()
            
            return dict_service.add_dict(dict_o)


class DictValueList(BaseView):
    
    def get(self,request):
        return render(request, 'system_dict_list.html')
    
    
    def post(self,request):
        #-----------------------------
        #需要获得翻页参数时添加
        #代码中使用self.startIndex和self.endIndex获取相应范围的记录
        #------------------------------
        #super().post(request)
        
        
        #接收查询参数---与页面上要查询的条件匹配
        dictTypeId = request.POST.get('dictTypeId','')
        """query by where1"""
        #添加查询条件，设置为逻辑与查询
        q = Q()
        q.connector = 'and '
        if type:
            q.children.append(('parent_id',dictTypeId))
        #执行查询
        d_list = dict.objects.filter(q).order_by('-sort').values()
        
        
        #组装JSON数据
        data = {}
        #设置总记录数
        data["total"] = dict.objects.filter(q).count()
        data["rows"] = list(d_list)
        print(data)
        
        return JsonResponse(data,safe=False)


class DictValueDel(BaseView):
    
    def get(self,request):
        data = {}
        dictValueId=request.GET.get("dictValueId")
        data["success"]=True
        data["msg"]="Success" 
        d_o = dict()
        d_o.id = dictValueId
        d_s = DictService()
        
        return d_s.del_dict(d_o)


class DictValueListByParentType(BaseView):

    def post(self, request):

        # 接收查询参数---与页面上要查询的条件匹配
        type = request.POST.get('template_type', '')
        _o = dict.objects.get(type=type)
        """query by where1"""
        # 添加查询条件，设置为逻辑与查询
        q = Q()
        q.connector = 'and '
        q.children.append(('parent_id', _o.id))
        # 执行查询
        d_list = dict.objects.filter(q).order_by('-sort').values()

        # 组装JSON数据
        #data = {}
        # 设置总记录数
        #data["total"] = dict.objects.filter(q).count()
        #data["rows"] = list(d_list)
        #print(data)

        return JsonResponse(list(d_list), safe=False)

