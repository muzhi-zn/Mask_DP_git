# -*- coding: utf-8 -*-

# Create your views here.

from django.shortcuts import render, HttpResponse
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from catalog.models import tool_name_route, tool_maintain
from maintain.models import maintain_change_log
from utilslibrary.base.base import BaseView
from utilslibrary.system_constant import Constant
from machine.models import machine_basic, machine_script_templates, writer_mapping
from system.models import role, template
from machine.service.machine_service import MachineService, WriterMappingService
from django.db.models import Q

from utilslibrary.utils.common_utils import getCurrentSessionName
from utilslibrary.utils.date_utils import getDateStr


class machine_manage_list(BaseView):

    def get(self, request):
        if request.method == 'GET':
            return render(request, 'machine_manage_list.html')

    def post(self, request):
        """根据查询条件获取 machine_basic"""
        if request.method == 'POST':
            # user_id = request.session.get(Constant.SESSION_CURRENT_USER_ID)
            super().post(request)
            q = Q()
            q.connector = 'and'
            q.children.append(('is_delete', 0))

            m_name = request.POST.get('s_machine_name')
            print(m_name)
            if m_name:
                q.children.append(('machine_name__contains', m_name))

            machine_list = machine_basic.objects.filter(q).order_by('-id').values()[self.startIndex: self.endIndex]

            data = {}
            data['total'] = machine_basic.objects.filter(q).count()
            data['rows'] = list(machine_list)

            print(data['total'], data['rows'])

            return JsonResponse(data, safe=False)


@csrf_exempt
def get_machine_options(request):
    """获取机器选项"""
    machine_list = tool_maintain.objects.filter(is_delete=0).values('exptool').distinct()
    return JsonResponse({'options': list(machine_list)}, safe=False)


class machine_manage_view(BaseView):

    def get(self, request):
        id = request.GET.get("id")
        print('view id = ' + id)
        if not id:
            return render(request, 'machine_manage_form.html')
        else:
            _o = machine_basic.objects.get(id=id)
            _template_list = template.objects.filter(is_delete=0).values('template_type')

            return render(request, 'machine_manage_form.html', {"machine": _o, "template": _template_list})


class machine_manage_add(BaseView):

    def get(self, request):
        _o = machine_basic()
        return render(request, 'machine_manage_form.html', {"method": "add", "machine": _o})

    def post(self, request):
        data = {}
        # Machine
        m_name = request.POST.get('machine_name')
        m_ip = request.POST.get('machine_ip')
        m_type = request.POST.get('machine_type')
        m_account = request.POST.get('machine_account')
        m_password = request.POST.get('machine_password')
        m_remark = request.POST.get('machine_remark')
        # FTP
        f_ip = request.POST.get('ftp_ip')
        f_path = request.POST.get('ftp_path')
        f_account = request.POST.get('ftp_account')
        f_password = request.POST.get('ftp_password')

        # insert data
        # check the record has exist

        # _o = machine_basic.objects.filter(name=name, is_delete=0)
        # if _o:
        #     data["success"] = False
        #     data["msg"] = "role name exists!"
        #     return JsonResponse(data, safe=False)

        _o = machine_basic()

        _o.machine_name = m_name
        _o.machine_ip = m_ip
        _o.machine_type = m_type
        _o.machine_account = m_account
        _o.machine_password = m_password
        _o.machine_remark = m_remark
        _o.ftp_ip = f_ip
        _o.ftp_path = f_path
        _o.ftp_account = f_account
        _o.ftp_password = f_password

        _s = MachineService()

        return _s.add_machine(_o)


class machine_manage_edit(BaseView):

    def get(self, request):
        id = request.GET.get("id")
        if not id:
            return render(request, 'machine_manage_form.html', {"method": "edit"})
        else:
            _o = machine_basic.objects.get(id=id)
            return render(request, 'machine_manage_form.html', {"machine": _o, "method": "edit"})

    def post(self, request):
        data = {}
        # Machine
        m_id = request.POST.get('id')
        m_name = request.POST.get('machine_name','')
        m_ip = request.POST.get('machine_ip','')
        m_type = request.POST.get('machine_type','')
        m_account = request.POST.get('machine_account','')
        m_password = request.POST.get('machine_password','')
        m_remark = request.POST.get('machine_remark','')
        # FTP
        f_ip = request.POST.get('ftp_ip','')
        f_path = request.POST.get('ftp_path','')
        f_account = request.POST.get('ftp_account','')
        f_password = request.POST.get('ftp_password','')

        # update data
        _o = machine_basic.objects.get(id=m_id)

        _o.machine_name = m_name
        _o.machine_ip = m_ip
        _o.machine_type = m_type
        _o.machine_account = m_account
        _o.machine_password = m_password
        _o.machine_remark = m_remark
        _o.ftp_ip = f_ip
        _o.ftp_path = f_path
        _o.ftp_account = f_account
        _o.ftp_password = f_password

        _s = MachineService()

        print('update')

        return _s.upd_machine(_o)


