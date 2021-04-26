from django.http import JsonResponse
from django.shortcuts import render

from catalog.models import tool_maintain, group_maintain, tool_name_route
from catalog.service.group_maintain_service import group_maintain_service
from catalog.service.tool_maintain_service import tool_maintain_service
from catalog.service.tool_name_route_service import tool_name_route_service
from maintain.models import maintain_change_log
from utilslibrary.base.base import BaseView
from utilslibrary.utils.common_utils import getCurrentSessionName


class ToolView(BaseView):
    def get(self, request):
        return render(request, 'catalog/tool_maintain.html')
    def post(self,request):
        super().post(request)
        query_set = tool_maintain.objects.filter(is_delete=0)
        query_list = list(query_set.values())[self.startIndex: self.endIndex]
        data = {'total': query_set.count(), 'rows': query_list}
        return JsonResponse(data, safe=False)


class GroupView(BaseView):
    def get(self, request):
        return render(request, 'catalog/tool_maintain.html')
    def post(self,request):
        super().post(request)
        group_id = request.POST.get('group_id')
        query_set = group_maintain.objects.filter(is_delete=0, group_id=group_id)
        query_list = list(query_set.values())[self.startIndex: self.endIndex]
        data = {'total': query_set.count(), 'rows': query_list}
        return JsonResponse(data, safe=False)


class ToolMaintainAdd(BaseView):
    def get(self, request):
        return render(request, 'catalog/tool_maintain_form.html', {'method': 'add', 't_m': ''})
    def post(self, request):
        tool_id = request.POST.get('tool_id')
        group_name = request.POST.get('group_name')
        exptool = request.POST.get('exptool')
        ip = request.POST.get('ip')
        account = request.POST.get('account')
        password = request.POST.get('password')
        tool_type = request.POST.get('tool_type')
        path = request.POST.get('path')
        t_m = tool_maintain()
        t_m.tool_id = tool_id
        t_m.group_name = group_name
        t_m.exptool = exptool
        t_m.ip = ip
        t_m.account = account
        t_m.password = password
        t_m.tool_type = tool_type
        t_m.path = path
        new_data = {}
        new_data['tool_id'] = tool_id
        new_data['group_name'] = group_name
        new_data['exptool'] = exptool
        new_data['ip'] = ip
        new_data['account'] = account
        new_data['password'] = password
        new_data['tool_type'] = tool_type
        new_data['path'] = path
        c_l = maintain_change_log()
        c_l.table = 'Tool Maintain'
        c_l.operation = 'Add'
        c_l.change_user = getCurrentSessionName(request)
        c_l.new_data = new_data
        return tool_maintain_service().add_tool_maintain(t_m, c_l)


class ToolMaintainEdit(BaseView):
    def get(self, request):
        id = request.GET.get('id')
        t_m = tool_maintain.objects.get(id=id)
        return render(request, 'catalog/tool_maintain_form.html', {'method': 'edit', 't_m': t_m})
    def post(self, request):
        id = request.POST.get('tool_maintain_id')
        tool_id = request.POST.get('tool_id')
        group_name = request.POST.get('group_name')
        exptool = request.POST.get('exptool')
        ip = request.POST.get('ip')
        account = request.POST.get('account')
        password = request.POST.get('password')
        tool_type = request.POST.get('tool_type')
        path = request.POST.get('path')
        t_m = tool_maintain.objects.get(id=id)
        c_l = maintain_change_log()
        old_data = {}
        old_data['tool_id'] = t_m.tool_id
        old_data['group_name'] = t_m.group_name
        old_data['exptool'] = t_m.exptool
        old_data['ip'] = t_m.ip
        old_data['account'] = t_m.account
        old_data['password'] = t_m.password
        old_data['tool_type'] = t_m.tool_type
        old_data['path'] = t_m.path
        t_m.tool_id = tool_id
        t_m.group_name = group_name
        t_m.exptool = exptool
        t_m.ip = ip
        t_m.account = account
        t_m.password = password
        t_m.tool_type = tool_type
        t_m.path = path
        new_data = {}
        new_data['tool_id'] = tool_id
        new_data['group_name'] = group_name
        new_data['exptool'] = exptool
        new_data['ip'] = ip
        new_data['account'] = account
        new_data['password'] = password
        new_data['tool_type'] = tool_type
        new_data['path'] = path
        c_l.data_id = id
        c_l.operation = 'Edit'
        c_l.old_data = old_data
        c_l.new_data = new_data
        c_l.table = 'Tool Maintain'
        c_l.change_user = getCurrentSessionName(request)
        c_l.save()
        return tool_maintain_service().updt_tool_maintain(t_m)


class ToolMaintainDel(BaseView):

    def get(self, request):
        ids = request.GET.get("ids")

        t_m = tool_maintain()
        t_m.id = ids

        return tool_maintain_service().del_tool_maintain(t_m, request)


