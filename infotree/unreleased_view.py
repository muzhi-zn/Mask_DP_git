# -*- coding: utf-8 -*-
import json
import os
import time
import pandas as pd
import xlwt
from django.core.serializers.json import DjangoJSONEncoder
from django.db import connection
from django.db.models import Q
from django.http.response import JsonResponse, HttpResponse, FileResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from catalog.models import tool_name_route
from infotree.models import unreleased_info, info_tree_data_export_log, info_tree_data_import_temp, tree, tree_option, \
    maintain_table, release_check, unreleased_mdt
from infotree.models import tree, tree_option, info_tree_template, info_tree_template_option, cd_map, cec
from infotree.service.unreleased_service import unreleased_service
from tooling_form.service.tooling_service import switch
from utilslibrary.base.base import BaseView
from utilslibrary.system_constant import Constant
from django.db import transaction
from system.models import upload_info
from utilslibrary.utils.date_utils import getDateStr, getMilliSecond
from utilslibrary.utils.common_utils import getCurrentSessionID, getCurrentSessionName
from Mask_DP.settings import PROJECT_NAME


@csrf_exempt
def unreleased_dict(request):
    tree_id_list = tree.objects.filter(is_delete=0).values()

    result_dict = {}
    for tree_id in tree_id_list:
        labels = tree_option.objects.filter(tree_id=tree_id['id'], is_delete=0).order_by('sort').exclude(
            value='MS03').values('value')
        label_list = []
        for label in labels:
            label_list.append(label['value'])
        result_dict[tree_id['name']] = label_list
    print(result_dict)
    return JsonResponse(data=result_dict, safe=False)


@csrf_exempt
def unreleased_edit_dict(request):
    temp_id_list = info_tree_template.objects.filter(is_delete=0, limit_type=1).values()

    result_dict = {}
    for temp_id in temp_id_list:
        labels = info_tree_template_option.objects.filter(temp_id=temp_id['id']).order_by('id').values('option')
        label_list = []
        for label in labels:
            label_list.append(label['option'])
        result_dict[temp_id['cs_command']] = label_list
    print(result_dict)
    return JsonResponse(data=result_dict, safe=False)


class unreleased_list(BaseView):

    def get(self, request):
        if request.method == 'GET':
            return render(request, 'info_tree/unreleased/infotree_unreleased_list.html')

    def post(self, request):
        if request.method == 'POST':
            data = {}

            super().post(request)
            q = Q()
            q.connector = 'and'
            q.children.append(('is_delete', 0))

            customer = request.POST.get('s_customer')
            tool = request.POST.get('s_tool')
            node = request.POST.get('s_node')
            tone = request.POST.get('s_tone')
            blank = request.POST.get('s_blank')
            grade = request.POST.get('s_grade')
            pattern_density = request.POST.get('s_pattern_density')
            layer = request.POST.get('s_layer')

            if customer and tool and node and tone and blank and grade and pattern_density and layer:
                q.children.append(('customer', customer))
                q.children.append(('tool', tool))
                q.children.append(('node', node))
                q.children.append(('tone', tone))
                q.children.append(('blank', blank))
                q.children.append(('grade', grade))
                q.children.append(('pattern_density', pattern_density))
                q.children.append(('layer', layer))

                info_tree_datalist = unreleased_info.objects.filter(q).order_by('id').values()[
                                     self.startIndex: self.endIndex]

                data['total'] = unreleased_info.objects.filter(q).count()
                data['rows'] = list(info_tree_datalist)

                return JsonResponse(data, safe=False)
            else:
                data['total'] = 0
                data['rows'] = []

                return JsonResponse(data, safe=False)


class unreleased_view(BaseView):

    def get(self, request):
        id = request.GET.get("id")
        if not id:
            return render(request, 'info_tree/unreleased/infotree_unreleased_form.html')
        else:
            _o = unreleased_info.objects.get(id=id)
            return render(request, 'info_tree/unreleased/infotree_unreleased_form.html', {"tree_data": _o})


class unreleased_add(BaseView):
    def get(self, request):
        return render(request, 'info_tree/unreleased/infotree_unreleased_add_form.html', {"method": "add"})

    def post(self, request):
        customer = request.POST.get('customer')
        tool = request.POST.get('tool')
        node = request.POST.get('node')
        tone = request.POST.get('tone')
        blank = request.POST.get('blank')
        grade = request.POST.get('grade')
        pattern_density = request.POST.get('pattern_density')
        layer = request.POST.get('layer')

        grade_list = grade.split(',')
        layer_list = layer.split(',')

        if customer and tool and node and tone and blank and grade and pattern_density and layer:

            for _grade in grade_list:
                for _layer in layer_list:
                    data_count = unreleased_info.objects.filter(customer=customer, tool=tool, node=node, tone=tone,
                                                                blank=blank,
                                                                grade__contains=_grade, pattern_density=pattern_density,
                                                                layer__contains=_layer, is_delete=0).count()
                    print(_grade, _layer, data_count)
                    if data_count != 0:
                        data = {"success": False, "msg": "Data already exists"}
                        return JsonResponse(data, safe=False)

            _o = unreleased_info()

            _o.customer = customer
            _o.tool = tool
            _o.node = node
            _o.tone = tone
            _o.blank = blank
            _o.grade = grade
            _o.pattern_density = pattern_density
            _o.layer = layer

            _s = unreleased_service()

            return _s.add_info_tree_data(_o)

        else:
            data = {"success": False, "msg": "Value must not be empty"}
            return JsonResponse(data, safe=False)


class unreleased_copy(BaseView):
    def get(self, request):
        s_customer = request.GET.get('s_customer')
        s_tool = request.GET.get('s_tool')
        s_node = request.GET.get('s_node')
        s_tone = request.GET.get('s_tone')
        s_blank = request.GET.get('s_blank')
        s_grade = request.GET.get('s_grade')
        s_pattern_density = request.GET.get('s_pattern_density')
        s_layer = request.GET.get('s_layer')
        return render(request, 'info_tree/unreleased/infotree_unreleased_add_form.html', {"method": "copy",
                                                                                          "s_tool": s_tool,
                                                                                          "s_customer": s_customer,
                                                                                          "s_node": s_node,
                                                                                          "s_tone": s_tone,
                                                                                          "s_blank": s_blank,
                                                                                          "s_grade": s_grade,
                                                                                          "s_pattern_density": s_pattern_density,
                                                                                          "s_layer": s_layer})

    def post(self, request):
        s_tool = request.POST.get('s_tool')
        s_customer = request.POST.get('s_customer')
        s_node = request.POST.get('s_node')
        s_tone = request.POST.get('s_tone')
        s_blank = request.POST.get('s_blank')
        s_grade = request.POST.get('s_grade')
        s_pattern_density = request.POST.get('s_pattern_density')
        s_layer = request.POST.get('s_layer')
        unreleased_id = \
            unreleased_info.objects.filter(customer=s_customer, tool=s_tool, node=s_node, tone=s_tone, blank=s_blank,
                                           grade__contains=s_grade, pattern_density=s_pattern_density,
                                           layer__contains=s_layer, is_delete=0, type='MDT',
                                           value='Y').order_by('-id')[0].id
        unreleased_mdt_info = unreleased_mdt.objects.filter(unreleased_id=unreleased_id, is_delete=0).values()
        mdt_list = list(unreleased_mdt_info)

        customer = request.POST.get('customer')
        tool = request.POST.get('tool')
        node = request.POST.get('node')
        tone = request.POST.get('tone')
        blank = request.POST.get('blank')
        grade = request.POST.get('grade')
        pattern_density = request.POST.get('pattern_density')
        layer = request.POST.get('layer')

        grade_list = grade.split(',')
        layer_list = layer.split(',')

        if s_tool and s_node and s_tone and s_blank and s_grade and s_pattern_density and s_layer and tool and \
                node and tone and blank and grade and pattern_density and layer and s_customer and customer:

            for _grade in grade_list:
                for _layer in layer_list:
                    data_count = unreleased_info.objects.filter(customer=customer, tool=tool, node=node, tone=tone,
                                                                blank=blank,
                                                                grade__contains=_grade, pattern_density=pattern_density,
                                                                layer__contains=_layer, is_delete=0).count()
                    print(_grade, _layer, data_count)
                    if data_count != 0:
                        data = {"success": False, "msg": "Data already exists"}
                        return JsonResponse(data, safe=False)

            _o = unreleased_info()

            _o.id = [s_customer, s_tool, s_node, s_tone, s_blank, s_grade, s_pattern_density, s_layer]
            _o.customer = customer
            _o.tool = tool
            _o.node = node
            _o.tone = tone
            _o.blank = blank
            _o.grade = grade
            _o.pattern_density = pattern_density
            _o.layer = layer

            _s = unreleased_service()

            return _s.add_copy_info_tree_data(_o, mdt_list)
        else:
            data = {"success": False, "msg": "Value must not be empty"}
            return JsonResponse(data, safe=False)


