# --coding:utf-8 --
"""role and auth manage

"""
from django.shortcuts import render

from system.models import role
from django.http.response import HttpResponseRedirect, JsonResponse
from utilslibrary.system_constant import Constant
from django.http import HttpResponse
from django.db.models import F, Q
from django.contrib.auth.hashers import make_password, check_password

from django.core import serializers
import json
from utilslibrary.decorators.auth_decorators import AuthCheck
from django.template.context_processors import request
from system.service.role_service import RoleService
from system.models import user_role, user
from utilslibrary.models.tree_model import TreeInfo, State
from system.models import menu, role_menu
from utilslibrary.base.base import BaseView


class RoleList(BaseView):

    def get(self, request):
        return render(request, 'system_role_list.html')

    def post(self, request):
        # -----------------------------
        # 需要获得翻页参数时添加
        # 代码中使用self.startIndex和self.endIndex获取相应范围的记录
        # ------------------------------
        # super().post(request)

        # 接收查询参数---与页面上要查询的条件匹配
        name = request.POST.get('name', '')
        """query by where1"""
        # 添加查询条件，设置为逻辑与查询
        q = Q()
        q.connector = 'and '
        q.children.append(('is_delete', 0))
        if name:
            q.children.append(('name__contains', name))
        # 执行查询
        u_list = role.objects.filter(q).order_by('-id').values()

        # 组装JSON数据
        data = {}
        # 设置总记录数
        data["total"] = role.objects.filter(q).count()
        data["rows"] = list(u_list)
        print(data)

        return JsonResponse(data, safe=False)


class RoleAdd(BaseView):

    def get(self, request):
        _o = role()
        return render(request, 'system_role_form.html', {"role": _o, "method": "add"})

    def post(self, request):
        data = {}

        id = request.POST.get('id')
        name = request.POST.get('name', '')
        useable = request.POST.get('useable', '0')
        remarks = request.POST.get('remarks', '')

        # insert data
        # check the record has exist
        _o = role.objects.filter(name=name, is_delete=0)
        if _o:
            data["success"] = False
            data["msg"] = "role name exists!"
            return JsonResponse(data, safe=False)
        _o = role()
        _o.name = name
        _o.remarks = remarks
        _o.useable = useable
        _s = RoleService()

        return _s.add_role(_o)


class RoleView(BaseView):

    def get(self, request):
        id = request.GET.get("id")
        print(id)
        if not id:
            return render(request, 'system_role_form.html')
        else:
            _o = role.objects.get(id=id)
            return render(request, 'system_role_form.html', {"role": _o})


class RoleEdit(BaseView):

    def get(self, request):
        id = request.GET.get("id")
        print(id)
        if not id:
            return render(request, 'system_role_form.html', {"method": "edit"})
        else:
            _o = role.objects.get(id=id)
            return render(request, 'system_role_form.html', {"role": _o, "method": "edit"})

    def post(self, request):
        data = {}

        id = request.POST.get('id')
        name = request.POST.get('name', '')
        useable = request.POST.get('useable', '0')
        remarks = request.POST.get('remarks', '')

        if name == '':
            data["success"] = False
            data["msg"] = "Input Data Error!"
            return JsonResponse(data, safe=False)

        if id:
            # update data
            _o = role.objects.get(id=id)
            _o.name = name
            _o.remarks = remarks
            _o.useable = useable

            _s = RoleService()
            return _s.upd_role(_o)


# role delete
class RoleDel(BaseView):

    def get(self, request):
        data = {}
        ids = request.GET.get("ids")
        data["success"] = True
        data["msg"] = "Success"
        _o = role()
        _o.id = ids
        _s = RoleService()

        return _s.del_role(_o)

    # check login name


class RoleCheckName(BaseView):

    def get(self, request):
        oldname = request.GET.get('oldName')
        name = request.GET.get('name')
        if name == oldname:
            return HttpResponse('true')
        _o_list = role.objects.filter(name=name, is_delete=0)
        if _o_list:
            return HttpResponse('false')
        else:
            return HttpResponse('true')


# role assign
class RoleUserList(BaseView):

    def post(self, request):
        super().post(request)
        # 组装JSON数据
        data = {}
        id = request.POST.get('roleId')

        q = Q()
        q.connector = 'and'
        q.children.append(('is_delete', 0))

        if id:
            user_id_list = user_role.objects.filter(role_id=id)
            id_list = []

            for user_id_o in user_id_list:
                id_list.append(user_id_o.user_id)

            q.children.append(('id__in', id_list))

            user_list = user.objects.filter(q).values()[self.startIndex:self.endIndex]

            # 设置总记录数
            data["total"] = user.objects.filter(q).values().count()
            data["rows"] = list(user_list)

        return JsonResponse(data, safe=False)


# user out role
class RoleUserOut(BaseView):

    def get(self, request):
        user_id = request.GET.get("userId")
        role_id = request.GET.get("roleId")
        user_role.objects.filter(user_id=user_id, role_id=role_id).delete()
        data = {}
        data["success"] = True
        data["msg"] = "Success"
        return JsonResponse(data, safe=False)


class RolePermissionView(BaseView):
    def get(self, request):
        roleId = request.GET.get('id')

        return render(request, 'system_role_permission.html', {'roleId': roleId})


class RolePersmissionTree(BaseView):
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

            # query exists
            _o_role_menu_list = role_menu.objects.filter(role_id=roleId, menu_id=_o.id, type=1)
            if _o_role_menu_list.count() > 0:
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


class RolePersmissionSave(BaseView):

    def post(self, request):
        id = request.POST.get("id")
        menuIds = request.POST.get("menuIds")
        _s = RoleService()
        return _s.assgin_role_menu(id, menuIds)