class GroupAdd(BaseView):
    def get(self, request):
        group_id = request.GET.get('group_id')
        return render(request, 'catalog/group_form.html', {'method': 'add', 't_m': '', 'group_id': group_id})
    def post(self,request):
        group_id = request.POST.get('group_id')
        tool = request.POST.get('tool')
        tool_name = request.POST.get('tool_name')
        info_tree_name = request.POST.get('info_tree_name')
        g_m = group_maintain()
        g_m.tool = tool
        g_m.group_id = group_id
        g_m.tool_name = tool_name
        g_m.info_tree_name = info_tree_name
        return group_maintain_service().add_group_maintain(g_m)


class GroupEdit(BaseView):
    def get(self, request):
        id = request.GET.get('id')
        group_id = request.GET.get('group_id')
        g_m = group_maintain.objects.get(id=id)
        return render(request, 'catalog/group_form.html', {'method': 'edit', 't_m': g_m, 'group_id': group_id})
    def post(self,request):
        group_id = request.POST.get('group_id')
        id = request.POST.get('tool_id')
        tool = request.POST.get('tool')
        tool_name = request.POST.get('tool_name')
        info_tree_name = request.POST.get('info_tree_name')
        g_m = group_maintain.objects.get(id=id)
        g_m.tool = tool
        g_m.group_id = group_id
        g_m.tool_name = tool_name
        g_m.info_tree_name = info_tree_name
        return group_maintain_service().updt_group_maintain(g_m)


class GroupDel(BaseView):
    def get(self, request):
        id = request.GET.get('id')
        g_m = group_maintain()
        g_m.id = id
        return group_maintain_service().del_group_maintain(g_m)


class ToolRouteList(BaseView):
    def get(self, request):
        return render(request, 'catalog/tool_name_route.html')
    def post(self, request):
        super().post(request)
        query_set = tool_name_route.objects.filter(is_delete=0)
        query_list = list(query_set.values())[self.startIndex: self.endIndex]
        data = {'total': query_set.count(), 'rows': query_list}
        return JsonResponse(data, safe=False)


class ToolRouteAdd(BaseView):
    def get(self, request):
        return render(request, 'catalog/tool_route_form.html', {'t_m': '', 'method': 'add'})
    def post(self, request):
        catalog_tool_id = request.POST.get('catalog_tool_id')
        writer_name = request.POST.get('writer_name')
        info_tree_name = request.POST.get('info_tree_name')
        machine_type = request.POST.get('machine_type')
        t_m = tool_name_route()
        t_m.catalog_tool_id = catalog_tool_id
        t_m.writer_name = writer_name
        t_m.info_tree_name = info_tree_name
        t_m.machine_type = machine_type
        new_data = {}
        new_data['catalog_tool_id'] = catalog_tool_id
        new_data['writer_name'] = writer_name
        new_data['info_tree_name'] = info_tree_name
        new_data['machine_type'] = machine_type
        c_l = maintain_change_log()
        c_l.operation = 'Add'
        c_l.table = 'Tool Name Route'
        c_l.change_user = getCurrentSessionName(request)
        c_l.new_data = new_data
        return tool_name_route_service().add_tool_route(t_m, c_l)


class ToolRouteEdit(BaseView):
    def get(self, request):
        id = request.GET.get('id')
        t_m = tool_name_route.objects.get(id=id)
        return render(request, 'catalog/tool_route_form.html', {'t_m': t_m, 'method': 'edit'})
    def post(self, request):
        catalog_tool_id = request.POST.get('catalog_tool_id')
        writer_name = request.POST.get('writer_name')
        info_tree_name = request.POST.get('info_tree_name')
        machine_type = request.POST.get('machine_type')
        id = request.POST.get('id')
        t_m = tool_name_route.objects.get(pk=id)
        old_data = {}
        old_data['catalog_tool_id'] = t_m.catalog_tool_id
        old_data['writer_name'] = t_m.writer_name
        old_data['info_tree_name'] = t_m.info_tree_name
        old_data['machine_type'] = t_m.machine_type
        t_m.catalog_tool_id = catalog_tool_id
        t_m.writer_name = writer_name
        t_m.info_tree_name = info_tree_name
        t_m.machine_type = machine_type
        new_data = {}
        new_data['catalog_tool_id'] = catalog_tool_id
        new_data['writer_name'] = writer_name
        new_data['info_tree_name'] = info_tree_name
        new_data['machine_type'] = machine_type
        c_l = maintain_change_log()
        c_l.table = 'Tool Name Route'
        c_l.data_id = id
        c_l.operation = 'Edit'
        c_l.change_user = getCurrentSessionName(request)
        c_l.new_data = new_data
        c_l.old_data = old_data
        c_l.save()
        return tool_name_route_service().upt_tool_route(t_m)


class ToolRouteDel(BaseView):
    def get(self, request):
        ids = request.GET.get('ids')
        t_m = tool_name_route()
        t_m.id = ids
        return tool_name_route_service().del_tool_route(t_m, request)