class unreleased_edit(BaseView):
    def get(self, request):
        id = request.GET.get("id")
        if not id:
            return render(request, 'info_tree/unreleased/infotree_unreleased_form.html', {"method": "edit"})
        else:
            _o = unreleased_info.objects.get(id=id)
            return render(request, 'info_tree/unreleased/infotree_unreleased_form.html',
                          {"method": "edit", "tree_data": _o})

    def post(self, request):
        id = request.POST.get('id')
        limit_type = request.POST.get('limit_type')
        sel_value = request.POST.get('sel_value')
        input_value = request.POST.get('input_value')
        file_id = request.POST.get('file_id')

        if sel_value or input_value:
            _o = unreleased_info.objects.get(id=id)

            if limit_type == '1':
                _o.value = sel_value
            else:
                _o.value = input_value

            cs_command_list = ['CS_SYSTEM_PARAM',
                               'CS_MASK_PARAM',
                               'CS_SOAKING',
                               'CS_W_CH_SOAK',
                               'CS_GCD_MESH_SIZE',
                               'CS_KBR_PRX_MESH_SIZE',
                               'CS_KBR_SW',
                               'CS_FEC_MODE',
                               'CS_THETA1',
                               'CS_SIGMAF1',
                               'CS_LEC_MODE',
                               'CS_GAMMA1',
                               'CS_SIGMAL1',
                               'CS_TEC_MODE',
                               'CS_TEC_COEF_DC0',
                               'CS_GCDPARAM_CD1',
                               'CS_GCDPARAM_CD2',
                               'CS_GCDPARAM_CD3',
                               'CS_GCDPARAM_BASEDOSE1',
                               'CS_GCDPARAM_BASEDOSE2',
                               'CS_GCDPARAM_BASEDOSE3',
                               'CS_GCDPARAM_ETA1',
                               'CS_GCDPARAM_ETA2',
                               'CS_GCDPARAM_ETA3',
                               'CS_POSITIONAL_CD_MAP',
                               'CEC_PARAM']

            # if _o.cs_command in cs_command_list and 'NA':

            if _o.cs_command == 'CS_POSITIONAL_CD_MAP':
                if input_value:
                    _o.cd_map_id = file_id
                else:
                    _o.cd_map_id = 0

            if _o.cs_command == 'CEC_PARAM':
                if input_value:
                    _o.cec_id = file_id
                else:
                    _o.cec_id = 0

            _o.version = _o.version + 1
            _s = unreleased_service()

            return _s.upd_info_tree_data(_o)
        else:
            data = {"success": False, "msg": "Failed"}
            return JsonResponse(data, safe=False)


class unreleased_del(BaseView):

    def get(self, request):
        tool = request.GET.get('tool')
        node = request.GET.get('node')
        tone = request.GET.get('tone')
        blank = request.GET.get('blank')
        grade = request.GET.get('grade')
        pattern_density = request.GET.get('pattern_density')
        layer = request.GET.get('layer')

        _o = unreleased_info()
        _o.tool = tool
        _o.node = node
        _o.tone = tone
        _o.blank = blank
        _o.grade = grade
        _o.pattern_density = pattern_density
        _o.layer = layer

        _s = unreleased_service()

        return _s.del_info_tree_data(_o)


def create_check(request):
    tool = request.POST.get('tool')
    node = request.POST.get('node')
    tone = request.POST.get('tone')
    blank = request.POST.get('blank')
    grade = request.POST.get('grade')
    pattern_density = request.POST.get('pattern_density')
    layer = request.POST.get('layer')

    _o = unreleased_info.objects.filter(tool=tool, node=node, tone=tone, blank=blank, grade=grade,
                                        pattern_density=pattern_density, layer=layer, is_delete=0).count()

    data = {}
    if _o == 0:
        data["success"] = True
        data["msg"] = "Success"
    else:
        data["success"] = False
        data["msg"] = "Failed"

    return JsonResponse(data, safe=False)


