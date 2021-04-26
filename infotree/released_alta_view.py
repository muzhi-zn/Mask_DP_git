# coding=utf-8
import json
import os
import time
import pandas as pd
import xlwt
from django.db import connection
from django.db.models import Q
from django.http.response import JsonResponse, HttpResponse, FileResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from infotree.models import released_info_alta, released_mdt, info_tree_data_import_temp, tree, tree_option
from infotree.models import tree, tree_option, info_tree_template, info_tree_template_option, cd_map, cec
from infotree.service.released_alta_service import released_alta_service
from utilslibrary.base.base import BaseView
from django.db import transaction
from system.models import upload_info
from utilslibrary.utils.date_utils import getDateStr, getMilliSecond
from utilslibrary.utils.common_utils import getCurrentSessionID
from Mask_DP.settings import PROJECT_NAME


class released_alta_list(BaseView):

    def get(self, request):
        if request.method == 'GET':
            return render(request, 'info_tree/released_alta/infotree_released_alta_list.html')

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
            level = request.POST.get('s_level')

            if customer and tool and node and tone and blank and grade and pattern_density and layer and level:
                q.children.append(('customer', customer))
                q.children.append(('tool', tool))
                q.children.append(('node', node))
                q.children.append(('tone', tone))
                q.children.append(('blank', blank))
                q.children.append(('grade', grade))
                q.children.append(('pattern_density', pattern_density))
                q.children.append(('layer', layer))
                q.children.append(('level', level))

                info_tree_datalist = released_info_alta.objects.filter(q).order_by('id').values()[
                                     self.startIndex: self.endIndex]

                data['total'] = released_info_alta.objects.filter(q).count()
                data['rows'] = list(info_tree_datalist)

                return JsonResponse(data, safe=False)
            else:
                data['total'] = 0
                data['rows'] = []

                return JsonResponse(data, safe=False)


class released_alta_view(BaseView):

    def get(self, request):
        id = request.GET.get("id")
        if not id:
            return render(request, 'info_tree/released/infotree_released_form.html')
        else:
            _o = released_info_alta.objects.get(id=id)
            return render(request, 'info_tree/released/infotree_released_form.html', {"released": _o})


class released_alta_del(BaseView):

    def get(self, request):
        customer = request.GET.get('customer')
        tool = request.GET.get('tool')
        node = request.GET.get('node')
        tone = request.GET.get('tone')
        blank = request.GET.get('blank')
        grade = request.GET.get('grade')
        pattern_density = request.GET.get('pattern_density')
        layer = request.GET.get('layer')

        _o = released_info_alta()
        _o.customer = customer
        _o.tool = tool
        _o.node = node
        _o.tone = tone
        _o.blank = blank
        _o.grade = grade
        _o.pattern_density = pattern_density
        _o.layer = layer

        _s = released_alta_service()

        return _s.del_released(_o)


