#--coding:utf-8 --
"""user and auth manage

"""
from django.shortcuts import render

from system.models import menu
from django.http.response import HttpResponseRedirect, JsonResponse
from utilslibrary.system_constant import Constant
from django.http import HttpResponse
from django.db.models import F,Q

from django.core import serializers
import json
from utilslibrary.decorators.auth_decorators import AuthCheck
from django.template.context_processors import request
from system.service.menu_service import MenuService
from utilslibrary.models.tree_model import TreeInfo,State
from utilslibrary.models.menu_model import MenuInfo
from utilslibrary.base.base import BaseView


class MenuList(BaseView):
    
    def get(self,request):
        return render(request, 'system_menu_list.html')
    
    
    
class MenuAdd(BaseView):
    
    def get(self,request):
        parent_id = request.GET.get("parent_id")
        
        if parent_id:
            _o = MenuInfo()
            _o.parent_id = parent_id
            _o_parent = menu.objects.get(id=parent_id)
            _o.parent_name = _o_parent.name
        else:
            _o = MenuInfo()
            _o.parent_id = 0
            _o.parent_name = "Menu"    
        return render(request, 'system_menu_form.html',{"menu":_o,"method":"add"})
    
    def post(self,request):
        data = {}
        id = request.POST.get("id")
        
        parentid = request.POST.get('parentid')
        parentids = ''
        if parentid == '':
            parentid = '0'

        if parentid!='0':
            #查询上级菜单的parent_id,用户刷新用
            _o = menu.objects.get(id=parentid)
            if _o.type==2:
                data["success"]=False
                data["msg"]="Button cannot add sub menu!" 
                return JsonResponse(data,safe=False)
            parentids = _o.parent_ids
            
        parentids = parentids+parentid+','
        name = request.POST.get('name','')
        href = request.POST.get('href','')
        base_href = request.POST.get('base_href','')
        type = request.POST.get('type','')
        icon = request.POST.get('icon','')
        isShow = request.POST.get('isShow','')
        remarks = request.POST.get('remarks','')
        
        if name =='' :
            data["success"]=False
            data["msg"]="Input Data Error!" 
            return JsonResponse(data,safe=False)
        _o = menu()
        _o.parent_id = parentid
        _o.parent_ids = parentids
            
        _o.has_children = "false"
        _o.icon = icon
        _o.name = name
        _o.href = href
        _o.base_href = base_href
        _o.is_show = isShow
        _o.type = type
            
        _s = MenuService()
                
        return _s.add_menu( _o)
            
        
        
class MenuView(BaseView):
    
    def get(self,request):
        id = request.GET.get("id")
        print(id)
        if not id:
            return render(request, 'system_menu_form.html')
        else:
            _o = menu.objects.get(id=id)
            parent_list = menu.objects.filter(id=_o.parent_id)
            if parent_list.count()>0:
                _o_parent = parent_list[0]
                _o.parent_name = _o_parent.name
            else:
                _o.parent_name = 'Menu'    
            return render(request, 'system_menu_form.html',{"menu":_o})
class MenuEdit(BaseView):
    def get(self,request):
        id = request.GET.get("id")
        print(id)
        if not id:
            _o = MenuInfo()
            _o.parent_id = 0
            _o.parent_name = "Menu"
            return render(request, 'system_menu_form.html',{"menu":_o,"method":"edit"})
        else:
            _o = menu.objects.get(id=id)
            parent_list = menu.objects.filter(id=_o.parent_id)
            if parent_list.count()>0:
                _o_parent = parent_list[0]
                _o.parent_name = _o_parent.name
            else:
                _o.parent_name = 'Menu'
            return render(request, 'system_menu_form.html',{"menu":_o,"method":"edit"})
    def post(self,request):
        data = {}
        id = request.POST.get("id")
        
        parentid = request.POST.get('parentid')
        parentids = ''
        if parentid == '':
            parentid = '0'

        if parentid!='0':
            #查询上级菜单的parent_id,用户刷新用
            _o = menu.objects.get(id=parentid)
            parentids = _o.parent_ids
        parentids = parentids+parentid+','    
        name = request.POST.get('name','')
        href = request.POST.get('href','')
        base_href = request.POST.get('base_href','')
        type = request.POST.get('type','')
        icon = request.POST.get('icon','')
        isShow = request.POST.get('isShow','')
        remarks = request.POST.get('remarks','')
        
        if name =='' :
            data["success"]=False
            data["msg"]="Input Data Error!" 
            return JsonResponse(data,safe=False)
        if id :
            #如果是修改菜单类型为按钮
            if type == "2":
                #查询本菜单是否有子菜单，有子菜单不允许修改
                _o_list = menu.objects.filter(parent_id=id)
                if _o_list.count()>0:
                    data["success"]=False
                    data["msg"]="Has sub menu,type cannot be modified!" 
                    return JsonResponse(data,safe=False)
            _o = menu.objects.get(id=id)
            _o.parent_id = parentid
            _o.parent_ids = parentids
            #set haschildren =true when has children menu
            _o_menu_list = menu.objects.filter(parent_id=id,type=1)
            if _o_menu_list.count()==0:
                hasChildren = 'false'
            else:
                hasChildren = 'true'
            _o.has_children = hasChildren
            _o.icon = icon
            _o.name = name
            _o.href = href
            _o.base_href = base_href
            _o.is_show = isShow
            _o.type = type
            _s = MenuService()
            return _s.upd_menu( _o)
       
    
        
            