@csrf_exempt
def check_value(request):
    cs_command = request.POST.get('cs_command')
    value = request.POST.get('value')
    id = request.POST.get('id')
    # type, 1: template 2:maintain
    type = request.POST.get('type')

    data_dict = {}

    if value == '':
        data_dict['success'] = True
        data_dict['msg'] = 'success'
        data_dict['file_id'] = 0
        return JsonResponse(data_dict, safe=False)

    temp = info_tree_template.objects.get(cs_command=cs_command, is_delete=0)

    pass_list = ['CS_POSITIONAL_CD_MAP', 'CEC_PARAM']
    print(cs_command, 'CS_POSITIONAL_CD_MAP')
    if cs_command not in pass_list:
        temp_option = info_tree_template_option.objects.get(temp_id=temp.id, is_delete=0)

    global s, msg, CS_STRIPE_LAYER_COUNT_data, _id

    if type == 1 or type == '1':
        CS_STRIPE_LAYER_COUNT_data = unreleased_info.objects.get(cs_command='CS_STRIPE_LAYER_COUNT', is_delete=0)

        CS_GCD_MESH_SIZE_data = unreleased_info.objects.get(cs_command='CS_GCD_MESH_SIZE', is_delete=0)
    elif type == 2 or type == '2':
        _o = unreleased_info.objects.get(id=id)
        CS_STRIPE_LAYER_COUNT_data = unreleased_info.objects.get(tool=_o.tool, node=_o.node, tone=_o.tone,
                                                                 blank=_o.blank, grade=_o.grade,
                                                                 pattern_density=_o.pattern_density, layer=_o.layer,
                                                                 cs_command='CS_STRIPE_LAYER_COUNT', is_delete=0)

        CS_GCD_MESH_SIZE_data = unreleased_info.objects.get(tool=_o.tool, node=_o.node, tone=_o.tone, blank=_o.blank,
                                                            grade=_o.grade, pattern_density=_o.pattern_density,
                                                            layer=_o.layer, cs_command='CS_GCD_MESH_SIZE', is_delete=0)
    _id = '0'
    s = False
    for case in switch(str(temp.cs_command)):

        if case('CS_STRIPE_LAYER_COUNT'):
            start = change_data_type(temp_option.start).trans_integer()
            end = change_data_type(temp_option.end).trans_integer()
            data = change_data_type(value).trans_integer()

            if start[0] and end[0] and data[0]:
                if start[1] <= data[1] <= end[1]:
                    s = True
                else:
                    msg = 'CS_STRIPE_LAYER_COUNT out of range'
            else:
                msg = 'CS_STRIPE_LAYER_COUNT data type error'
            break

        if case('CS_SOAKING'):

            if value == 'NA':
                s = True
            else:
                start = change_data_type(temp_option.start).trans_integer()
                end = change_data_type(temp_option.end).trans_integer()
                data = change_data_type(value).trans_integer()

                if start[0] and end[0] and data[0]:
                    if start[1] <= data[1] <= end[1]:
                        s = True
                    else:
                        msg = 'CS_SOAKING out of range'
                else:
                    msg = 'CS_SOAKING data type error'
            break

        if case('CS_W_CH_SOAK'):
            if value == 'NA':
                s = True
            else:
                start = change_data_type(temp_option.start).trans_integer()
                end = change_data_type(temp_option.end).trans_integer()
                data = change_data_type(value).trans_integer()

                if start[0] and end[0] and data[0]:
                    if start[1] <= data[1] <= end[1]:
                        s = True
                    else:
                        msg = 'CS_W_CH_SOAK out of range'
                else:
                    msg = 'CS_W_CH_SOAK data type error'
            break

        if case('CS_BASE_DOSE'):
            start = change_data_type(temp_option.start).trans_integer()
            end = change_data_type(temp_option.end).trans_integer()
            data = change_data_type(value).trans_float()
            CS_STRIPE_LAYER_COUNT_data_val = change_data_type(CS_STRIPE_LAYER_COUNT_data.value).trans_integer()

            if start[0] and end[0] and data[0] and CS_STRIPE_LAYER_COUNT_data_val[0]:
                if start[1] <= data[1] <= end[1] * CS_STRIPE_LAYER_COUNT_data_val[1]:
                    s = True
                else:
                    msg = 'CS_BASE_DOSE out of range'
            else:
                msg = 'CS_BASE_DOSE data type error'
            break

        if case('CS_SIGMA1'):
            start = change_data_type(temp_option.start).trans_integer()
            end = change_data_type(temp_option.end).trans_integer()
            data = change_data_type(value).trans_float()

            if start[0] and end[0] and data[0]:
                if start[1] <= data[1] <= end[1]:
                    s = True
                else:
                    msg = 'CS_SIGMA1 out of range'
            else:
                msg = 'CS_SIGMA1 data type error'
            break

        if case('CS_ETA1'):
            start = change_data_type(temp_option.start).trans_integer()
            end = change_data_type(temp_option.end).trans_integer()
            data = change_data_type(value).trans_float()

            if start[0] and end[0] and data[0]:
                if start[1] <= data[1] <= end[1]:
                    s = True
                else:
                    msg = 'CS_ETA1 out of range'
            else:
                msg = 'CS_ETA1 data type error'
            break

        if case('CS_KBR_PRX_MESH_SIZE'):
            if value == 'NA':
                s = True
            else:
                start = change_data_type(temp_option.start).trans_integer()
                end = change_data_type(temp_option.end).trans_integer()
                data = change_data_type(value).trans_integer()
                CS_GCD_MESH_SIZE_data = change_data_type(CS_GCD_MESH_SIZE_data.value).trans_integer()

                if start[0] and end[0] and data[0] and CS_GCD_MESH_SIZE_data[0]:
                    if start[1] <= data[1] <= CS_GCD_MESH_SIZE_data[1] / end[1]:
                        s = True
                    else:
                        msg = 'CS_KBR_PRX_MESH_SIZE out of range'
                else:
                    msg = 'CS_KBR_PRX_MESH_SIZE data type error'
            break

        if case('CS_THETA1'):
            if value == 'NA':
                s = True
            else:
                start = change_data_type(temp_option.start).trans_float()
                end = change_data_type(temp_option.end).trans_float()
                data = change_data_type(value).trans_float()

                if start[0] and end[0] and data[0]:
                    if start[1] <= data[1] <= end[1]:
                        s = True
                    else:
                        msg = 'CS_THETA1 out of range'
                else:
                    msg = 'CS_THETA1 data type error'
            break

        if case('CS_SIGMAF1'):
            if value == 'NA':
                s = True
            else:
                end = change_data_type(temp_option.end).trans_integer()
                data = change_data_type(value).trans_float()
                CS_GCD_MESH_SIZE_data = change_data_type(CS_GCD_MESH_SIZE_data.value).trans_integer()

                if end[0] and data[0] and CS_GCD_MESH_SIZE_data[0]:
                    if CS_GCD_MESH_SIZE_data[1] <= data[1] <= end[1]:
                        s = True
                    else:
                        msg = 'CS_SIGMAF1 out of range'
                else:
                    msg = 'CS_SIGMAF1 data type error'
            break

        if case('CS_GAMMA1'):
            if value == 'NA':
                s = True
            else:
                start = change_data_type(temp_option.start).trans_integer()
                end = change_data_type(temp_option.end).trans_integer()
                data = change_data_type(value).trans_float()

                if start[0] and end[0] and data[0]:
                    if start[1] <= data[1] <= end[1]:
                        s = True
                    else:
                        msg = 'CS_GAMMA1 out of range'
                else:
                    msg = 'CS_GAMMA1 data type error'
            break

        if case('CS_SIGMAL1'):
            if value == 'NA':
                s = True
            else:
                end = change_data_type(temp_option.end).trans_integer()
                data = change_data_type(value).trans_float()
                CS_GCD_MESH_SIZE_data = change_data_type(CS_GCD_MESH_SIZE_data.value).trans_integer()

                if end[0] and data[0] and CS_GCD_MESH_SIZE_data[0]:
                    if CS_GCD_MESH_SIZE_data[1] <= data[1] <= end[1]:
                        s = True
                    else:
                        msg = 'CS_SIGMAL1 out of range'
                else:
                    msg = 'CS_SIGMAL1 data type error'
            break

        if case('CS_TEC_COEF_DC0'):
            if value == 'NA':
                s = True
            else:
                start = change_data_type(temp_option.start).trans_integer()
                end = change_data_type(temp_option.end).trans_integer()
                data = change_data_type(value).trans_float()

                if start[0] and end[0] and data[0]:
                    if start[1] <= data[1] <= end[1]:
                        s = True
                    else:
                        msg = 'CS_TEC_COEF_DC0 out of range'
                else:
                    msg = 'CS_TEC_COEF_DC0 data type error'
            break

        if case('CS_GCDPARAM_CD1'):
            if value == 'NA':
                s = True
            else:
                start = change_data_type(temp_option.start).trans_integer()
                end = change_data_type(temp_option.end).trans_integer()
                data = change_data_type(value).trans_float()

                if start[0] and end[0] and data[0]:
                    if start[1] <= data[1] <= end[1] and data[1] != 0.0 and data[1] != 0:
                        s = True
                    else:
                        msg = 'CS_GCDPARAM_CD1 out of range'
                else:
                    msg = 'CS_GCDPARAM_CD1 data type error'
            break

        if case('CS_GCDPARAM_CD2'):
            if value == 'NA':
                s = True
            else:
                start = change_data_type(temp_option.start).trans_integer()
                end = change_data_type(temp_option.end).trans_integer()
                data = change_data_type(value).trans_float()

                if start[0] and end[0] and data[0]:
                    if start[1] <= data[1] <= end[1] and data[1] != 0.0 and data[1] != 0:
                        s = True
                    else:
                        msg = 'CS_GCDPARAM_CD2 out of range'
                else:
                    msg = 'CS_GCDPARAM_CD2 data type error'
            break

        if case('CS_GCDPARAM_CD3'):
            if value == 'NA':
                s = True
            else:
                start = change_data_type(temp_option.start).trans_integer()
                end = change_data_type(temp_option.end).trans_integer()
                data = change_data_type(value).trans_float()

                if start[0] and end[0] and data[0]:
                    if start[1] <= data[1] <= end[1] and data[1] != 0.0 and data[1] != 0:
                        s = True
                    else:
                        msg = 'CS_GCDPARAM_CD3 out of range'
                else:
                    msg = 'CS_GCDPARAM_CD3 data type error'
            break

        if case('CS_GCDPARAM_BASEDOSE1'):
            if value == 'NA':
                s = True
            else:
                start = change_data_type(temp_option.start).trans_integer()
                end = change_data_type(temp_option.end).trans_integer()
                data = change_data_type(value).trans_float()
                CS_STRIPE_LAYER_COUNT_data_val = change_data_type(CS_STRIPE_LAYER_COUNT_data.value).trans_integer()

                if start[0] and end[0] and data[0] and CS_STRIPE_LAYER_COUNT_data_val[0]:
                    if start[1] <= data[1] <= end[1] * CS_STRIPE_LAYER_COUNT_data_val[1]:
                        s = True
                    else:
                        msg = 'CS_GCDPARAM_BASEDOSE1 out of range'
                else:
                    msg = 'CS_GCDPARAM_BASEDOSE1 data type error'
            break

        if case('CS_GCDPARAM_BASEDOSE2'):
            if value == 'NA':
                s = True
            else:
                start = change_data_type(temp_option.start).trans_integer()
                end = change_data_type(temp_option.end).trans_integer()
                data = change_data_type(value).trans_float()
                CS_STRIPE_LAYER_COUNT_data_val = change_data_type(CS_STRIPE_LAYER_COUNT_data.value).trans_integer()

                if start[0] and end[0] and data[0] and CS_STRIPE_LAYER_COUNT_data_val[0]:
                    if start[1] <= data[1] <= end[1] * CS_STRIPE_LAYER_COUNT_data_val[1]:
                        s = True
                    else:
                        msg = 'CS_GCDPARAM_BASEDOSE2 out of range'
                else:
                    msg = 'CS_GCDPARAM_BASEDOSE2 data type error'
            break

        if case('CS_GCDPARAM_BASEDOSE3'):
            if value == 'NA':
                s = True
            else:
                start = change_data_type(temp_option.start).trans_integer()
                end = change_data_type(temp_option.end).trans_integer()
                data = change_data_type(value).trans_float()
                CS_STRIPE_LAYER_COUNT_data_val = change_data_type(CS_STRIPE_LAYER_COUNT_data.value).trans_integer()

                if start[0] and end[0] and data[0] and CS_STRIPE_LAYER_COUNT_data_val[0]:
                    if start[1] <= data[1] <= end[1] * CS_STRIPE_LAYER_COUNT_data_val[1]:
                        s = True
                    else:
                        msg = 'CS_GCDPARAM_BASEDOSE3 out of range'
                else:
                    msg = 'CS_GCDPARAM_BASEDOSE3 data type error'
            break

        if case('CS_GCDPARAM_ETA1'):
            if value == 'NA':
                s = True
            else:
                start = change_data_type(temp_option.start).trans_integer()
                end = change_data_type(temp_option.end).trans_integer()
                data = change_data_type(value).trans_float()

                if start[0] and end[0] and data[0]:
                    if start[1] <= data[1] <= end[1]:
                        s = True
                    else:
                        msg = 'CS_GCDPARAM_ETA1 out of range'
                else:
                    msg = 'CS_GCDPARAM_ETA1 data type error'
            break

        if case('CS_GCDPARAM_ETA2'):
            if value == 'NA':
                s = True
            else:
                start = change_data_type(temp_option.start).trans_integer()
                end = change_data_type(temp_option.end).trans_integer()
                data = change_data_type(value).trans_float()

                if start[0] and end[0] and data[0]:
                    if start[1] <= data[1] <= end[1]:
                        s = True
                    else:
                        msg = 'CS_GCDPARAM_ETA2 out of range'
                else:
                    msg = 'CS_GCDPARAM_ETA2 data type error'
            break

        if case('CS_GCDPARAM_ETA3'):
            if value == 'NA':
                s = True
            else:
                start = change_data_type(temp_option.start).trans_integer()
                end = change_data_type(temp_option.end).trans_integer()
                data = change_data_type(value).trans_float()

                if start[0] and end[0] and data[0]:
                    if start[1] <= data[1] <= end[1]:
                        s = True
                    else:
                        msg = 'CS_GCDPARAM_ETA3 out of range'
                else:
                    msg = 'CS_GCDPARAM_ETA3 data type error'
            break

        if case('CS_POSITIONAL_CD_MAP'):

            data = str(value)
            if value == 'NA':
                s = True
            else:

                data_dat = data + '.dat'
                data_prm = data + '.prm'
                path_list = []
                for dirPath, dirNames, fileNames in os.walk(Constant.CD_MAP_PATH):
                    for f in fileNames:
                        path_list.append(f)

                _o = cd_map.objects.filter(cd_map_dat_name=data_dat, index_prm_name=data_prm, is_delete=0).values('id')

                if data_dat in path_list and data_prm in path_list and _o.count() == 1:
                    s = True
                    _id = _o[0]['id']
                else:
                    msg = 'CD MAP file name not found'
            break

        if case('CEC_PARAM'):
            data = str(value)
            if value == 'NA':
                s = True
            else:
                data_txt = data + '.txt'
                path_list = []
                for dirPath, dirNames, fileNames in os.walk(Constant.CEC_PATH):
                    for f in fileNames:
                        path_list.append(f)

                _o = cec.objects.filter(cec_name=data_txt, is_delete=0).values('id')

                if data_txt in path_list and _o.count() == 1:
                    s = True
                    _id = _o[0]['id']
                else:
                    msg = 'CEC file name not found'
            break

    if s:
        data_dict['success'] = True
        data_dict['msg'] = 'success'
        data_dict['file_id'] = _id
    else:
        data_dict['success'] = False
        data_dict['msg'] = msg
    return JsonResponse(data_dict, safe=False)


class change_data_type:

    def __init__(self, value):
        self.value = value

    def trans_integer(self):
        try:
            data = int(self.value)
            return True, data
        except Exception as e:
            print(e)
            return False, 'data type error'

    def trans_float(self):
        try:
            data = float(self.value)
            return True, data
        except Exception as e:
            print(e)
            return False, 'data type error'


