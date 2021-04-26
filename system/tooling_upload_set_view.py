from django.shortcuts import render, HttpResponse
from django.http.response import JsonResponse

from tooling_form.models import setting, upload_error_msg
from utilslibrary.base.base import BaseView
from django.db.models import Q
from system.service.tooling_upload_set_service import ImportSetService, ErrorMsgService


# tooling_upload_set_list
class tooling_upload_set_list(BaseView):

    def get(self, request):
        if request.method == 'GET':
            return render(request, 'system_tooling_upload_set.html')

    def post(self, request):
        """根据查询条件获取 mdt_info"""
        if request.method == 'POST':
            # user_id = request.session.get(Constant.SESSION_CURRENT_USER_ID)
            super().post(request)
            q = Q()
            q.connector = 'and'
            q.children.append(('is_delete', 0))

            setting_list = setting.objects.filter(q).order_by('sort').values()[self.startIndex: self.endIndex]

            data = {}
            data['total'] = setting.objects.filter(q).count()
            data['rows'] = list(setting_list)

            print(data['total'], data['rows'])

            return JsonResponse(data, safe=False)


# tooling_upload_set_view
class tooling_upload_set_view(BaseView):

    def get(self, request):
        id = request.GET.get("id")
        if not id:
            return render(request, 'system_tooling_upload_set_form.html')
        else:
            _o = setting.objects.get(id=id)
            return render(request, 'system_tooling_upload_set_form.html', {"upload_set": _o})


# tooling_upload_set_add
class tooling_upload_set_add(BaseView):

    def get(self, request):
        _o = setting()
        return render(request, 'system_tooling_upload_set_form.html', {"upload_set": _o, "method": "add"})

    def post(self, request):
        data = {}

        # setting
        m_sort = request.POST.get('sort')
        m_sheet_no = request.POST.get('sheet_no')
        m_sheet_name = request.POST.get('sheet_name')
        m_column_no = request.POST.get('column_no')
        m_column_name = request.POST.get('column_name')
        m_required_field = request.POST.get('required_field')
        m_row = request.POST.get('row')
        m_column = request.POST.get('column')
        m_parent_id = request.POST.get('parent_id')
        m_regex = request.POST.get('regex')
        m_regex_no = request.POST.get('regex_no')
        m_enable = request.POST.get('enable')

        _o = setting()
        _o.sort = m_sort
        _o.sheet_no = m_sheet_no
        _o.sheet_name = m_sheet_name
        _o.column_no = m_column_no
        _o.column_name = m_column_name
        _o.required_field = m_required_field
        _o.row = m_row
        _o.column = m_column
        _o.parent_id = m_parent_id
        _o.regex = m_regex
        _o.regex_no = m_regex_no
        _o.enable = m_enable

        _s = ImportSetService()

        return _s.add_setting(_o)


# tooling_upload_set_edit
class tooling_upload_set_edit(BaseView):

    def get(self, request):
        id = request.GET.get("id")
        if not id:
            return render(request, 'system_tooling_upload_set_form.html', {"method": "edit"})
        else:
            _o = setting.objects.get(id=id)
            return render(request, 'system_tooling_upload_set_form.html', {"upload_set": _o, "method": "edit"})

    def post(self, request):
        data = {}

        # setting
        m_id = request.POST.get('id')
        m_sort = request.POST.get('sort')
        m_sheet_no = request.POST.get('sheet_no')
        m_sheet_name = request.POST.get('sheet_name')
        m_column_no = request.POST.get('column_no')
        m_column_name = request.POST.get('column_name')
        m_required_field = request.POST.get('required_field')
        m_row = request.POST.get('row')
        m_column = request.POST.get('column')
        m_parent_id = request.POST.get('parent_id')
        m_regex = request.POST.get('regex')
        m_regex_no = request.POST.get('regex_no')
        m_enable = request.POST.get('enable')

        _o = setting.objects.get(id=m_id)

        _o.sheet_no = m_sheet_no
        _o.sort = m_sort
        _o.sheet_name = m_sheet_name
        _o.column_no = m_column_no
        _o.column_name = m_column_name
        _o.required_field = m_required_field
        _o.row = m_row
        _o.column = m_column
        _o.parent_id = m_parent_id
        _o.regex = m_regex
        _o.regex_no = m_regex_no
        _o.enable = m_enable

        _s = ImportSetService()

        return _s.upd_setting(_o)


