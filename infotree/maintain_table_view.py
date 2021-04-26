# -*- coding: utf-8 -*-
from django.db.models import Q
from django.http.response import JsonResponse
from django.shortcuts import render
from infotree.models import maintain_table, maintain_table_mdt
from utilslibrary.base.base import BaseView
from infotree.service.maintain_table_service import maintain_table_service, maintain_table_mdt_service
from django.views.decorators.csrf import csrf_exempt


class maintain_table_list(BaseView):

    def get(self, request):
        if request.method == 'GET':
            return render(request, 'info_tree/infotree_maintain_table_list.html')

    def post(self, request):
        if request.method == 'POST':
            data = {}

            super().post(request)
            q = Q()
            q.connector = 'and'
            q.children.append(('is_delete', 0))

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

            m_list = maintain_table.objects.filter(q).order_by(order_by).values()[
                     self.startIndex: self.endIndex]

            print(m_list.query)

            data['total'] = maintain_table.objects.filter(q).count()
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


@csrf_exempt
def get_row_count(request):
    if request.method == 'POST':
        id = request.POST.get('id')

        count = maintain_table_mdt.objects.filter(maintain_table_id=id, is_delete=0).count()
        print(count)
        data = {"count": count}
        return JsonResponse(data, safe=False)


class maintain_table_mdt_list(BaseView):
    def get(self, request):
        if request.method == 'GET':
            return render(request, 'info_tree/infotree_maintain_table_mdt_form.html')

    def post(self, request):
        if request.method == 'POST':
            data = {}

            super().post(request)
            q = Q()
            q.connector = 'and'
            q.children.append(('is_delete', 0))

            id = request.POST.get('id')

            if id:
                q.children.append(('maintain_table_id', id))

            m_list = maintain_table_mdt.objects.filter(q).order_by('id').values()[
                     self.startIndex: self.endIndex]

            print(m_list.query)

            data['total'] = maintain_table_mdt.objects.filter(q).count()
            data['rows'] = list(m_list)

            return JsonResponse(data, safe=False)


class maintain_table_mdt_view(BaseView):

    def get(self, request):
        if request.method == 'GET':
            id = request.GET.get('id')
            _o = maintain_table_mdt.objects.get(id=id, is_delete=0)
            return render(request, 'info_tree/infotree_maintain_table_mdt_form.html', {"mdt": _o})


class maintain_table_mdt_add(BaseView):

    def get(self, request):
        if request.method == 'GET':
            maintain_table_id = request.GET.get('maintain_table_id')
            _o = maintain_table_mdt()
            return render(request, 'info_tree/infotree_maintain_table_mdt_form.html',
                          {"method": "add", "mdt": _o, "maintain_table_id": maintain_table_id})

    def post(self, request):
        if request.method == 'POST':

            maintain_table_id = request.POST.get('maintain_table_id')
            cad_layer = request.POST.get('cad_layer')
            data_type = request.POST.get('data_type')
            writer_mdt = request.POST.get('writer_mdt')
            writer_dose = request.POST.get('writer_dose')

            if maintain_table_id and cad_layer and data_type and writer_mdt and writer_dose:

                _o = maintain_table_mdt()
                _o.maintain_table_id = maintain_table_id
                _o.cad_layer = cad_layer
                _o.data_type = data_type
                _o.writer_mdt = writer_mdt
                _o.writer_dose = writer_dose

                _s = maintain_table_mdt_service()

                return _s.add_mdt(_o)
            else:
                data = {"success": False, "msg": "Failed"}
                return JsonResponse(data, safe=False)


class maintain_table_mdt_edit(BaseView):

    def get(self, request):
        if request.method == 'GET':
            id = request.GET.get('id')
            _o = maintain_table_mdt.objects.get(id=id, is_delete=0)
            return render(request, 'info_tree/infotree_maintain_table_mdt_form.html', {"method": "edit", "mdt": _o})

    def post(self, request):
        if request.method == 'POST':

            id = request.POST.get('id')
            cad_layer = request.POST.get('cad_layer')
            data_type = request.POST.get('data_type')
            writer_mdt = request.POST.get('writer_mdt')
            writer_dose = request.POST.get('writer_dose')

            if id and cad_layer and data_type and writer_mdt and writer_dose:

                _o = maintain_table_mdt.objects.get(id=id)
                _o.cad_layer = cad_layer
                _o.data_type = data_type
                _o.writer_mdt = writer_mdt
                _o.writer_dose = writer_dose

                _s = maintain_table_mdt_service()

                return _s.upd_mdt(_o)
            else:
                data = {"success": False, "msg": "Failed"}
                return JsonResponse(data, safe=False)


class maintain_table_mdt_del(BaseView):

    def get(self, request):
        ids = request.GET.get("ids")

        _o = maintain_table_mdt()
        _o.id = ids

        _s = maintain_table_mdt_service()

        return _s.del_mdt(_o)
