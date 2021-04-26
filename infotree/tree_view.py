# # -*- coding: utf-8 -*-
# # Create your views here.
#
import re
import collections
from django.shortcuts import render
from django.http.response import JsonResponse

from tooling_form.service.tooling_service import switch
from utilslibrary.base.base import BaseView
from django.db.models import Q
from infotree.service.tree_service import tree_service, tree_option_service
from infotree.models import tree, tree_option, unreleased_info


# Tree List
class tree_list(BaseView):

    def get(self, request):
        if request.method == 'GET':
            return render(request, 'info_tree/tree/infotree_tree_list.html')

    def post(self, request):
        if request.method == 'POST':
            super().post(request)
            q = Q()
            q.connector = 'and'
            q.children.append(('is_delete', 0))

            _o = tree.objects.filter(q).order_by('id').values()[self.startIndex: self.endIndex]

            data = {'total': tree.objects.filter(q).count(), 'rows': list(_o)}

            return JsonResponse(data, safe=False)


# Tree View
class tree_view(BaseView):

    def get(self, request):
        id = request.GET.get("id")
        if not id:
            return render(request, 'info_tree/tree/infotree_tree_form.html')
        else:
            _o = tree.objects.get(id=id)
            return render(request, 'info_tree/tree/infotree_tree_form.html', {"tree": _o})


# Tree Add
class tree_add(BaseView):

    def get(self, request):
        _o = tree()
        return render(request, 'info_tree/tree/infotree_tree_form.html', {"method": "add", "tree": _o})

    def post(self, request):
        data = {}

        name = request.POST.get('name')
        description = request.POST.get('description')

        _o = tree()

        _o.name = name
        _o.description = description

        _s = tree_service()

        return _s.add_tree(_o)


# Tree Edit
class tree_edit(BaseView):

    def get(self, request):
        id = request.GET.get("id")
        if not id:
            return render(request, 'info_tree/tree/infotree_tree_form.html', {"method": "edit"})
        else:
            _o = tree.objects.get(id=id)
            return render(request, 'info_tree/tree/infotree_tree_form.html', {"method": "edit", "tree": _o})

    def post(self, request):

        id = request.POST.get('id')
        name = request.POST.get('name')
        description = request.POST.get('description')

        _o = tree.objects.get(id=id)

        _o.name = name
        _o.description = description

        _s = tree_service()

        return _s.upd_tree(_o)


# Tree Del
class tree_del(BaseView):

    def get(self, request):
        ids = request.GET.get("ids")

        _o = tree()
        _o.id = ids

        _s = tree_service()

        return _s.del_tree(_o)


# Tree Option List
class tree_option_list(BaseView):

    def post(self, request):
        if request.method == 'POST':
            super().post(request)

            id = request.POST.get('id')
            q = Q()
            q.connector = 'and'
            q.children.append(('is_delete', 0))

            if id:
                q.children.append(('tree_id', id))

            _o = tree_option.objects.filter(q).order_by('-id').values()[self.startIndex: self.endIndex]

            data = {'total': tree_option.objects.filter(q).count(), 'rows': list(_o)}

            return JsonResponse(data, safe=False)


# Tree Option View
class tree_option_view(BaseView):

    def get(self, request):
        id = request.GET.get("id")
        if not id:
            return render(request, 'info_tree/tree/infotree_tree_option_form.html')
        else:
            _o = tree_option.objects.get(id=id)
            return render(request, 'info_tree/tree/infotree_tree_option_form.html', {"tree_option": _o})


# Tree Option Add
class tree_option_add(BaseView):

    def get(self, request):
        tree_id = request.GET.get('set_id')
        _o = tree_option()
        return render(request, 'info_tree/tree/infotree_tree_option_form.html', {"method": "add",
                                                                                 "tree_option": _o,
                                                                                 "tree_id": tree_id})

    def post(self, request):
        data = {}

        tree_id = request.POST.get('tree_id')
        sort = request.POST.get('sort')
        value = request.POST.get('value')

        _tree = tree.objects.get(id=tree_id)
        name_list = ['Grade', 'Pattern_density']
        if _tree.name in name_list:
            check_res = check_value(_tree.name, value)
            if not check_res[0]:
                return JsonResponse(check_res[1], safe=False)

        sql = "select * from infotree_tree_option " \
              "where binary value = '" + value + "' and is_delete = 0 and tree_id = '" + tree_id + "'"
        tree_option_c = tree_option.objects.raw(sql)

        if tree_option_c.__len__() != 0:
            data["success"] = False
            data["msg"] = "'" + value + "' already exists"
            return JsonResponse(data, safe=False)

        _o = tree_option()

        _o.tree_id = tree_id
        _o.sort = sort
        _o.value = value

        _s = tree_option_service()

        return _s.add_tree_option(_o)