# machine delete
class machine_manage_del(BaseView):

    def get(self, request):
        data = {}
        ids = request.GET.get("ids")
        data["success"] = True
        data["msg"] = "Success"
        _o = machine_basic()
        _o.id = ids
        _s = MachineService()

        return _s.del_machine(_o)


# check login name
class RoleCheckName(BaseView):

    def get(self, request):
        oldname = request.GET.get('oldName')
        name = request.GET.get('name')

        print('oldname = ' + oldname, 'name = ' + name)
        if name == oldname:
            return HttpResponse('true')
        _o_list = role.objects.filter(name=name, is_delete=0)
        if _o_list:
            return HttpResponse('false')
        else:
            return HttpResponse('true')


class WriterMappingList(BaseView):

    def get(self, request):
        return render(request, 'tooling_form/writer_mapping_list.html')

    def post(self, request):
        q = Q()
        q.connector = 'and'
        q.children.append(('is_delete', 0))
        product = request.POST.get('product')
        if product:
            q.children.append(('product', product))
        layer = request.POST.get('layerName')
        if layer:
            q.children.append(('layer_name', layer))
        wm_list = writer_mapping.objects.values().order_by('-id').filter(q)
        data = {'total': writer_mapping.objects.filter(q).count(), 'rows': list(wm_list)}
        return JsonResponse(data, safe=True)


class WriterMappingAdd(BaseView):

    def get(self, request):
        return render(request, 'tooling_form/writer_mapping_form.html', {'method': 'add', 'w_m': writer_mapping()})

    def post(self, request):
        wm = writer_mapping()
        wm.seq = request.POST.get('seq')
        wm.customer = request.POST.get('customer')
        wm.design_rule = request.POST.get('design_rule')
        wm.product = request.POST.get('product')
        wm.layer_name = request.POST.get('layer_name')
        wm.product_type = request.POST.get('product_type')
        wm.grade_from = request.POST.get('grade_from')
        wm.grade_to = request.POST.get('grade_to')
        wm.mask_type = request.POST.get('mask_type')
        wm.tone = request.POST.get('tone')
        # wm.machine_id = request.POST.get('machine_id')
        wm.exp_tool = request.POST.get('exp_tool')
        wm.comment = request.POST.get('comment')
        wm.book_user_id = request.session.get(Constant.SESSION_CURRENT_USER_ID)
        wm.book_user_name = request.session.get(Constant.SESSION_CURRENT_USER_LOGINNAME)
        wm.book_time = getDateStr()
        wm.info_tree_tool_id = request.POST.get('info_tree_tool_id')
        wm.catalog_tool_id = request.POST.get('catalog_tool_id')
        c_l = maintain_change_log()
        new_data = {}
        new_data['seq'] = request.POST.get('seq')
        new_data['customer'] = request.POST.get('customer')
        new_data['design_rule'] = request.POST.get('design_rule')
        new_data['product'] = request.POST.get('product')
        new_data['layer_name'] = request.POST.get('layer_name')
        new_data['product_type'] = request.POST.get('product_type')
        new_data['grade_from'] = request.POST.get('grade_from')
        new_data['grade_to'] = request.POST.get('grade_to')
        new_data['mask_type'] = request.POST.get('mask_type')
        new_data['tone'] = request.POST.get('tone')
        # new_data['machine_id'] = request.POST.get('machine_id')
        new_data['exp_tool'] = request.POST.get('exp_tool')
        new_data['comment'] = request.POST.get('comment')
        new_data['book_user_id'] = request.session.get(Constant.SESSION_CURRENT_USER_ID)
        new_data['book_user_name'] = request.session.get(Constant.SESSION_CURRENT_USER_LOGINNAME)
        new_data['book_time'] = getDateStr()
        new_data['info_tree_tool_id'] = request.POST.get('info_tree_tool_id')
        new_data['catalog_tool_id'] = request.POST.get('catalog_tool_id')
        c_l.operation = 'Add'
        c_l.change_user = getCurrentSessionName(request)
        c_l.table = 'Writer Mapping'
        c_l.new_data = new_data
        return WriterMappingService().add_writer_mapping(wm, c_l)


