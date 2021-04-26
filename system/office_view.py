# --coding:utf-8 --
"""office and auth manage

"""
from django.shortcuts import render

from system.models import office
from django.http.response import HttpResponseRedirect, JsonResponse
from utilslibrary.system_constant import Constant
from django.http import HttpResponse
from django.db.models import F, Q
from django.contrib.auth.hashers import make_password, check_password

from django.core import serializers
import json
from utilslibrary.decorators.auth_decorators import AuthCheck
from django.template.context_processors import request
from system.service.office_service import OfficeService

from utilslibrary.base.base import BaseView
from utilslibrary.models.tree_model import TreeInfo, State
from system.model.office_model import OfficeInfo


# Create your views here.

class OfficeList(BaseView):

    def get(self, request):
        return render(request, 'system_office_list.html')


class OfficeAdd(BaseView):

    def get(self, request):
        _o = office()
        return render(request, 'system_office_form.html', {"method": "add", "office": _o})

    def post(self, request):
        data = {}

        id = request.POST.get('id')
        parent_id = request.POST.get('parent_id', '')
        name = request.POST.get('name', '')
        code = request.POST.get('code', '')
        type = request.POST.get('type', '')
        useable = request.POST.get('useable', '')
        remarks = request.POST.get('remarks', '')

        if name == '':
            data["success"] = False
            data["msg"] = "Input Data Error!"
            return JsonResponse(data, safe=False)

            # insert data

        # check the record has exist
        _o = office.objects.filter(name=name, is_delete=0)
        if _o:
            data["success"] = False
            data["msg"] = "office name exists!"
            return JsonResponse(data, safe=False)
        _o = office()
        _o.parent_id = parent_id
        _o.name = name
        _o.code = code
        _o.type = type
        _o.useable = useable
        _o.remarks = remarks
        _s = OfficeService()

        return _s.add_office(_o)


class OfficeView(BaseView):

    def get(self, request):
        id = request.GET.get("id")
        print(id)
        if not id:
            return render(request, 'system_office_form.html')
        else:
            _o = office.objects.get(id=id)
            # query parent name
            if _o.parent_id:
                tmp_o_list = office.objects.filter(id=_o.parent_id)
                if tmp_o_list and tmp_o_list.count() > 0:
                    tmp_o = tmp_o_list[0]
                    _o.parent_name = tmp_o.name
            return render(request, 'system_office_form.html', {"office": _o})


class OfficeEdit(BaseView):

    def get(self, request):
        id = request.GET.get("id")
        print(id)
        if not id:
            return render(request, 'system_office_form.html', {"method": "edit"})
        else:
            _o = office.objects.get(id=id)
            # query parent name
            if _o.parent_id:
                tmp_o_list = office.objects.filter(id=_o.parent_id)
                if tmp_o_list and tmp_o_list.count() > 0:
                    tmp_o = tmp_o_list[0]
                    _o.parent_name = tmp_o.name
            return render(request, 'system_office_form.html', {"office": _o, "method": "edit"})

    def post(self, request):
        data = {}

        id = request.POST.get('id')
        parent_id = request.POST.get('parent_id', '')
        name = request.POST.get('name', '')
        code = request.POST.get('code', '')
        type = request.POST.get('type', '')
        useable = request.POST.get('useable', '')
        remarks = request.POST.get('remarks', '')

        if name == '':
            data["success"] = False
            data["msg"] = "Input Data Error!"
            return JsonResponse(data, safe=False)

        if id:
            # update data
            _o = office.objects.get(id=id)
            _o.parent_id = parent_id
            _o.name = name
            _o.code = code
            _o.type = type
            _o.useable = useable
            _o.remarks = remarks

            _s = OfficeService()
            return _s.upd_office(_o)


# office delete
class OfficeDel(BaseView):

    def get(self, request):
        data = {}
        ids = request.GET.get("id")
        data["success"] = True
        data["msg"] = "Success"
        _o = office()
        _o.id = ids
        _s = OfficeService()

        return _s.del_office(_o)

    # check login name


class OfficeCheckName(BaseView):

    def get(self, request):
        ln = request.GET.get('loginName')
        oln = request.GET.get('oldLoginName')
        if ln == oln:
            return HttpResponse('true')
        _o_list = office.objects.filter(loginname=ln, is_delete=0)
        if _o_list:
            return HttpResponse('false')
        else:
            return HttpResponse('true')


class OfficeGetChildren(BaseView):

    def get(self, request):
        parentId = request.GET.get('parentId')
        if parentId == '-1':
            parentId = 0
        o_list = office.objects.filter(parent_id=parentId, is_delete=0).annotate(parentId=F('parent_id')).values(
            'parentId', 'id', 'name', 'sort', 'type', 'code', 'useable')
        data = list(o_list)
        return JsonResponse(data, safe=False)


class OfficeTreeData(BaseView):

    def get(self, request):

        # _o_list = office.objects.filter(is_delete=0).annotate(parent=F('parent_id'),text=F('name')).values('id','parent','name','text','type')
        o_list = office.objects.filter(is_delete=0)
        temp_list = []
        _st = State()
        _st.opened = True

        for _o in o_list:
            _tr = TreeInfo()
            _tr.id = _o.id
            _tr.name = _o.name
            _tr.text = _o.name
            if _o.parent_id == '0':
                _tr.parent = '#'
            else:
                _tr.parent = _o.parent_id
            _tr.state = _st
            temp_list.append(_tr)
        data = json.dumps(temp_list, default=_tr.conver_to_dict)

        # data = list(data)
        print(data)
        # data = [{"id": 1, "name": "\u516c\u53f8", "text": "\u516c\u53f8", "parent": "#", "state": {"opened": True}}, {"id": 2, "name": "\u8d22\u52a1\u90e8", "text": "\u8d22\u52a1\u90e8", "parent": "1", "state": {"opened": True}}]
        # data =[{"id":"1","remarks":"","createDate":"2013-05-27 08:00:00","updateDate":"2015-11-11 17:40:49","parentIds":"0,","name":"总公司","sort":10,"hasChildren":True,"code":"100000","type":"1","grade":"1","address":"","zipCode":"","master":"","phone":"","fax":"","email":"","useable":"1","parentId":"0"}]
        return HttpResponse(data)
