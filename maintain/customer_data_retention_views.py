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
from infotree.models import unreleased_info, info_tree_data_export_log, info_tree_data_import_temp, tree, tree_option, \
    maintain_table
from infotree.models import tree, tree_option, info_tree_template, info_tree_template_option, cd_map, cec
#from infotree.service.maintain_service import Maintain_Service
#from tooling.service.tooling_service import switch
from utilslibrary.base.base import BaseView
from utilslibrary.system_constant import Constant
from django.db import transaction
from system.models import upload_info
from utilslibrary.utils.date_utils import getDateStr, getMilliSecond
from utilslibrary.utils.common_utils import getCurrentSessionID
from Mask_DP.settings import PROJECT_NAME
from maintain.models import ftp_data_table,retention_data_table
from datetime import datetime
from maintain.service.customer_data_retention_service import CustomerDataRetentionService
class customer_data_retention_list(BaseView):

    def get(self, request):
        if request.method == 'GET':
            return render(request, 'maintain/customer_data_retention.html')

    def post(self, request):
        if request.method == 'POST':
            data = {}

            super().post(request)
            q = Q()
            q.connector = 'and'
            q.children.append(('is_delete', 0))

            customer = request.POST.get('s_customer')
            product_name = request.POST.get('s_product_name')
            date = request.POST.get('s_date')

            if customer and product_name and date:
                q.children.append(('customer', customer))
                q.children.append(('product_name', product_name))
                q.children.append(('date', date))

                info_tree_datalist = retention_data_table.objects.filter(q).order_by('id').values()[
                                     self.startIndex: self.endIndex]

                data['total'] = retention_data_table.objects.filter(q).count()
                data['rows'] = list(info_tree_datalist)

                return JsonResponse(data, safe=False)
            else:
                data['total'] = 0
                data['rows'] = []

                return JsonResponse(data, safe=False)


class customer_data_retention_pass(BaseView):

    def get(self, request):
        data = {}
        ids = request.GET.get('ids')
        c_f = CustomerDataRetentionService()
        c_f.id = ids
        return CustomerDataRetentionService().pass_data_in(c_f, request)

class customer_data_retention_pass_cancel(BaseView):

    def get(self, request):
        data = {}
        ids = request.GET.get('ids')
        c_f = CustomerDataRetentionService()
        c_f.id = ids
        return CustomerDataRetentionService().cancel_pass_data_in(c_f, request)


def customer_data_retention_tree_json(request):
    q = Q()
    q.connector = 'and'
    q.children.append(('is_delete', 0))
    customer = request.GET.get('customer')  # 产品名
    if customer:
        q.children.append(('customer', customer))
    product_name = request.GET.get('product_name')  # 产品名
    if product_name:
        q.children.append(('product_name', product_name))
    if request.GET.get('start_date'):
        start_time = int(request.GET.get('start_date'))
        q.children.append(('date__gte', start_time))
    if request.GET.get('end_date'):
        end_time = int(request.GET.get('end_date'))
        q.children.append(('date__lte', end_time))
#    tree_type = int(request.GET.get('tree_type'))
    j_list = []

    # Tool
    customer_list = retention_data_table.objects.filter(q).order_by('customer').values(
        'customer').distinct()
    print(customer_list)

    print(customer_list.query)
    for customer in customer_list:
        customer_dict = {"level": 1,
                     "name": customer['customer'],
                     "text": customer['customer'],
                     "children": []}

        j_list.append(customer_dict)
        customer_no = len(j_list) - 1

        # Node
        q.children.append(('customer', customer['customer']))
        product_name_list = retention_data_table.objects.filter(q).values(
            'product_name').distinct()
        q.children.remove(('customer', customer['customer']))
        print(product_name_list)
        if product_name_list.count() == 0:
            continue

        tree_info_2 = [customer['customer']]
        for product_name in product_name_list:
            product_name_dict = {"level": 2,
                         "name": product_name['product_name'],
                         "text": product_name['product_name'],
                         "tree_info_2": tree_info_2,
                         "children": []}

            j_list[customer_no]['children'].append(product_name_dict)
            product_name_no = len(j_list[customer_no]['children']) - 1

            # Tone
            q.children.append(('product_name',  product_name['product_name']))
            date_list = retention_data_table.objects.filter(q).values('date').distinct()
            q.children.remove(('product_name', product_name['product_name']))
            print(date_list)

            if date_list.count() == 0:
                continue

            tree_info_3 = [customer['customer'], product_name['product_name']]
            for date in date_list:
                date_dict = {"level": 3,
                             "name": date['date'],
                             "text": date['date'],
                             "tree_info_3": tree_info_3}

                j_list[customer_no]['children'][product_name_no]['children'].append(date_dict)
                #date_no = len(j_list[customer_no]['children'][product_name_no]['children']) - 1



    k = json.dumps(j_list)

    return HttpResponse(k)


@csrf_exempt
def customer_data_retention_export(request):
    tool = request.GET.get('s_tool')
    node = request.GET.get('s_node')
    tone = request.GET.get('s_tone')
    blank = request.GET.get('s_blank')
    grade = request.GET.get('s_grade')
    pattern_density = request.GET.get('s_pattern_density')
    layer = request.GET.get('s_layer')

    path, excel_name = write_excel(tool, node, tone, blank, grade, pattern_density, layer)

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

#    Maintain_Service().add_export_log(_o)

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
    sheet1 = f.add_sheet(u'Mask Layer', cell_overwrite_ok=True)  # 建立sheet

    tree_data = unreleased_info.objects.filter(tool=tool, node=node, tone=tone, blank=blank, grade=grade,
                                              pattern_density=pattern_density, layer=layer, is_delete=0)

    excel_head_name = [u'tool', u'node', u'tone', u'blank', u'grade', u'pattern_density', u'layer', u'type',
                       u'cs_command', u'value', u'temp_version', u'version']
    row = [excel_head_name]
    for data in tree_data:
        data_list = [data.tool, data.node, data.tone, data.blank, data.grade, data.pattern_density, data.layer,
                     data.type, data.cs_command, data.value, data.temp_version, data.version]
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
@csrf_exempt
def get_customer(request):
    customer = retention_data_table.objects.filter(is_delete='0')
    customer_list = list()
    for code_ in customer:
        if code_.customer not in customer_list:
            customer_list.append(code_.customer)
    return JsonResponse({'success': True, 'data': customer_list}, safe=False)