class WriterMappingEdit(BaseView):

    def get(self, request):
        id = request.GET.get('id')
        if id:
            w_m = writer_mapping.objects.get(pk=id)
            return render(request, 'tooling_form/writer_mapping_form.html', {'method': 'edit', 'w_m': w_m})
        else:
            w_m = writer_mapping()
            return render(request, 'tooling_form/writer_mapping_form.html', {'method': 'edit', 'w_m': w_m})

    def post(self, request):
        id = request.POST.get('id')
        wm = writer_mapping.objects.get(pk=id)
        old_data = {}
        old_data['seq'] = wm.seq
        old_data['customer'] = wm.customer
        old_data['design_rule'] = wm.design_rule
        old_data['product'] = wm.product
        old_data['layer_name'] = wm.layer_name
        old_data['product_type'] = wm.product_type
        old_data['grade_from'] = wm.grade_from
        old_data['grade_to'] = wm.grade_to
        old_data['mask_type'] = wm.mask_type
        old_data['tone'] = wm.tone
        old_data['machine_id'] = wm.machine_id
        old_data['exp_tool'] = wm.exp_tool
        old_data['comment'] = wm.comment
        old_data['book_user_id'] = wm.book_user_id
        old_data['book_user_name'] = wm.book_user_name
        old_data['book_time'] = wm.book_time
        old_data['info_tree_tool_id'] = wm.info_tree_tool_id
        old_data['catalog_tool_id'] = wm.catalog_tool_id
        wm.seq = request.POST.get('seq')
        wm.customer = request.POST.get('customer')
        wm.design_rule = request.POST.get('design_rule')
        wm.product = request.POST.get('product')
        wm.layer_name = request.POST.get('layer_name')
        wm.product_type = request.POST.get('product_type')
        wm.grade_from = request.POST.get('grade_from')
        wm.grade_to = request.POST.get('grade_to')
        wm.mask_type = request.POST.get('mask_type')
        wm.tone = request.POST.get('tone')
        # wm.machine_id = request.POST.get('machine_id')
        wm.exp_tool = request.POST.get('exp_tool')
        wm.comment = request.POST.get('comment')
        wm.book_user_id = request.session.get(Constant.SESSION_CURRENT_USER_ID)
        wm.book_user_name = request.session.get(Constant.SESSION_CURRENT_USER_LOGINNAME)
        wm.book_time = getDateStr()
        wm.info_tree_tool_id = request.POST.get('info_tree_tool_id')
        wm.catalog_tool_id = request.POST.get('catalog_tool_id')
        c_l = maintain_change_log()
        new_data = {}
        new_data['seq'] = request.POST.get('seq')
        new_data['customer'] = request.POST.get('customer')
        new_data['design_rule'] = request.POST.get('design_rule')
        new_data['product'] = request.POST.get('product')
        new_data['layer_name'] = request.POST.get('layer_name')
        new_data['product_type'] = request.POST.get('product_type')
        new_data['grade_from'] = request.POST.get('grade_from')
        new_data['grade_to'] = request.POST.get('grade_to')
        new_data['mask_type'] = request.POST.get('mask_type')
        new_data['tone'] = request.POST.get('tone')
        # new_data['machine_id'] = request.POST.get('machine_id')
        new_data['exp_tool'] = request.POST.get('exp_tool')
        new_data['comment'] = request.POST.get('comment')
        new_data['book_user_id'] = request.session.get(Constant.SESSION_CURRENT_USER_ID)
        new_data['book_user_name'] = request.session.get(Constant.SESSION_CURRENT_USER_LOGINNAME)
        new_data['book_time'] = getDateStr()
        new_data['info_tree_tool_id'] = request.POST.get('info_tree_tool_id')
        new_data['catalog_tool_id'] = request.POST.get('catalog_tool_id')
        c_l.operation = 'Edit'
        c_l.change_user = getCurrentSessionName(request)
        c_l.table = 'Writer Mapping'
        c_l.data_id = id
        c_l.new_data = new_data
        c_l.old_data = old_data
        c_l.save()
        return WriterMappingService().add_writer_mapping(wm, c_l)


class WriterMappingDel(BaseView):

    def get(self, request):
        ids = request.GET.get('ids')
        wm = writer_mapping()
        wm.id = ids
        return WriterMappingService().del_writer_mapping(wm, request)


class WriterMappingView(BaseView):

    def get(self, request):
        id = request.GET.get('id')
        if id:
            w_m = writer_mapping.objects.get(pk=id)
            return render(request, 'tooling_form/writer_mapping_form.html', {'method': 'view', 'w_m': w_m})
        else:
            w_m = writer_mapping()
            return render(request, 'tooling_form/writer_mapping_form.html', {'method': 'view', 'w_m': w_m})


class DispatchEdit(BaseView):
    """修改lot的dispatch信息"""
    pass

@csrf_exempt
def gen_info_tree_tool_id(request):
    writer_name = request.POST.get('writer_name')
    query_set = tool_name_route.objects.filter(writer_name=writer_name, is_delete=0)
    info_tree_tool_id_list = []
    for query in query_set:
        if query.info_tree_name not in info_tree_tool_id_list:
            info_tree_tool_id_list.append(query.info_tree_name)
    return JsonResponse({'success': True, 'info_tree': info_tree_tool_id_list}, safe=False)

@csrf_exempt
def gen_catalog_tool_id(reqeust):
    info_tree_tool_id = reqeust.POST.get('info_tree_tool_id')
    query_set = tool_name_route.objects.filter(info_tree_name=info_tree_tool_id, is_delete=0)
    if query_set:
        catalog_tool_id = query_set.first().catalog_tool_id
    else:
        return JsonResponse({'success': False}, safe=False)
    return JsonResponse({'success': True, 'tool_id': catalog_tool_id}, safe=False)