# Tree Option Edit
class tree_option_edit(BaseView):

    def get(self, request):
        id = request.GET.get("id")
        if not id:
            return render(request, 'info_tree/tree/infotree_tree_option_form.html', {"method": "edit"})
        else:
            _o = tree_option.objects.get(id=id)
            return render(request, 'info_tree/tree/infotree_tree_option_form.html',
                          {"method": "edit", "tree_option": _o})

    def post(self, request):
        data = {}
        id = request.POST.get('id')
        tree_id = request.POST.get('tree_id')
        sort = request.POST.get('sort')
        old_value = request.POST.get('old_value')
        value = request.POST.get('value')

        _tree = tree.objects.get(id=tree_id)
        name_list = ['Grade', 'Pattern_density', 'Layer']
        if _tree.name in name_list:
            check_res = check_value(_tree.name, value)
            if not check_res[0]:
                return JsonResponse(check_res[1], safe=False)

        # 判斷值是否存在
        if not (old_value == value):
            sql = "select * from infotree_tree_option " \
                  "where binary value = '" + value + "' and is_delete = 0 and tree_id = '" + tree_id + "'"
            tree_option_c = tree_option.objects.raw(sql)

            if tree_option_c.__len__() != 0:
                data["success"] = False
                data["msg"] = "'" + value + "' already exists"
                return JsonResponse(data, safe=False)

        _o = tree_option.objects.get(id=id)

        # 判斷是否可以修改，info_tree_data是否還有關聯資料
        _tree = tree.objects.get(id=_o.tree_id)

        # unreleased
        unreleased_sql = "select * from infotree_unreleased_info " \
                         "where binary " + _tree.name.lower() + " = '" + _o.value + "' and is_delete = 0"
        unreleased_data = unreleased_info.objects.raw(unreleased_sql)

        # unreleased_alta
        unreleased_alta_sql = "select * from infotree_unreleased_info_alta " \
                              "where binary " + _tree.name.lower() + " = '" + _o.value + "' and is_delete = 0"
        unreleased_alta_data = unreleased_info.objects.raw(unreleased_alta_sql)

        # release
        released_sql = "select * from infotree_released_info " \
                       "where binary " + _tree.name.lower() + " = '" + _o.value + "' and is_delete = 0"
        released_data = unreleased_info.objects.raw(released_sql)

        # released_alta
        released_alta_sql = "select * from infotree_released_info_alta " \
                            "where binary " + _tree.name.lower() + " = '" + _o.value + "' and is_delete = 0"
        released_alta_data = unreleased_info.objects.raw(released_alta_sql)

        if unreleased_data.__len__() != 0 and unreleased_alta_data.__len__() != 0 and \
                released_data.__len__() != 0 and released_alta_data.__len__() != 0:
            data["success"] = False
            data["msg"] = "There are data in maintain, please do not delete !"
            return JsonResponse(data, safe=False)

        _o.tree_id = tree_id
        _o.sort = sort
        _o.value = value

        _s = tree_option_service()

        return _s.upd_tree_option(_o)


# Tree Option Del
class tree_option_del(BaseView):

    def get(self, request):
        ids = request.GET.get("ids")

        _o = tree()
        _o.id = ids

        _s = tree_option_service()

        return _s.del_tree_option(_o)


def check_value(name, value):
    data = {}
    for case in switch(name):
        if case('Grade'):
            value_list = value.split(',')
            pattern = re.compile(r"^[A-Z]$")
            for v in value_list:
                m = pattern.match(v)
                if not m:
                    data["success"] = False
                    data["msg"] = "format error"
                    return False, data
                elif collections.Counter(value_list)[v] != 1:
                    data["success"] = False
                    data["msg"] = "'" + v + "' repeat "
                    return False, data
            break

        if case('Pattern_density'):
            value_list = value.split('-')
            if len(value_list) != 2:
                data["success"] = False
                data["msg"] = "format error"
                return False, data

            pattern = re.compile(r"^(0|[1-9][0-9]?|100)$")
            m = pattern.match(value_list[0])
            m_1 = pattern.match(value_list[1])
            left_val = value_list[0]
            right_val = value_list[1]
            if not (m and m_1):
                data["success"] = False
                data["msg"] = "value out of range or format error"
                return False, data
            elif float(left_val) > float(right_val):
                data["success"] = False
                data["msg"] = "Left and right are equal or left is less than right"
                return False, data
            break

        # if case('Layer'):
        #     value_list = value.split(',')
        #     pattern = re.compile(r"^[1-9][0-9|x]{2}$|^[1-9][0-9][A-Z]$|^[*]$")
        #     for v in value_list:
        #         m = pattern.match(v)
        #         if not m:
        #             data["success"] = False
        #             data["msg"] = "format error"
        #             return False, data
        #         elif collections.Counter(value_list)[v] != 1:
        #             data["success"] = False
        #             data["msg"] = "'" + v + "' repeat "
        #             return False, data
        #     break
    return True, 'success'