# tooling_upload_set_del
class tooling_upload_set_del(BaseView):

    def get(self, request):
        data = {}
        ids = request.GET.get("ids")
        data["success"] = True
        data["msg"] = "Success"

        _o = setting()

        _o.id = ids
        _s = ImportSetService()

        return _s.del_setting(_o)


# tooling_upload_set_select
class tooling_upload_set_select(BaseView):
    def get(self, request):
        return render(request, 'system_tooling_upload_set_user_select.html')


# error msg list
class tooling_upload_error_msg_list(BaseView):

    def post(self, request):
        # super().post(request)
        data = {}

        q = Q()
        q.connector = 'and'
        q.children.append(('is_delete', 0))
        l_id = request.POST.get('id')
        print('l_id = ', l_id)
        if id:
            q.children.append(('set_id', l_id))

        error_msg_list = upload_error_msg.objects.filter(q).values()

        data["total"] = error_msg_list.count()
        data["rows"] = list(error_msg_list)
        # data["mdt_id"] = l_id
        print(data)

        return JsonResponse(data, safe=False)


# error msg view
class tooling_upload_error_msg_view(BaseView):

    def get(self, request):
        id = request.GET.get("id")
        if not id:
            return render(request, 'system_tooling_upload_error_msg_form.html')
        else:
            _o = upload_error_msg.objects.get(id=id)
            set_id = _o.set_id
            return render(request, 'system_tooling_upload_error_msg_form.html', {"error_msg": _o, "set_id": set_id})


# error msg add
class tooling_upload_error_msg_add(BaseView):

    def get(self, request):
        _o = upload_error_msg()
        set_id = request.GET.get('set_id')
        print('set_id', set_id)
        return render(request, 'system_tooling_upload_error_msg_form.html',
                      {"method": "add", "error_msg": _o, "set_id": set_id})

    def post(self, request):
        data = {}

        m_set_id = request.POST.get('set_id')
        m_message = request.POST.get('message')
        m_remark = request.POST.get('remark')

        print('123123', m_set_id, m_message, m_remark)

        _o = upload_error_msg()

        _o.set_id = m_set_id
        _o.message = m_message
        _o.remark = m_remark

        _s = ErrorMsgService()

        return _s.add_error_msg(_o)


# error msg edit
class tooling_upload_error_msg_edit(BaseView):

    def get(self, request):
        id = request.GET.get("id")
        if not id:
            return render(request, 'system_tooling_upload_error_msg_form.html', {"method": "edit"})
        else:
            _o = upload_error_msg.objects.get(id=id)
            set_id = _o.set_id
            print('set_id', set_id)
            return render(request, 'system_tooling_upload_error_msg_form.html',
                          {"error_msg": _o, "method": "edit", "set_id": set_id})

    def post(self, request):
        data = {}

        m_id = request.POST.get('id')
        m_set_id = request.POST.get('set_id')
        m_message = request.POST.get('message')
        m_remark = request.POST.get('remark')

        # update data
        _o = upload_error_msg.objects.get(id=m_id)

        _o.id = m_id
        _o.set_id = m_set_id
        _o.message = m_message
        _o.remark = m_remark

        _s = ErrorMsgService()

        return _s.upd_error_msg(_o)


# error msg del
class tooling_upload_error_msg_del(BaseView):

    def get(self, request):
        data = {}
        ids = request.GET.get("ids")
        data["success"] = True
        data["msg"] = "Success"

        _o = upload_error_msg()

        _o.id = ids
        _s = ErrorMsgService()

        return _s.del_error_msg(_o)