#menu delete
class MenuDel(BaseView):
    
    def get(self,request):
        data = {}
        id=request.GET.get("id")
        data["success"]=True
        data["msg"]="Success" 
        _o = menu()
        _o.id = id
        _s = MenuService()
        
        return _s.del_menu( _o)  
    
#generate add ,list,view,edit,del menu
class GenerateSubMenu(BaseView):
    
    def get(self,request):
        data = {}
        id=request.GET.get("id")
        data["success"]=True
        data["msg"]="Success" 
        _o = menu()
        _o.id = id
        _s = MenuService()
        
        return _s.generate_sub_menu( _o)  

class MenuTree(BaseView):
    
    def get(self,request):
        o_list = menu.objects.filter(is_delete=0,type=1).order_by("sort")
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
            _tr.state = _st
            temp_list.append(_tr)
        _tr = TreeInfo()
                
        data=json.dumps(temp_list, default=_tr.conver_to_dict)
        
        #data = list(data)
        print(data)
        #data = [{"id": 1, "name": "\u516c\u53f8", "text": "\u516c\u53f8", "parent": "#", "state": {"opened": True}}, {"id": 2, "name": "\u8d22\u52a1\u90e8", "text": "\u8d22\u52a1\u90e8", "parent": "1", "state": {"opened": True}}]
        #data =[{"id":"1","remarks":"","createDate":"2013-05-27 08:00:00","updateDate":"2015-11-11 17:40:49","parentIds":"0,","name":"总公司","sort":10,"hasChildren":True,"code":"100000","type":"1","grade":"1","address":"","zipCode":"","master":"","phone":"","fax":"","email":"","useable":"1","parentId":"0"}]
        return HttpResponse(data)

class GetChildren(BaseView):
    
    def get(self,request):
        parentId = request.GET.get('parentId')
        #添加查询条件，设置为逻辑与查询
        q = Q()
        q.connector = 'and '
        q.children.append(('is_delete',0))
        if parentId=='-1':
            q.children.append(('parent_id',0))
        else:
            q.children.append(('parent_id',parentId))
            
        #组装JSON数据
        data = {}
        
        temp_list = []
        o_list = menu.objects.filter(q).order_by("sort")
        for _o in o_list:
            _o_i = MenuInfo()
            _o_i.id = _o.id
            _o_i.name = _o.name
            _o_i.href = _o.href
            _o_i.base_href = _o.base_href
            _o_i.sort = _o.sort
            _o_i.type = _o.type
            _o_i.parentId = _o.parent_id
            _o_i.parentIds = _o.parent_ids
            _o_i.isShow =_o.is_show
            _o_list = menu.objects.filter(parent_id=_o.id)
            if _o_list.count()>0:
            #if _o.type==1:
                _o_i.hasChildren = True
            else:
                _o_i.hasChildren = False    
            _o_i.icon = _o.icon
            temp_list.append(_o_i)
        _o_i = MenuInfo()    
        data=json.dumps(temp_list, default=_o_i.conver_to_dict)
        data = json.loads(data)
        return JsonResponse(data,safe=False)

class MenuIconSelect(BaseView):
    
    def get(self,request):
        return render(request, 'system_menu_icon.html')     

class MenuSort(BaseView):
    
    def get(self,request):
        id1 = request.GET.get("id1")           
        sort1 = request.GET.get("sort1")           
        id2 = request.GET.get("id2")           
        sort2 = request.GET.get("sort2")
        _s = MenuService()
        return _s.sort(id1, sort1, id2, sort2)
                   