def unreleased_tree_json(request):
    tree_type = int(request.GET.get('tree_type'))
    j_list = []
    customer_list = unreleased_info.objects.filter(lock=tree_type, is_delete=0).values(
        'customer').distinct().order_by('customer')
    for customer in customer_list:
        # Tool
        tool_list = unreleased_info.objects.filter(customer=customer['customer']).values(
            'tool').distinct().order_by('tool')
        customer_dict = {"level": 1,
                         "name": customer['customer'],
                         "m_title": customer['customer'],
                         "text": customer['customer'],
                         "children": []}
        j_list.append(customer_dict)
        customer_no = len(j_list) - 1
        print(tool_list)

        print(tool_list.query)
        tree_info_2 = [customer['customer']]
        for tool in tool_list:
            # catalog_tool_id = tool_name_route.objects.get(info_tree_name=tool['tool']).catalog_tool_id

            tool_dict = {"level": 2,
                         "name": tool['tool'],
                         "text": tool['tool'],
                         "tree_info_2": tree_info_2,
                         "children": []}

            j_list[customer_no]['children'].append(tool_dict)
            tool_no = len(j_list[customer_no]['children']) - 1

            # Node
            node_list = unreleased_info.objects.filter(lock=tree_type, is_delete=0, tool=tool['tool'],
                                                       customer=customer['customer']).values(
                'node').distinct()
            print(node_list)
            if node_list.count() == 0:
                continue

            tree_info_3 = [customer['customer'], tool['tool']]
            for node in node_list:
                node_dict = {"level": 3,
                             "name": node['node'],
                             "text": node['node'],
                             "tree_info_3": tree_info_3,
                             "children": []}

                j_list[customer_no]['children'][tool_no]['children'].append(node_dict)
                node_no = len(j_list[customer_no]['children'][tool_no]['children']) - 1

                # Tone
                tone_list = unreleased_info.objects.filter(lock=tree_type, is_delete=0, tool=tool['tool'],
                                                           node=node['node'], customer=customer['customer']).values(
                    'tone').distinct()
                print(tone_list)

                if tone_list.count() == 0:
                    continue

                tree_info_4 = [customer['customer'], tool['tool'], node['node']]
                for tone in tone_list:
                    tone_dict = {"level": 4,
                                 "name": tone['tone'],
                                 "text": tone['tone'],
                                 "tree_info_4": tree_info_4,
                                 "children": []}

                    j_list[customer_no]['children'][tool_no]['children'][node_no]['children'].append(tone_dict)
                    tone_no = len(j_list[customer_no]['children'][tool_no]['children'][node_no]['children']) - 1

                    # Blank
                    blank_list = unreleased_info.objects.filter(lock=tree_type, is_delete=0,
                                                                tool=tool['tool'],
                                                                node=node['node'],
                                                                tone=tone['tone'],
                                                                customer=customer['customer']).values(
                        'blank').distinct()
                    if blank_list.count() == 0:
                        continue

                    tree_info_5 = [customer['customer'], tool['tool'], node['node'], tone['tone']]
                    for blank in blank_list:
                        blank_dict = {"level": 5,
                                      "name": blank['blank'],
                                      "text": blank['blank'],
                                      "tree_info_5": tree_info_5,
                                      "children": []}

                        j_list[customer_no]['children'][tool_no]['children'][node_no]['children'][tone_no][
                            'children'].append(blank_dict)
                        blank_no = len(
                            j_list[customer_no]['children'][tool_no]['children'][node_no]['children'][tone_no][
                                'children']) - 1

                        # Grade
                        grade_list = unreleased_info.objects.filter(lock=tree_type, is_delete=0,
                                                                    tool=tool['tool'],
                                                                    node=node['node'],
                                                                    tone=tone['tone'],
                                                                    blank=blank['blank'],
                                                                    customer=customer['customer']).values(
                            'grade').distinct()
                        if grade_list.count() == 0:
                            continue

                        tree_info_6 = [customer['customer'], tool['tool'], node['node'], tone['tone'], blank['blank']]
                        for grade in grade_list:
                            grade_dict = {"level": 6,
                                          "name": grade['grade'],
                                          "text": grade['grade'],
                                          "tree_info_6": tree_info_6,
                                          "children": []}

                            j_list[customer_no]['children'][tool_no]['children'][node_no]['children'][tone_no][
                                'children'][blank_no][
                                'children'].append(grade_dict)
                            grade_no = len(
                                j_list[customer_no]['children'][tool_no]['children'][node_no]['children'][tone_no][
                                    'children']
                                [blank_no]['children']) - 1

                            # Pattern density
                            pattern_density_list = unreleased_info.objects.filter(lock=tree_type, is_delete=0,
                                                                                  tool=tool['tool'],
                                                                                  node=node['node'],
                                                                                  tone=tone['tone'],
                                                                                  blank=blank['blank'],
                                                                                  grade=grade['grade'],
                                                                                  customer=customer['customer']).values(
                                'pattern_density').distinct()
                            if pattern_density_list.count() == 0:
                                continue

                            tree_info_7 = [customer['customer'], tool['tool'], node['node'], tone['tone'],
                                           blank['blank'], grade['grade']]
                            for pattern_density in pattern_density_list:
                                pattern_density_dict = {"level": 7,
                                                        "name": pattern_density['pattern_density'],
                                                        "text": pattern_density['pattern_density'],
                                                        "tree_info_7": tree_info_7,
                                                        "children": []}

                                j_list[customer_no]['children'][tool_no]['children'][node_no]['children'][tone_no][
                                    'children'][blank_no][
                                    'children'][grade_no]['children'].append(pattern_density_dict)
                                pattern_density_no = len(
                                    j_list[customer_no]['children'][tool_no]['children'][node_no]['children'][tone_no][
                                        'children']
                                    [blank_no]['children'][grade_no]['children']) - 1

                                # Layer
                                layer_list = unreleased_info.objects.filter(lock=tree_type, is_delete=0,
                                                                            tool=tool['tool'],
                                                                            node=node['node'],
                                                                            tone=tone['tone'],
                                                                            blank=blank['blank'],
                                                                            grade=grade['grade'],
                                                                            pattern_density=pattern_density[
                                                                                'pattern_density'],
                                                                            customer=customer['customer']).values(
                                    'layer').distinct()
                                if layer_list.count() == 0:
                                    continue

                                tree_info_8 = [customer['customer'], tool['tool'], node['node'], tone['tone'],
                                               blank['blank'], grade['grade'],
                                               pattern_density['pattern_density']]
                                for layer in layer_list:
                                    layer_dict = {"level": 8,
                                                  "name": layer['layer'],
                                                  "text": layer['layer'],
                                                  "tree_info_8": tree_info_8}

                                    j_list[customer_no]['children'][tool_no]['children'][node_no]['children'][tone_no][
                                        'children'][blank_no][
                                        'children'][grade_no]['children'][pattern_density_no]['children'].append(
                                        layer_dict)

    k = json.dumps(j_list)

    return HttpResponse(k)