def released_alta_tree_json(request):
    tree_type = int(request.GET.get('tree_type'))
    j_list = []
    customer_list = released_info_alta.objects.filter(lock=tree_type, is_delete=0).values(
        'customer').distinct().order_by('customer')
    for customer in customer_list:
        # Tool
        tool_list = released_info_alta.objects.filter(customer=customer['customer']).values(
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
            node_list = released_info_alta.objects.filter(lock=tree_type, is_delete=0, tool=tool['tool'],
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
                tone_list = released_info_alta.objects.filter(lock=tree_type, is_delete=0, tool=tool['tool'],
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
                    blank_list = released_info_alta.objects.filter(lock=tree_type, is_delete=0,
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
                        grade_list = released_info_alta.objects.filter(lock=tree_type, is_delete=0,
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
                            pattern_density_list = released_info_alta.objects.filter(lock=tree_type, is_delete=0,
                                                                                     tool=tool['tool'],
                                                                                     node=node['node'],
                                                                                     tone=tone['tone'],
                                                                                     blank=blank['blank'],
                                                                                     grade=grade['grade'],
                                                                                     customer=customer[
                                                                                         'customer']).values(
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
                                layer_list = released_info_alta.objects.filter(lock=tree_type, is_delete=0,
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
                                                  "children": [],
                                                  "tree_info_8": tree_info_8}

                                    j_list[customer_no]['children'][tool_no]['children'][node_no]['children'][tone_no][
                                        'children'][blank_no][
                                        'children'][grade_no]['children'][pattern_density_no]['children'].append(
                                        layer_dict)
                                    layer_no = len(
                                        j_list[customer_no]['children'][tool_no]['children'][node_no]['children'][
                                            tone_no][
                                            'children']
                                        [blank_no]['children'][grade_no]['children'][pattern_density_no][
                                            'children']) - 1
                                    # level
                                    level_list = released_info_alta.objects.filter(lock=tree_type, is_delete=0,
                                                                                   tool=tool['tool'],
                                                                                   node=node['node'],
                                                                                   tone=tone['tone'],
                                                                                   blank=blank['blank'],
                                                                                   grade=grade['grade'],
                                                                                   pattern_density=pattern_density[
                                                                                       'pattern_density'],
                                                                                   customer=customer[
                                                                                       'customer'],
                                                                                   layer=layer['layer']).values(
                                        'level').distinct()
                                    if level_list.count() == 0:
                                        continue

                                    tree_info_9 = [customer['customer'], tool['tool'], node['node'], tone['tone'],
                                                   blank['blank'], grade['grade'],
                                                   pattern_density['pattern_density'], layer['layer']]
                                    for level in level_list:
                                        level_dict = {"level": 9,
                                                      "name": level['level'],
                                                      "text": level['level'],
                                                      "tree_info_9": tree_info_9}

                                        j_list[customer_no]['children'][tool_no]['children'][node_no]['children'][
                                            tone_no][
                                            'children'][blank_no][
                                            'children'][grade_no]['children'][pattern_density_no]['children'][layer_no][
                                            'children'].append(
                                            level_dict)

    k = json.dumps(j_list)

    return HttpResponse(k)


@csrf_exempt
def released_alta_export(request):
    tool = request.GET.get('s_tool')
    node = request.GET.get('s_node')
    tone = request.GET.get('s_tone')
    blank = request.GET.get('s_blank')
    grade = request.GET.get('s_grade')
    pattern_density = request.GET.get('s_pattern_density')
    layer = request.GET.get('s_layer')

    path, excel_name = write_excel(tool, node, tone, blank, grade, pattern_density, layer)

    # _o = info_tree_data_export_log()
    # _o.tool = tool
    # _o.node = node
    # _o.tone = tone
    # _o.blank = blank
    # _o.grade = grade
    # _o.pattern_density = pattern_density
    # _o.layer = layer
    # _o.file_name = excel_name
    # _o.file_path = path

    # Unreleased_alta_service().add_export_log(_o)

    file = open(path, 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="' + excel_name + '"'
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
def write_excel(tool, node, tone, blank, grade, pattern_density, layer):
    f = xlwt.Workbook()  # 建立工作簿
    '''建立第一個sheet:sheet1'''
    sheet1 = f.add_sheet(u'released_alta', cell_overwrite_ok=True)  # 建立sheet

    tree_data = released_info_alta.objects.filter(tool=tool, node=node, tone=tone, blank=blank, grade=grade,
                                                  pattern_density=pattern_density, layer=layer, is_delete=0)

    excel_head_name = [u'tool', u'node', u'tone', u'blank', u'grade', u'pattern_density', u'layer', u'type',
                       u'item', u'value', u'version']
    row = [excel_head_name]
    for data in tree_data:
        data_list = [data.tool, data.node, data.tone, data.blank, data.grade, data.pattern_density, data.layer,
                     data.type, data.item, data.value, data.version]
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


class released_alta_mdt_list(BaseView):

    def get(self, request):
        if request.method == 'GET':
            id = request.GET.get('id')
            return render(request, 'info_tree/released_alta/infotree_released_alta_mdt_list.html',
                          {"released_alta_id": id})

    def post(self, request):
        if request.method == 'POST':
            data = {}

            super().post(request)
            q = Q()
            q.connector = 'and'
            q.children.append(('is_delete', 0))
            # type 1:released_info 2:released_info_alta
            q.children.append(('type', 2))

            released_alta_id = request.POST.get('released_alta_id')

            if released_alta_id:
                q.children.append(('released_id', released_alta_id))

            info_tree_datalist = released_mdt.objects.filter(q).order_by('id').values()[
                                 self.startIndex: self.endIndex]

            data['total'] = released_mdt.objects.filter(q).count()
            data['rows'] = list(info_tree_datalist)

            return JsonResponse(data, safe=False)
