# -*- coding: utf-8 -*-
from django.db.models import Q
from django.http.response import JsonResponse
from django.shortcuts import render
from infotree.models import maintain_table, maintain_table_mdt, unreleased_info
from utilslibrary.base.base import BaseView
from infotree.service.maintain_table_service import maintain_table_service, maintain_table_mdt_service
from django.views.decorators.csrf import csrf_exempt


class maintain_check_list(BaseView):

    def get(self, request):
        if request.method == 'GET':
            return render(request, 'info_tree/unreleased/infotree_unreleased_check_list.html')

    def post(self, request):
        if request.method == 'POST':
            data = {}

            super().post(request)
            q = Q()
            q.connector = 'and'
            q.children.append(('is_delete', 0))
            q.children.append(('lock', 1))

            tool = request.POST.get('s_tool')
            node = request.POST.get('s_node')
            tone = request.POST.get('s_tone')
            blank = request.POST.get('s_blank')
            grade = request.POST.get('s_grade')
            pattern_density = request.POST.get('s_pattern_density')
            layer = request.POST.get('s_layer')
            sort_name = request.POST.get('sort_name')
            sort_order = request.POST.get('sort_order')

            if sort_order == 'asc':
                order_by = sort_name
            elif sort_order == 'desc':
                order_by = '-' + sort_name
            else:
                order_by = 'id'

            if tool:
                q.children.append(('tool', tool))

            if node:
                q.children.append(('node', node))

            if tone:
                q.children.append(('tone', tone))

            if blank:
                q.children.append(('blank', blank))

            if grade:
                q.children.append(('grade', grade))

            if pattern_density:
                q.children.append(('pattern_density', pattern_density))

            if layer:
                q.children.append(('layer', layer))

            m_list = unreleased_info.objects.filter(q).order_by(order_by).values('tool', 'node', 'tone', 'blank',
                                                                                'grade', 'pattern_density',
                                                                                'layer').distinct()[
                     self.startIndex: self.endIndex]

            print(m_list.query)

            data['total'] = unreleased_info.objects.filter(q).order_by(order_by).values('tool', 'node', 'tone', 'blank',
                                                                                       'grade', 'pattern_density',
                                                                                       'layer').distinct().count()
            data['rows'] = list(m_list)

            return JsonResponse(data, safe=False)


class maintain_table_view(BaseView):

    def get(self, request):
        id = request.GET.get("id")
        if not id:
            return render(request, 'info_tree/infotree_maintain_table_form.html')
        else:
            _o = maintain_table.objects.get(id=id)
            return render(request, 'info_tree/infotree_maintain_table_form.html', {"maintain_table": _o})


class maintain_table_edit(BaseView):
    def get(self, request):
        id = request.GET.get("id")
        if not id:
            return render(request, 'info_tree/infotree_maintain_table_form.html', {"method": "edit"})
        else:
            _o = maintain_table.objects.get(id=id)
            return render(request, 'info_tree/infotree_maintain_table_form.html',
                          {"method": "edit", "maintain_table": _o})

    def post(self, request):
        id = request.POST.get('id')
        mdt = request.POST.get('mdt')
        remark = request.POST.get('remark')

        _o = maintain_table.objects.get(id=id)
        _o.mdt = mdt
        _o.remark = remark

        _s = maintain_table_service()

        return _s.upd_maintain_table(_o)