@csrf_exempt
def unreleased_export(request):
    customer = request.GET.get('s_customer')
    tool = request.GET.get('s_tool')
    node = request.GET.get('s_node')
    tone = request.GET.get('s_tone')
    blank = request.GET.get('s_blank')
    grade = request.GET.get('s_grade')
    pattern_density = request.GET.get('s_pattern_density')
    layer = request.GET.get('s_layer')

    path, excel_name = write_excel(customer, tool, node, tone, blank, grade, pattern_density, layer)

    _o = info_tree_data_export_log()
    _o.tool = tool
    _o.node = node
    _o.tone = tone
    _o.blank = blank
    _o.grade = grade
    _o.pattern_density = pattern_density
    _o.layer = layer
    _o.file_name = excel_name
    _o.file_path = path

    unreleased_service().add_export_log(_o)

    file = open(path, 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="' + excel_name + '"'
    return response


@csrf_exempt
def unreleased_download(request):
    cur_path = os.path.abspath(os.path.dirname(__file__)).split(PROJECT_NAME)[0]  # 获得项目同级目录
    temp_path = os.path.join(os.path.dirname(cur_path), Constant.TOOLING_FORM_DOWNLOAD_DIR)

    file_name = 'Mask_DP_infotree_unreleased_template.xlsx'
    path = os.path.join(temp_path, file_name)

    file = open(path, 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="' + file_name + '"'
    return response


def set_style(name, height, bold=False):
    style = xlwt.XFStyle()  # 初始化樣式

    font = xlwt.Font()  # 為樣式建立字型
    font.name = name  # 'Times New Roman'
    font.bold = bold
    font.color_index = 4
    font.height = height
    # borders= xlwt.Borders()
    # borders.left= 6
    # borders.right= 6
    # borders.top= 6
    # borders.bottom= 6
    style.font = font
    # style.borders = borders
    return style


# export excel
def write_excel(customer, tool, node, tone, blank, grade, pattern_density, layer):
    f = xlwt.Workbook()  # 建立工作簿
    '''建立第一個sheet:sheet1'''
    sheet1 = f.add_sheet(u'unreleased', cell_overwrite_ok=True)  # 建立sheet

    tree_data = unreleased_info.objects.filter(customer=customer, tool=tool, node=node, tone=tone, blank=blank,
                                               grade=grade,
                                               pattern_density=pattern_density, layer=layer, is_delete=0)

    excel_head_name = [u'customer', u'tool', u'node', u'tone', u'blank', u'grade', u'pattern_density', u'layer',
                       u'type',
                       u'cs_command', u'value', u'version']
    row = [excel_head_name]
    for data in tree_data:
        data_list = [data.customer, data.tool, data.node, data.tone, data.blank, data.grade, data.pattern_density,
                     data.layer,
                     data.type, data.cs_command, data.value, data.version]
        print(data_list)
        row.append(data_list)

    print(row)

    # row = [[u'A', u'B', u'C', u'D', u'E'], [u'1', u'2', u'3', u'4', u'5'], [u'1', u'2', u'3', u'4', u'5']]
    for row_c in range(0, len(row)):
        row_1 = row[row_c]
        for row_2 in range(0, len(row_1)):
            r = row_1[row_2]
            sheet1.write(row_c, row_2, r, set_style('Times New Roman', 220, True))

    # excel_name = str(datetime.datetime.now())
    excel_name = str(time.time()).replace('.', '')
    # time.time()

    file_name = excel_name + '.xls'
    print(os.path.dirname(__file__))
    cur_path = os.path.abspath(os.path.dirname(__file__)).split('Mask_DP')[0]
    upl_path = os.path.join(os.path.dirname(cur_path), 'infotree_export')
    if not os.path.exists(upl_path):
        os.mkdir(upl_path)

    file_path = os.path.join(upl_path, file_name)

    f.save(file_path)

    return file_path, file_name


class unreleased_import(BaseView):

    def get(self, request):
        if request.method == 'GET':

            cur_path = os.path.abspath(os.path.dirname(__file__)).split('Mask_DP')[0]
            upl_path = os.path.join(os.path.dirname(cur_path), 'Mask_DP_maintain_import/')
            if not os.path.exists(upl_path):
                os.mkdir(upl_path)

            upl_path = upl_path.replace('\\', '/')

            sub_id = 'INFOTREE_UNRELEASED'
            server_url = '/system/upload/file_upload/'
            auto = False
            threads = 1
            fileNumLimit = 1
            fileSizeLimit = 10 * 1024 * 1024
            fileSingleSizeLimit = 10 * 1024 * 1024
            file_type = 'xlsx, xls'
            check_type = 'md5'
            type_no = '0'
            callback_api = "/infotree/unreleased/import_check/"
            # callback_api = ''
            return render(request, 'system_upload.html', {'id': 0,
                                                          'sub_id': sub_id,
                                                          'server_path': upl_path,
                                                          'server_url': server_url,
                                                          'auto': auto,
                                                          'threads': threads,
                                                          'fileNumLimit': fileNumLimit,
                                                          'fileSizeLimit': fileSizeLimit,
                                                          'fileSingleSizeLimit': fileSingleSizeLimit,
                                                          'file_type': file_type,
                                                          'check_type': check_type,
                                                          'type_no': type_no,
                                                          'callback_api': callback_api})


class unreleased_import_check(BaseView):
    def post(self, request):
        if request.method == 'POST':

            res_id = request.POST.get('res_id')
            file_info = upload_info.objects.get(id=res_id)

            file_path = os.path.join(file_info.file_path, file_info.file_name)
            # file_path = 'D:/infotree_maintain_temp.xlsx'
            excel = pd.read_excel(file_path, sheet_name='unreleased')

            cursor = connection.cursor()
            # 清除 infotree_info_tree_data_import_temp 資料
            cursor.execute("delete from infotree_info_tree_data_import_temp")
            # 將 infotree_info_tree_data_import_temp id 計數重置
            cursor.execute("alter table infotree_info_tree_data_import_temp auto_increment =1")

            excel_len = len(excel)

            # 取得欄位名稱
            group = str(excel.iloc[0, 0])
            customer = str(excel.iloc[0, 1])
            tool = str(excel.iloc[0, 2])
            node = str(excel.iloc[0, 3])
            tone = str(excel.iloc[0, 4])
            blank = str(excel.iloc[0, 5])
            grade = str(excel.iloc[0, 6])
            pattern_density = str(excel.iloc[0, 7])
            layer = str(excel.iloc[0, 8])
            type = str(excel.iloc[0, 9])
            cs_command = str(excel.iloc[0, 10])
            value = str(excel.iloc[0, 11])
            limit_type = str(excel.iloc[0, 12])
            limit = str(excel.iloc[0, 13])

            # 判斷欄位名稱
            if not (group == 'Group' and tool == 'Tool' and node == 'Node' and tone == 'Tone' and blank == 'Blank' and \
                    grade == 'Grade' and pattern_density == 'Pattern density' and layer == 'Layer' and \
                    type == 'Type' and cs_command == 'CS_Command' and value == 'Value' and \
                    limit_type == 'Limit_type' and limit == 'Limit' and customer == 'Customer'):
                data = {"success": False, "msg": "Column name error"}
                return JsonResponse(data, safe=False)

            # 將 excel 資料插入 info_tree_data_import_temp
            try:
                i = 1
                data_list = list()
                while i < excel_len:
                    _o = info_tree_data_import_temp()
                    _o.group = int(excel.iloc[i, 0])
                    _o.customer = str(excel.iloc[i, 1])
                    _o.tool = str(excel.iloc[i, 2])
                    _o.node = str(excel.iloc[i, 3])
                    _o.tone = str(excel.iloc[i, 4])
                    _o.blank = str(excel.iloc[i, 5])
                    _o.grade = str(excel.iloc[i, 6])
                    _o.pattern_density = str(excel.iloc[i, 7])
                    _o.layer = str(excel.iloc[i, 8])
                    _o.type = str(excel.iloc[i, 9])
                    _o.cs_command = str(excel.iloc[i, 10])
                    _o.value = str(excel.iloc[i, 11])
                    _o.limit_type = int(excel.iloc[i, 12])
                    _o.limit = str(excel.iloc[i, 13])
                    data_list.append(_o)
                    i += 1

                info_tree_data_import_temp.objects.bulk_create(data_list)
            except Exception as e:
                print(e)
                data = {"success": False, "msg": "Excel data insert into info_tree_data_import_temp failed"}
                return JsonResponse(data, safe=False)

            # 獲取 tree 字典
            tree_id_list = tree.objects.filter(is_delete=0).values()
            tree_value_dict = {}
            for tree_id in tree_id_list:
                labels = tree_option.objects.filter(tree_id=tree_id['id'], is_delete=0).order_by('id').values('value')
                label_list = []
                for label in labels:
                    label_list.append(label['value'])
                tree_value_dict[tree_id['name']] = label_list

            # 獲取 template 字典
            temp_id_list = info_tree_template.objects.filter(is_delete=0, limit_type=1).values()
            temp_option_dict = {}
            for temp_id in temp_id_list:
                labels = info_tree_template_option.objects.filter(temp_id=temp_id['id'], is_delete=0).order_by(
                    'id').values('option')
                label_list = []
                for label in labels:
                    label_list.append(label['option'])
                temp_option_dict[temp_id['cs_command']] = label_list

            print(tree_value_dict)
            print(temp_option_dict)

            global cd_map_cec_id_dict
            cd_map_cec_id_dict = {}
            # 查詢數據 distinct
            gp_list = info_tree_data_import_temp.objects.all().values('group').distinct()
            param_list = info_tree_data_import_temp.objects.all().values('customer', 'tool', 'node', 'tone', 'blank',
                                                                         'grade',
                                                                         'pattern_density', 'layer').distinct()

            # 判斷 excel 內不同的group，[tool,noe,tone,blank,grade,pattern_density,layer]是否不同
            if not len(gp_list) == len(param_list):
                data = {"success": False,
                        "msg": "Group not match from [tool,noe,tone,blank,grade,pattern_density,layer]"}
                return JsonResponse(data, safe=False)

            for gp in gp_list:
                print(gp['group'])

                # 判斷每個 group 的資料筆數與 template 是否一致
                # ['MS05', 'MS06', 'MS18','MS28']
                temp_data = info_tree_template.objects.filter(Q(machine_type__contains='MS05') | Q(
                    machine_type__contains='MS06') | Q(machine_type__contains='MS18') | Q(
                    machine_type__contains='MS28')).exclude(is_delete=1)
                print(temp_data.query)

                temp_count = temp_data.count()

                gp_count = info_tree_data_import_temp.objects.filter(group=gp['group']).count()
                print("gp_count =", gp_count)
                print("temp_count =", temp_count)
                if not gp_count == temp_count:
                    msg = "Group : " + str(gp['group']) + " data count error"
                    data = {"success": False, "msg": msg}
                    return JsonResponse(data, safe=False)

                # 判斷相同的group, [tool,noe,tone,blank,grade,pattern_density,layer] 是否相同
                gp_dis_list = info_tree_data_import_temp.objects.filter(group=gp['group']).values(
                    'customer', 'tool', 'node', 'tone', 'blank', 'grade', 'pattern_density', 'layer').distinct()
                gp_dis_count = gp_dis_list.count()
                if not gp_dis_count == 1:
                    msg = "Group : " + str(
                        gp['group']) + ", [customer,tool,noe,tone,blank,grade,pattern_density,layer] 不相同"
                    data = {"success": False, "msg": msg}
                    return JsonResponse(data, safe=False)

                # 判斷 cs_command 是否重覆
                gp_cs_dis_count = info_tree_data_import_temp.objects.filter(group=gp['group']).values(
                    'cs_command').distinct().count()
                if not gp_cs_dis_count == gp_count:
                    msg = "Group : " + str(gp['group']) + " cs_command repeat"
                    data = {"success": False, "msg": msg}
                    return JsonResponse(data, safe=False)

                # 判斷 tool,noe,tone,blank,grade,pattern_density,layer 是否在選項內
                print(gp_dis_list[0]['tool'] in tree_value_dict['Tool'], gp_dis_list[0]['tool'],
                      tree_value_dict['Tool'])
                print(gp_dis_list[0]['node'] in tree_value_dict['Node'], gp_dis_list[0]['node'],
                      tree_value_dict['Node'])
                print(gp_dis_list[0]['tone'] in tree_value_dict['Tone'], gp_dis_list[0]['tone'],
                      tree_value_dict['Tone'])
                print(gp_dis_list[0]['blank'] in tree_value_dict['Blank'], gp_dis_list[0]['blank'],
                      tree_value_dict['Blank'])
                print(gp_dis_list[0]['grade'] in tree_value_dict['Grade'], gp_dis_list[0]['grade'],
                      tree_value_dict['Grade'])
                print(gp_dis_list[0]['pattern_density'] in tree_value_dict['Pattern_density'],
                      gp_dis_list[0]['pattern_density'], tree_value_dict['Pattern_density'])
                print(gp_dis_list[0]['layer'] in tree_value_dict['Layer'], gp_dis_list[0]['layer'],
                      tree_value_dict['Layer'])

                if not (gp_dis_list[0]['tool'] in tree_value_dict['Tool'] \
                        and gp_dis_list[0]['node'] in tree_value_dict['Node'] \
                        and gp_dis_list[0]['customer'] in tree_value_dict['Customer'] \
                        and gp_dis_list[0]['tone'] in tree_value_dict['Tone'] \
                        and gp_dis_list[0]['blank'] in tree_value_dict['Blank'] \
                        and gp_dis_list[0]['grade'] in tree_value_dict['Grade'] \
                        and gp_dis_list[0]['pattern_density'] in tree_value_dict['Pattern_density'] \
                        and gp_dis_list[0]['layer'] in tree_value_dict['Layer']):
                    msg = "Group : " + str(gp['group']) + " out of option"
                    data = {"success": False, "msg": msg}
                    return JsonResponse(data, safe=False)

                # 判斷 tool,noe,tone,blank,grade,pattern_density,layer 是否存在
                infotree_data_count = unreleased_info.objects.filter(tool=gp_dis_list[0]['tool'],
                                                                     customer=gp_dis_list[0]['customer'],
                                                                     node=gp_dis_list[0]['node'],
                                                                     tone=gp_dis_list[0]['tone'],
                                                                     blank=gp_dis_list[0]['blank'],
                                                                     grade=gp_dis_list[0]['grade'],
                                                                     pattern_density=gp_dis_list[0]['pattern_density'],
                                                                     layer=gp_dis_list[0]['layer'], is_delete=0).count()
                if not infotree_data_count == 0:
                    msg = "Group : " + str(gp['group']) + "[" + gp_dis_list[0]['tool'] + "," + \
                          gp_dis_list[0]['node'] + "," + gp_dis_list[0]['tone'] + "," + \
                          gp_dis_list[0]['blank'] + "," + gp_dis_list[0]['grade'] + "," + \
                          gp_dis_list[0]['pattern_density'] + "," + gp_dis_list[0]['layer'] + "," + " already exists"
                    data = {"success": False, "msg": msg}
                    return JsonResponse(data, safe=False)

                check_data_res, check_data_msg, cd_map_id, cec_id = self.check_data(gp['group'], temp_option_dict)

                msg = "Group : " + str(gp['group']) + ", " + check_data_msg
                if not check_data_res:
                    data = {"success": False, "msg": msg}
                    return JsonResponse(data, safe=False)

                cd_map_cec_id_dict[gp['group']] = {'cd_map_id': cd_map_id, 'cec_id': cec_id}

            print(cd_map_cec_id_dict)

            # 插入數據到 unreleased_info
            try:
                with transaction.atomic():
                    group = int(
                        unreleased_info.objects.all().values('group').distinct().order_by('-group')[0]['group']) + 1

                    temp_gp_data_list = list()
                    for _gp in gp_list:
                        print(_gp, _gp['group'])
                        _cd_map_id = cd_map_cec_id_dict[_gp['group']]['cd_map_id']
                        _cec_id = cd_map_cec_id_dict[_gp['group']]['cec_id']
                        _temp_gp_data = info_tree_data_import_temp.objects.filter(group=_gp['group'])
                        for temp_gp_data in _temp_gp_data:
                            _o = unreleased_info()
                            _o.group = group
                            if temp_gp_data.cs_command == 'CS_POSITIONAL_CD_MAP':
                                _o.cd_map_id = _cd_map_id
                            if temp_gp_data.cs_command == 'CEC_PARAM':
                                _o.cec_id = _cec_id
                            _o.customer = temp_gp_data.customer
                            _o.tool = temp_gp_data.tool
                            _o.node = temp_gp_data.node
                            _o.tone = temp_gp_data.tone
                            _o.blank = temp_gp_data.blank
                            _o.grade = temp_gp_data.grade
                            _o.pattern_density = temp_gp_data.pattern_density
                            _o.layer = temp_gp_data.layer
                            _o.type = temp_gp_data.type
                            _o.cs_command = temp_gp_data.cs_command
                            if temp_gp_data.value == 'NA' or temp_gp_data.value == 'nan':
                                _o.value = 'NA'
                            else:
                                _o.value = temp_gp_data.value
                            _o.limit_type = _o.limit = temp_gp_data.limit_type
                            _o.limit = temp_gp_data.limit
                            _o.temp_version = 0
                            _o.version = 1
                            _o.create_by = getCurrentSessionID
                            _o.create_date = getDateStr()
                            _o.create_time = getMilliSecond()
                            temp_gp_data_list.append(_o)

                        _m = maintain_table()
                        _m.customer = temp_gp_data.customer
                        _m.tool = temp_gp_data.tool
                        _m.node = temp_gp_data.node
                        _m.tone = temp_gp_data.tone
                        _m.blank = temp_gp_data.blank
                        _m.grade = temp_gp_data.grade
                        _m.pattern_density = temp_gp_data.pattern_density
                        _m.layer = temp_gp_data.layer
                        _m.create_by = getCurrentSessionID
                        _m.create_date = getDateStr()
                        _m.create_time = getMilliSecond()
                        _m.save()

                    unreleased_info.objects.bulk_create(temp_gp_data_list)

            except Exception as e:
                print(e)
                data = {"success": False, "msg": "Excel data insert into unreleased_info failed"}
                return JsonResponse(data, safe=False)

        data = {"success": True, "msg": "import success"}
        return JsonResponse(data, safe=False)

    def check_data(self, gp, temp_option_dict):
        try:
            with transaction.atomic():
                _data = info_tree_data_import_temp.objects.filter(group=gp)
                CS_STRIPE_data = info_tree_data_import_temp.objects.get(group=gp, cs_command='CS_STRIPE_LAYER_COUNT')
                CS_GCD_data = info_tree_data_import_temp.objects.get(group=gp, cs_command='CS_GCD_MESH_SIZE')

                print(CS_STRIPE_data, CS_GCD_data)
                global cd_map_id, cec_id
                for data in _data:
                    print("cs_command =", data.cs_command, "value =", data.value)
                    ch_res, ch_msg, _id = self.check_data_one(data.type, data.cs_command, data.value, data.limit_type,
                                                              CS_STRIPE_data, CS_GCD_data, temp_option_dict)
                    print(data.cs_command, ch_res, msg, _id)
                    if not ch_res:
                        return False, ch_msg, 0, 0

                    if data.cs_command == 'CS_POSITIONAL_CD_MAP':
                        cd_map_id = _id

                    if data.cs_command == 'CEC_PARAM':
                        cec_id = _id

                return True, ch_msg, cd_map_id, cec_id
        except Exception as e:
            print(e)
            return False, 'check data failed', 0, 0

    def check_data_one(self, type, cs_command, value, limit_type, CS_STRIPE_data, CS_GCD_data, temp_option_dict):
        try:
            global s, msg, temp, _id

            temp = info_tree_template.objects.get(cs_command=cs_command, is_delete=0)
            pass_list = ['CS_POSITIONAL_CD_MAP', 'CEC_PARAM']
            if cs_command not in pass_list and limit_type == 2:
                temp_option = info_tree_template_option.objects.get(temp_id=temp.id, is_delete=0)

            s = False
            msg = ''
            _id = 0

            cs_command_list = ['CS_SYSTEM_PARAM',
                               'CS_MASK_PARAM',
                               'CS_SOAKING',
                               'CS_W_CH_SOAK',
                               'CS_GCD_MESH_SIZE',
                               'CS_KBR_PRX_MESH_SIZE',
                               'CS_KBR_SW',
                               'CS_FEC_MODE',
                               'CS_THETA1',
                               'CS_SIGMAF1',
                               'CS_LEC_MODE',
                               'CS_GAMMA1',
                               'CS_SIGMAL1',
                               'CS_TEC_MODE',
                               'CS_TEC_COEF_DC0',
                               'CS_GCDPARAM_CD1',
                               'CS_GCDPARAM_CD2',
                               'CS_GCDPARAM_CD3',
                               'CS_GCDPARAM_BASEDOSE1',
                               'CS_GCDPARAM_BASEDOSE2',
                               'CS_GCDPARAM_BASEDOSE3',
                               'CS_GCDPARAM_ETA1',
                               'CS_GCDPARAM_ETA2',
                               'CS_GCDPARAM_ETA3',
                               'CS_POSITIONAL_CD_MAP',
                               'CEC_PARAM']
            if cs_command in cs_command_list and (value == 'NA' or value == 'nan'):
                print('pass ', str(cs_command))
                s = True
            else:
                for case in switch(str(cs_command)):

                    if case('CS_SYSTEM_PARAM'):
                        if type == temp.type and cs_command == temp.cs_command and limit_type == temp.limit_type:
                            if value == '' or value == 'nan':
                                msg = "CS_SYSTEM_PARAM can't be null"
                            else:
                                s = True
                        break

                    if case('CS_MASK_PARAM'):
                        if type == temp.type and cs_command == temp.cs_command and limit_type == temp.limit_type:
                            if value == '' or value == 'nan':
                                msg = "CS_MASK_PARAM can't be null"
                            else:
                                s = True
                        break

                    if case('CS_COLUMN_PARAM'):
                        if type == temp.type and cs_command == temp.cs_command and limit_type == temp.limit_type:
                            if value == '' or value == 'nan':
                                msg = "CS_COLUMN_PARAM can't be null"
                            else:
                                s = True
                        break

                    if case('CS_STRIPE_LAYER_COUNT'):
                        start = change_data_type(temp_option.start).trans_integer()
                        end = change_data_type(temp_option.end).trans_integer()
                        data = change_data_type(value).trans_integer()

                        if start[0] and end[0] and data[0]:
                            if start[1] <= data[1] <= end[1]:
                                s = True
                            else:
                                msg = 'CS_STRIPE_LAYER_COUNT out of range'
                        else:
                            msg = 'CS_STRIPE_LAYER_COUNT data type error'
                        break

                    if case('CS_SOAKING'):
                        start = change_data_type(temp_option.start).trans_integer()
                        end = change_data_type(temp_option.end).trans_integer()
                        data = change_data_type(value).trans_integer()

                        if start[0] and end[0] and data[0]:
                            if start[1] <= data[1] <= end[1]:
                                s = True
                            else:
                                msg = 'CS_SOAKING out of range'
                        else:
                            msg = 'CS_SOAKING data type error'
                        break

                    if case('CS_W_CH_SOAK'):
                        start = change_data_type(temp_option.start).trans_integer()
                        end = change_data_type(temp_option.end).trans_integer()
                        data = change_data_type(value).trans_integer()

                        if start[0] and end[0] and data[0]:
                            if start[1] <= data[1] <= end[1]:
                                s = True
                            else:
                                msg = 'CS_W_CH_SOAK out of range'
                        else:
                            msg = 'CS_W_CH_SOAK data type error'
                        break

                    if case('CS_IO_CH_WAIT'):
                        data = str(value)

                        if data in temp_option_dict['CS_IO_CH_WAIT']:
                            s = True
                        else:
                            s = False
                            msg = 'CS_IO_CH_WAIT error'
                        break

                    if case('CS_PROX'):
                        data = str(value)

                        if data in temp_option_dict['CS_PROX']:
                            s = True
                        else:
                            s = False
                            msg = 'CS_PROX error'
                        break

                    if case('CS_BASE_DOSE'):
                        start = change_data_type(temp_option.start).trans_integer()
                        end = change_data_type(temp_option.end).trans_integer()
                        data = change_data_type(value).trans_float()
                        CS_STRIPE_LAYER_COUNT_data_val = change_data_type(CS_STRIPE_data.value).trans_integer()

                        if start[0] and end[0] and data[0] and CS_STRIPE_LAYER_COUNT_data_val[0]:
                            if start[1] <= data[1] <= end[1] * CS_STRIPE_LAYER_COUNT_data_val[1]:
                                s = True
                            else:
                                msg = 'CS_BASE_DOSE out of range'
                        else:
                            msg = 'CS_BASE_DOSE data type error'
                        break

                    if case('CS_SIGMA1'):
                        start = change_data_type(temp_option.start).trans_integer()
                        end = change_data_type(temp_option.end).trans_integer()
                        data = change_data_type(value).trans_float()

                        if start[0] and end[0] and data[0]:
                            if start[1] <= data[1] <= end[1]:
                                s = True
                            else:
                                msg = 'CS_SIGMA1 out of range'
                        else:
                            msg = 'CS_SIGMA1 data type error'
                        break

                    if case('CS_ETA1'):
                        start = change_data_type(temp_option.start).trans_integer()
                        end = change_data_type(temp_option.end).trans_integer()
                        data = change_data_type(value).trans_float()

                        if start[0] and end[0] and data[0]:
                            if start[1] <= data[1] <= end[1]:
                                s = True
                            else:
                                msg = 'CS_ETA1 out of range'
                        else:
                            msg = 'CS_ETA1 data type error'
                        break

                    if case('CS_GCD_MESH_SIZE'):
                        data = str(value)

                        if data in temp_option_dict['CS_GCD_MESH_SIZE']:
                            s = True
                        else:
                            s = False
                            msg = 'CS_GCD_MESH_SIZE error'
                        break

                    if case('CS_KBR_PRX_MESH_SIZE'):
                        start = change_data_type(temp_option.start).trans_integer()
                        end = change_data_type(temp_option.end).trans_integer()
                        data = change_data_type(value).trans_integer()
                        CS_GCD_MESH_SIZE_data = change_data_type(CS_GCD_data.value).trans_integer()

                        if start[0] and end[0] and data[0] and CS_GCD_MESH_SIZE_data[0]:
                            if start[1] <= data[1] <= CS_GCD_MESH_SIZE_data[1] / end[1]:
                                s = True
                            else:
                                msg = 'CS_KBR_PRX_MESH_SIZE out of range'
                        else:
                            msg = 'CS_KBR_PRX_MESH_SIZE data type error'
                        break

                    if case('CS_KBR_SW'):
                        data = str(value)

                        if data in temp_option_dict['CS_KBR_SW']:
                            s = True
                        else:
                            s = False
                            msg = 'CS_KBR_SW error'
                        break

                    if case('CS_FEC_MODE'):
                        data = str(value)

                        if data in temp_option_dict['CS_FEC_MODE']:
                            s = True
                        else:
                            s = False
                            msg = 'CS_FEC_MODE error'
                        break

                    if case('CS_THETA1'):
                        start = change_data_type(temp_option.start).trans_float()
                        end = change_data_type(temp_option.end).trans_float()
                        data = change_data_type(value).trans_float()

                        if start[0] and end[0] and data[0]:
                            if start[1] <= data[1] <= end[1]:
                                s = True
                            else:
                                msg = 'CS_THETA1 out of range'
                        else:
                            msg = 'CS_THETA1 data type error'
                        break

                    if case('CS_SIGMAF1'):
                        end = change_data_type(temp_option.end).trans_integer()
                        data = change_data_type(value).trans_float()
                        CS_GCD_MESH_SIZE_data = change_data_type(CS_GCD_data.value).trans_integer()

                        if end[0] and data[0] and CS_GCD_MESH_SIZE_data[0]:
                            if CS_GCD_MESH_SIZE_data[1] <= data[1] <= end[1]:
                                s = True
                            else:
                                msg = 'CS_SIGMAF1 out of range'
                        else:
                            msg = 'CS_SIGMAF1 data type error'
                        break

                    if case('CS_LEC_MODE'):
                        data = str(value)

                        if data in temp_option_dict['CS_LEC_MODE']:
                            s = True
                        else:
                            s = False
                            msg = 'CS_LEC_MODE error'
                        break

                    if case('CS_GAMMA1'):
                        start = change_data_type(temp_option.start).trans_integer()
                        end = change_data_type(temp_option.end).trans_integer()
                        data = change_data_type(value).trans_float()

                        if start[0] and end[0] and data[0]:
                            if start[1] <= data[1] <= end[1]:
                                s = True
                            else:
                                msg = 'CS_GAMMA1 out of range'
                        else:
                            msg = 'CS_GAMMA1 data type error'
                        break

                    if case('CS_SIGMAL1'):
                        end = change_data_type(temp_option.end).trans_integer()
                        data = change_data_type(value).trans_float()
                        CS_GCD_MESH_SIZE_data = change_data_type(CS_GCD_data.value).trans_integer()

                        if end[0] and data[0] and CS_GCD_MESH_SIZE_data[0]:
                            if CS_GCD_MESH_SIZE_data[1] <= data[1] <= end[1]:
                                s = True
                            else:
                                msg = 'CS_SIGMAL1 out of range'
                        else:
                            msg = 'CS_SIGMAL1 data type error'
                        break

                    if case('CS_TEC_MODE'):
                        data = str(value)

                        if data in temp_option_dict['CS_TEC_MODE']:
                            s = True
                        else:
                            s = False
                            msg = 'CS_TEC_MODE error'
                        break

                    if case('CS_TEC_COEF_DC0'):
                        start = change_data_type(temp_option.start).trans_integer()
                        end = change_data_type(temp_option.end).trans_integer()
                        data = change_data_type(value).trans_float()

                        if start[0] and end[0] and data[0]:
                            if start[1] <= data[1] <= end[1]:
                                s = True
                            else:
                                msg = 'CS_TEC_COEF_DC0 out of range'
                        else:
                            msg = 'CS_TEC_COEF_DC0 data type error'
                        break

                    if case('CS_GCDPARAM_CD1'):
                        start = change_data_type(temp_option.start).trans_integer()
                        end = change_data_type(temp_option.end).trans_integer()
                        data = change_data_type(value).trans_float()

                        if start[0] and end[0] and data[0]:
                            if start[1] <= data[1] <= end[1] and data[1] != 0.0 and data[1] != 0:
                                s = True
                            else:
                                msg = 'CS_GCDPARAM_CD1 out of range'
                        else:
                            msg = 'CS_GCDPARAM_CD1 data type error'
                        break

                    if case('CS_GCDPARAM_CD2'):
                        start = change_data_type(temp_option.start).trans_integer()
                        end = change_data_type(temp_option.end).trans_integer()
                        data = change_data_type(value).trans_float()

                        if start[0] and end[0] and data[0]:
                            if start[1] <= data[1] <= end[1] and data[1] != 0.0 and data[1] != 0:
                                s = True
                            else:
                                msg = 'CS_GCDPARAM_CD2 out of range'
                        else:
                            msg = 'CS_GCDPARAM_CD2 data type error'
                        break

                    if case('CS_GCDPARAM_CD3'):
                        start = change_data_type(temp_option.start).trans_integer()
                        end = change_data_type(temp_option.end).trans_integer()
                        data = change_data_type(value).trans_float()

                        if start[0] and end[0] and data[0]:
                            if start[1] <= data[1] <= end[1] and data[1] != 0.0 and data[1] != 0:
                                s = True
                            else:
                                msg = 'CS_GCDPARAM_CD3 out of range'
                        else:
                            msg = 'CS_GCDPARAM_CD3 data type error'
                        break

                    if case('CS_GCDPARAM_BASEDOSE1'):
                        start = change_data_type(temp_option.start).trans_integer()
                        end = change_data_type(temp_option.end).trans_integer()
                        data = change_data_type(value).trans_float()
                        CS_STRIPE_LAYER_COUNT_data_val = change_data_type(CS_STRIPE_data.value).trans_integer()

                        if start[0] and end[0] and data[0] and CS_STRIPE_LAYER_COUNT_data_val[0]:
                            if start[1] <= data[1] <= end[1] * CS_STRIPE_LAYER_COUNT_data_val[1]:
                                s = True
                            else:
                                msg = 'CS_GCDPARAM_BASEDOSE1 out of range'
                        else:
                            msg = 'CS_GCDPARAM_BASEDOSE1 data type error'
                        break

                    if case('CS_GCDPARAM_BASEDOSE2'):
                        start = change_data_type(temp_option.start).trans_integer()
                        end = change_data_type(temp_option.end).trans_integer()
                        data = change_data_type(value).trans_float()
                        CS_STRIPE_LAYER_COUNT_data_val = change_data_type(CS_STRIPE_data.value).trans_integer()

                        if start[0] and end[0] and data[0] and CS_STRIPE_LAYER_COUNT_data_val[0]:
                            if start[1] <= data[1] <= end[1] * CS_STRIPE_LAYER_COUNT_data_val[1]:
                                s = True
                            else:
                                msg = 'CS_GCDPARAM_BASEDOSE2 out of range'
                        else:
                            msg = 'CS_GCDPARAM_BASEDOSE2 data type error'
                        break

                    if case('CS_GCDPARAM_BASEDOSE3'):
                        start = change_data_type(temp_option.start).trans_integer()
                        end = change_data_type(temp_option.end).trans_integer()
                        data = change_data_type(value).trans_float()
                        CS_STRIPE_LAYER_COUNT_data_val = change_data_type(CS_STRIPE_data.value).trans_integer()

                        if start[0] and end[0] and data[0] and CS_STRIPE_LAYER_COUNT_data_val[0]:
                            if start[1] <= data[1] <= end[1] * CS_STRIPE_LAYER_COUNT_data_val[1]:
                                s = True
                            else:
                                msg = 'CS_GCDPARAM_BASEDOSE3 out of range'
                        else:
                            msg = 'CS_GCDPARAM_BASEDOSE3 data type error'
                        break

                    if case('CS_GCDPARAM_ETA1'):
                        start = change_data_type(temp_option.start).trans_integer()
                        end = change_data_type(temp_option.end).trans_integer()
                        data = change_data_type(value).trans_float()

                        if start[0] and end[0] and data[0]:
                            if start[1] <= data[1] <= end[1]:
                                s = True
                            else:
                                msg = 'CS_GCDPARAM_ETA1 out of range'
                        else:
                            msg = 'CS_GCDPARAM_ETA1 data type error'
                        break

                    if case('CS_GCDPARAM_ETA2'):
                        start = change_data_type(temp_option.start).trans_integer()
                        end = change_data_type(temp_option.end).trans_integer()
                        data = change_data_type(value).trans_float()

                        if start[0] and end[0] and data[0]:
                            if start[1] <= data[1] <= end[1]:
                                s = True
                            else:
                                msg = 'CS_GCDPARAM_ETA2 out of range'
                        else:
                            msg = 'CS_GCDPARAM_ETA2 data type error'
                        break

                    if case('CS_GCDPARAM_ETA3'):
                        start = change_data_type(temp_option.start).trans_integer()
                        end = change_data_type(temp_option.end).trans_integer()
                        data = change_data_type(value).trans_float()

                        if start[0] and end[0] and data[0]:
                            if start[1] <= data[1] <= end[1]:
                                s = True
                            else:
                                msg = 'CS_GCDPARAM_ETA3 out of range'
                        else:
                            msg = 'CS_GCDPARAM_ETA3 data type error'
                        break

                    if case('CS_POSITIONAL_CD_MAP'):
                        data = str(value)
                        data_dat = data + '.dat'
                        data_prm = data + '.prm'
                        path_list = []
                        for dirPath, dirNames, fileNames in os.walk(Constant.CD_MAP_PATH):
                            for f in fileNames:
                                path_list.append(f)

                        _o = cd_map.objects.filter(cd_map_dat_name=data_dat, index_prm_name=data_prm,
                                                   is_delete=0).values(
                            'id')

                        if data_dat in path_list and data_prm in path_list and _o.count() == 1:
                            s = True
                            _id = _o[0]['id']
                            print('CS_POSITIONAL_CD_MAP =', _id)
                        else:
                            msg = 'CD MAP file name not found'
                        break

                    if case('CEC_PARAM'):
                        data = str(value)
                        data_txt = data + '.txt'
                        path_list = []
                        for dirPath, dirNames, fileNames in os.walk(Constant.CEC_PATH):
                            for f in fileNames:
                                path_list.append(f)

                        _o = cec.objects.filter(cec_name=data_txt, is_delete=0).values('id')

                        if data_txt in path_list and _o.count() == 1:
                            s = True
                            _id = _o[0]['id']
                            print('CEC_PARAM =', _id)
                        else:
                            msg = 'CEC file name not found'
                        break

                    if case('MDT'):
                        data = str(value)

                        if data in temp_option_dict['MDT']:
                            s = True
                        else:
                            s = False
                            msg = 'MDT error'
                        break

            return s, msg, _id
        except Exception as e:
            print(e)
            return False, "check_data error\n" + str(e), 0


@csrf_exempt
def unreleased_release(request):
    customer = request.POST.get('customer')
    tool = request.POST.get('tool')
    node = request.POST.get('node')
    tone = request.POST.get('tone')
    blank = request.POST.get('blank')
    grade = request.POST.get('grade')
    pattern_density = request.POST.get('pattern_density')
    layer = request.POST.get('layer')
    level = request.POST.get('level', 0)

    # 判断是否有空值
    unreleased_info_count = unreleased_info.objects.filter(customer=customer, tool=tool, node=node, tone=tone,
                                                           blank=blank, grade=grade,
                                                           pattern_density=pattern_density, layer=layer, is_delete=0
                                                           ).exclude(value='').count()

    temp_count = info_tree_template.objects.filter(
        Q(machine_type__contains='MS05') | Q(machine_type__contains='MS06') | Q(machine_type__contains='MS18') | Q(
            machine_type__contains='MS28')).exclude(is_delete=1).count()

    print(unreleased_info_count, temp_count)

    if unreleased_info_count != temp_count:
        data = {"success": False, "msg": "Value can't be null"}
        return JsonResponse(data, safe=False)

    # 判断 MDT=Y 但 MDT_LIST 没有资料
    unreleased_info_id = \
        unreleased_info.objects.filter(customer=customer, tool=tool, node=node, tone=tone, blank=blank, grade=grade,
                                       pattern_density=pattern_density, layer=layer, is_delete=0,
                                       cs_command='MDT').values('id', 'value')[0]
    print(unreleased_info_id)
    if unreleased_info_id['value'] == 'Y':
        unreleased_mdt_count = unreleased_mdt.objects.filter(unreleased_id=unreleased_info_id['id'],
                                                             is_delete=0).count()
        if unreleased_mdt_count == 0:
            data = {"success": False, "msg": "MDT value is 'Y'.  But not found data"}
            return JsonResponse(data, safe=False)

    # data = {"success": True, "msg": "Success"}
    # return JsonResponse(data, safe=False)

    _unre = unreleased_info.objects.filter(customer=customer, tool=tool, node=node, tone=tone, blank=blank, grade=grade,
                                           pattern_density=pattern_density, layer=layer, is_delete=0)
    group = _unre[0].group

    _o = release_check()

    _o.group = group
    _o.customer = customer
    _o.tool = tool
    _o.node = node
    _o.tone = tone
    _o.blank = blank
    _o.grade = grade
    _o.pattern_density = pattern_density
    _o.layer = layer
    _o.level = level
    _o.create_user = getCurrentSessionName(request)

    _s = unreleased_service()

    return _s.add_release_check(_o)


class unreleased_mdt_list(BaseView):

    def get(self, request):
        if request.method == 'GET':
            id = request.GET.get('id')
            lock = request.GET.get('lock')
            return render(request, 'info_tree/unreleased/infotree_unreleased_mdt_list.html',
                          {"unreleased_id": id, "lock": lock})

    def post(self, request):
        if request.method == 'POST':
            data = {}

            super().post(request)
            q = Q()
            q.connector = 'and'
            q.children.append(('is_delete', 0))
            # type 1:unreleased_info 2:unreleased_info_alta
            q.children.append(('type', 1))

            unreleased_id = request.POST.get('unreleased_id')

            if unreleased_id:
                q.children.append(('unreleased_id', unreleased_id))

            info_tree_data_list = unreleased_mdt.objects.filter(q).order_by('id').values()[
                                  self.startIndex: self.endIndex]

            data['total'] = unreleased_mdt.objects.filter(q).count()
            data['rows'] = list(info_tree_data_list)

            return JsonResponse(data, safe=False)


class unreleased_mdt_view(BaseView):

    def get(self, request):
        if request.method == 'GET':
            id = request.GET.get('id')
            _o = unreleased_mdt.objects.get(id=id)
            return render(request, 'info_tree/unreleased/infotree_unreleased_mdt_form.html', {"mdt": _o})


class unreleased_mdt_add(BaseView):

    def get(self, request):
        if request.method == 'GET':
            _o = unreleased_mdt()
            id = request.GET.get('unreleased_id')
            return render(request, 'info_tree/unreleased/infotree_unreleased_mdt_form.html',
                          {"unreleased_id": id, "mdt": _o, "method": "add"})

    def post(self, request):
        if request.method == 'POST':

            unreleased_id = request.POST.get('unreleased_id')
            cad_layer = request.POST.get('cad_layer')
            data_type = request.POST.get('data_type')
            writer_mdt = request.POST.get('writer_mdt')
            writer_dose = request.POST.get('writer_dose')

            if unreleased_id and cad_layer and data_type and writer_mdt and writer_dose:

                _o = unreleased_mdt()
                _o.type = 1
                _o.unreleased_id = unreleased_id
                _o.cad_layer = cad_layer
                _o.data_type = data_type
                _o.writer_mdt = writer_mdt
                _o.writer_dose = writer_dose

                _s = unreleased_service()

                return _s.add_mdt(_o)
            else:
                data = {"success": False, "msg": "Failed"}
                return JsonResponse(data, safe=False)


class unreleased_mdt_edit(BaseView):

    def get(self, request):
        if request.method == 'GET':
            id = request.GET.get('id')
            _o = unreleased_mdt.objects.get(id=id)
            return render(request, 'info_tree/unreleased/infotree_unreleased_mdt_form.html',
                          {"mdt": _o, "method": "edit"})

    def post(self, request):
        if request.method == 'POST':

            id = request.POST.get('id')
            cad_layer = request.POST.get('cad_layer')
            data_type = request.POST.get('data_type')
            writer_mdt = request.POST.get('writer_mdt')
            writer_dose = request.POST.get('writer_dose')

            if id and cad_layer and data_type and writer_mdt and writer_dose:

                _o = unreleased_mdt.objects.get(id=id)
                _o.cad_layer = cad_layer
                _o.data_type = data_type
                _o.writer_mdt = writer_mdt
                _o.writer_dose = writer_dose

                _s = unreleased_service()

                return _s.upd_mdt(_o)
            else:
                data = {"success": False, "msg": "Failed"}
                return JsonResponse(data, safe=False)


class unreleased_mdt_del(BaseView):
    def get(self, request):
        if request.method == 'GET':
            ids = request.GET.get('ids')

            _o = unreleased_mdt()
            _o.id = ids

            _s = unreleased_service()

            return _s.del_mdt(_o)
