# # -*- coding: utf-8 -*-
# # Create your views here.
from django.shortcuts import render, HttpResponse
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from utilslibrary.base.base import BaseView
from django.db.models import Q
from infotree.models import info_tree_template, info_tree_template_option, tree, tree_option
from infotree.service.template_service import template_service, template_option_service


@csrf_exempt
def template_dict(request):
    tree_id_list = tree.objects.filter(is_delete=0).values()

    result_dict = {}
    for tree_id in tree_id_list:
        labels = tree_option.objects.filter(tree_id=tree_id['id'], is_delete=0).order_by('sort').values('value')
        label_list = []
        for label in labels:
            label_list.append(label['value'])
        result_dict[tree_id['name']] = label_list
    print(result_dict)
    return JsonResponse(data=result_dict, safe=False)


# Template List
class template_list(BaseView):

    def get(self, request):
        if request.method == 'GET':
            return render(request, 'info_tree/template/infotree_template_list.html')

    def post(self, request):
        """根据查询条件获取 mdt_info"""
        if request.method == 'POST':
            super().post(request)

            cs_command = request.POST.get('s_cs_command')

            q = Q()
            q.connector = 'and'
            q.children.append(('is_delete', 0))

            if cs_command:
                q.children.append(('cs_command__contains', cs_command))

            temp_list = info_tree_template.objects.filter(q).order_by('id').values()[
                        self.startIndex: self.endIndex]

            data = {'total': info_tree_template.objects.filter(q).count(), 'rows': list(temp_list)}

            return JsonResponse(data, safe=False)


# Template View
class template_view(BaseView):

    def get(self, request):
        id = request.GET.get("id")
        if not id:
            return render(request, 'info_tree/template/infotree_template_form.html')
        else:
            _o = info_tree_template.objects.get(id=id)
            return render(request, 'info_tree/template/infotree_template_form.html', {"temp": _o})


# Template Add
class template_add(BaseView):

    def get(self, request):
        _o = info_tree_template()
        return render(request, 'info_tree/template/infotree_template_form.html', {"method": "add", "temp": _o})

    def post(self, request):

        machine_type = request.POST.get('machine_type')
        level = request.POST.get('level')
        type = request.POST.get('type')
        cs_command = request.POST.get('cs_command')
        data_type = request.POST.get('data_type')
        # limit_type, 0:TEXT(不限制) 1:下拉選單 2:範圍數值
        limit_type = request.POST.get('limit_type')
        limit = request.POST.get('limit')

        if machine_type and level and type and cs_command and data_type and limit_type and limit:
            _o = info_tree_template()
            _o.machine_type = machine_type
            _o.level = level
            _o.type = type
            _o.cs_command = cs_command
            _o.data_type = data_type
            _o.limit_type = limit_type
            _o.limit = limit

            _s = template_service()

            return _s.add_template(_o)
        else:
            data = {"success": False, "msg": "Failed"}
            return JsonResponse(data, safe=False)


# Template Edit
class template_edit(BaseView):

    def get(self, request):
        id = request.GET.get("id")
        if not id:
            return render(request, 'info_tree/template/infotree_template_form.html', {"range": "edit"})
        else:
            _o = info_tree_template.objects.get(id=id)
            return render(request, 'info_tree/template/infotree_template_form.html', {"method": "edit", "temp": _o})

    def post(self, request):

        id = request.POST.get('id')
        machine_type = request.POST.get('machine_type')
        level = request.POST.get('level')
        type = request.POST.get('type')
        cs_command = request.POST.get('cs_command')
        data_type = request.POST.get('data_type')
        limit_type = request.POST.get('limit_type')
        limit = request.POST.get('limit')

        if id and machine_type and type and cs_command and data_type and limit_type:
            _o = info_tree_template.objects.get(id=id)
            _o.machine_type = machine_type
            _o.level = level
            _o.type = type
            _o.cs_command = cs_command
            _o.data_type = data_type
            _o.limit = limit
            _o.limit_type = limit_type

            _s = template_service()

            return _s.upd_template(_o)
        else:
            data = {"success": False, "msg": "Failed"}
            return JsonResponse(data, safe=False)


