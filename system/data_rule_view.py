#--coding:utf-8 --
"""data rule manage

"""
from django.shortcuts import render

from system.models import menu,data_rule,role_data_rule
from django.http.response import HttpResponseRedirect, JsonResponse
from utilslibrary.system_constant import Constant
from django.http import HttpResponse
from django.db.models import F,Q

from django.core import serializers
import json
from utilslibrary.decorators.auth_decorators import AuthCheck
from django.template.context_processors import request
from system.service.data_rule_service import DataRuleService
from utilslibrary.models.tree_model import TreeInfo,State
from utilslibrary.models.menu_model import MenuInfo
from utilslibrary.base.base import BaseView


class DataRuleList(BaseView):
    
    def get(self,request):
        return render(request, 'system_menu_list.html')

    def post(self, request):
        # -----------------------------
        # 需要获得翻页参数时添加
        # 代码中使用self.startIndex和self.endIndex获取相应范围的记录
        # ------------------------------
        super().post(request)

        # 接收查询参数---与页面上要查询的条件匹配
        menu_id = request.POST.get('menu_id', '')
        """query by where1"""
        # 添加查询条件，设置为逻辑与查询
        q = Q()
        q.connector = 'and '
        q.children.append(('is_delete', 0))
        if menu_id:
            q.children.append(('menu_id',menu_id))
        print('startIndex{} endIndex{}'.format(self.startIndex, self.endIndex))
        # 执行查询
        u_list = data_rule.objects.filter(q).order_by('-id')[self.startIndex:self.endIndex].values()

        # 组装JSON数据
        data = {}
        # 设置总记录数
        data["total"] = data_rule.objects.filter(q).count()
        data["rows"] = list(u_list)
        print(data)

        return JsonResponse(data, safe=False)


class DataRuleAdd(BaseView):
    
    def get(self,request):
        menu_id = request.GET.get("menu_id")
        _o = data_rule()
        return render(request, 'system_datarule_form.html',{"menu_id":menu_id,"method":"add","data_rule":_o})
    
    def post(self,request):
        data = {}
        menu_id = request.POST.get("menuId")
        name = request.POST.get('name')
        class_name = request.POST.get('class_name')
        field = request.POST.get('field')
        express = request.POST.get('express')
        value = request.POST.get('value')
        remarks = request.POST.get("remarks" )

        if name =='' or class_name=='' or field=='' or express=='' or value=='':
            data["success"]=False
            data["msg"]="Input Data Error!" 
            return JsonResponse(data,safe=False)

        _o = data_rule()
        _o.menu_id = menu_id
        _o.name = name
        _o.class_name = class_name
        _o.r_filed = field
        _o.r_express = express
        _o.r_value = value
        _o.remarks = remarks
        _s = DataRuleService()
                
        return _s.add_data_rule( _o)
            
        
        
class DataRuleView(BaseView):
    
    def get(self,request):
        id = request.GET.get("id")
        menu_id = request.GET.get("menu_id")

        print(id)
        if not id:
            return render(request, 'system_datarule_form.html', {"menu_id": menu_id, "method": "add"})

        else:
            _o = data_rule.objects.get(id=id)
            return render(request, 'system_datarule_form.html', {"data_rule": _o, "method": "edit"})
class DataRuleEdit(BaseView):
    def get(self,request):
        id = request.GET.get("id")
        menu_id = request.GET.get("menu_id")

        print(id)
        if not id:
            return render(request, 'system_datarule_form.html', {"menu_id": menu_id, "method": "add"})

        else:
            _o = data_rule.objects.get(id=id)
            return render(request, 'system_datarule_form.html',{"data_rule":_o,"method":"edit"})
    def post(self,request):
        data = {}
        id = request.POST.get("id")

        name = request.POST.get('name')
        class_name = request.POST.get('class_name')
        field = request.POST.get('field')
        express = request.POST.get('express')
        value = request.POST.get('value')
        remarks = request.POST.get("remarks")

        if name == '' or class_name == '' or field == '' or express == '' or value == '':
            data["success"] = False
            data["msg"] = "Input Data Error!"
            return JsonResponse(data, safe=False)

        _o = data_rule.objects.get(id = id)
        _o.name = name
        _o.class_name = class_name
        _o.r_filed = field
        _o.r_express = express
        _o.r_value = value
        _o.remarks = remarks


        _s = DataRuleService()
        return _s.upd_data_rule( _o)
       
    
        
            
#menu delete
class DataRuleDel(BaseView):
    
    def get(self,request):
        data = {}
        id=request.GET.get("id")
        data["success"]=True
        data["msg"]="Success" 
        _o = menu()
        _o.id = id
        _s = DataRuleService()
        
        return _s.del_data_rule( _o)


class DataRulePermissionView(BaseView):
    def get(self, request):
        roleId = request.GET.get('id')

        return render(request, 'system_datarule_permission.html', {'roleId': roleId})


class DataRulePersmissionTree(BaseView):
    def get(self, request):
        roleId = request.GET.get('roleId')
        print(roleId)
        o_list = menu.objects.filter(is_delete=0).order_by("sort")
        temp_list = []
        _st = State()
        _st.opened = True
        _tr = TreeInfo()
        _tr.id = 0
        _tr.name = 'Menu'
        _tr.text = 'Menu'
        _tr.parent = '#'
        _tr.state = _st
        temp_list.append(_tr)

        for _o in o_list:
            _tr = TreeInfo()
            _tr.id = _o.id
            _tr.name = _o.name
            _tr.text = _o.name
            _tr.parent = _o.parent_id



            temp_list.append(_tr)
        #query data rule
        _o_data_rule_list = data_rule.objects.filter()
        for _o in _o_data_rule_list:
            _tr = TreeInfo()
            _tr.id = _o.id
            _tr.name = _o.name
            _tr.text = _o.name
            _tr.parent = _o.menu_id
            _tr.type = '4'
            # query exists
            _o_role_data_rule_list = role_data_rule.objects.filter(role_id=roleId,data_rule_id=_o.id)
            if _o_role_data_rule_list.count() > 0:
                _st = State()
                _st.selected = True
                _tr.state = _st
            temp_list.append(_tr)
        _tr = TreeInfo()

        data = json.dumps(temp_list, default=_tr.conver_to_dict)

        # data = list(data)
        print(data)
        # data = [{"id": 1, "name": "\u516c\u53f8", "text": "\u516c\u53f8", "parent": "#", "state": {"opened": True}}, {"id": 2, "name": "\u8d22\u52a1\u90e8", "text": "\u8d22\u52a1\u90e8", "parent": "1", "state": {"opened": True}}]
        # data =[{"id":"1","remarks":"","createDate":"2013-05-27 08:00:00","updateDate":"2015-11-11 17:40:49","parentIds":"0,","name":"总公司","sort":10,"hasChildren":True,"code":"100000","type":"1","grade":"1","address":"","zipCode":"","master":"","phone":"","fax":"","email":"","useable":"1","parentId":"0"}]
        return HttpResponse(data)


class DataRulePersmissionSave(BaseView):

    def post(self, request):
        id = request.POST.get("id")
        dataRuleIds = request.POST.get("dataRuleIds")
        _s = DataRuleService()
        return _s.role_data_rule_save(id, dataRuleIds)