# Template Del
class template_del(BaseView):

    def get(self, request):
        data = {}
        ids = request.GET.get("ids")
        data["success"] = True
        data["msg"] = "Success"

        _o = info_tree_template()
        _o.id = ids

        _s = template_service()

        return _s.del_template(_o)


# Template Option List
class template_option_list(BaseView):

    def post(self, request):
        if request.method == 'POST':
            super().post(request)

            temp_id = request.POST.get('id')

            q = Q()
            q.connector = 'and'
            q.children.append(('is_delete', 0))

            if temp_id:
                q.children.append(('temp_id', temp_id))

            option_list = info_tree_template_option.objects.filter(q).order_by('-sort').values()[
                          self.startIndex: self.endIndex]

            data = {}
            data['total'] = info_tree_template_option.objects.filter(q).count()
            data['rows'] = list(option_list)

            return JsonResponse(data, safe=False)


# Template Option View
class template_option_view(BaseView):

    def get(self, request):
        id = request.GET.get("id")
        if not id:
            return render(request, 'info_tree/template/infotree_template_option_form.html')
        else:
            _o = info_tree_template_option.objects.get(id=id)
            limit_type = request.GET.get('limit_type')
            return render(request, 'info_tree/template/infotree_template_option_form.html', {"temp_option": _o,
                                                                                    "limit_type": limit_type})


# Template Option Add
class template_option_add(BaseView):

    def get(self, request):
        temp_id = request.GET.get('set_id')
        limit_type = request.GET.get('limit_type')
        _o = info_tree_template_option()
        return render(request, 'info_tree/template/infotree_template_option_form.html', {"method": "add",
                                                                                "temp_option": _o,
                                                                                "temp_id": temp_id,
                                                                                "limit_type": limit_type})

    def post(self, request):
        data = {}

        temp_id = request.POST.get('temp_id')
        sort = request.POST.get('sort')
        option = request.POST.get('option')
        start = request.POST.get('start')
        end = request.POST.get('end')
        remark = request.POST.get('remark')

        _o = info_tree_template_option()

        _o.temp_id = temp_id
        _o.sort = sort
        _o.option = option
        _o.start = start
        _o.end = end
        _o.remark = remark
        _s = template_option_service()

        return _s.add_template_option(_o)


# Template Option Edit
class template_option_edit(BaseView):

    def get(self, request):
        id = request.GET.get("id")
        if not id:
            return render(request, 'info_tree/template/infotree_template_option_form.html', {"method": "edit"})
        else:
            _o = info_tree_template_option.objects.get(id=id)
            limit_type = request.GET.get('limit_type')
            return render(request, 'info_tree/template/infotree_template_option_form.html', {"method": "edit",
                                                                                    "temp_option": _o,
                                                                                    "limit_type": limit_type})

    def post(self, request):

        id = request.POST.get('id')
        temp_id = request.POST.get('temp_id')
        sort = request.POST.get('sort')
        option = request.POST.get('option')
        start = request.POST.get('start')
        end = request.POST.get('end')
        remark = request.POST.get('remark')

        # update data
        _o = info_tree_template_option.objects.get(id=id)

        _o.temp_id = temp_id
        _o.sort = sort
        _o.option = option
        _o.start = start
        _o.end = end
        _o.remark = remark

        _s = template_option_service()

        return _s.upd_template_option(_o)


# Template Option Del
class template_option_del(BaseView):

    def get(self, request):
        data = {}
        ids = request.GET.get("ids")
        data["success"] = True
        data["msg"] = "Success"

        _o = info_tree_template_option()
        _o.id = ids

        _s = template_option_service()

        return _s.del_template_option(_o)
