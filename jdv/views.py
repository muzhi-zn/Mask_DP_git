# coding=utf-8
import logging
import traceback

from django.db import transaction
from django.shortcuts import render
from django.template.context_processors import request
from django.http.response import JsonResponse, FileResponse
from django.db.models.query_utils import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from jdv.models import mes_blank_code
from jdv.jobs import run_jobs
from jdv.models import lot_info
from datetime import datetime

from jdv.service.jdv_service import jdvService
from jdv.service.mapping_blankCode_service import MappingBlankCodeService
from maintain.models import maintain_change_log
from utilslibrary.base.base import BaseView
from utilslibrary.decorators.gen_trail_decorators import gen_trail
from utilslibrary.system_constant import Constant
from utilslibrary.utils.common_utils import getCurrentSessionName

log = logging.getLogger('LOGGING')


# Create your views here.
class jdvLotList(BaseView):

    def get(self, request):
        """跳转jdv service页面"""
        if request.method == 'GET':
            return render(request, 'jdv_lot_list.html')

    def post(self, request):
        """根据查询条件获取lot list"""
        if request.method == 'POST':
            user_id = request.session.get(Constant.SESSION_CURRENT_USER_ID)
            super().post(request)
            q = Q()
            q.connector = 'and'
            # q.children.append(('lot_owner_id', user_id))  # 归属客户
            q.children.append(('is_delete', 0))
            # q.children.append(('payment_status', 1))
            product_name = request.POST.get('product_name')  # 产品名
            if product_name:
                q.children.append(('product_name', product_name))
            tip_no = request.POST.get('tip_no')
            if tip_no:
                q.children.append(('tip_no', tip_no))
            query_date = request.POST.get('query_date')
            if query_date:
                start_date = datetime.strptime(query_date.split(' - ')[0], '%Y-%m-%d %H:%M:%S')
                end_date = datetime.strptime(query_date.split(' - ')[1], '%Y-%m-%d %H:%M:%S')
                q.children.append(('ready_date__gte', start_date))
                q.children.append(('ready_date__lte', end_date))
            lot_list = lot_info.objects.filter(q).values()[self.startIndex: self.endIndex]
            data = {}
            data['total'] = lot_info.objects.filter(q).count()
            data['rows'] = list(lot_list)
            return JsonResponse(data, safe=False)


class paymentCheckList(BaseView):
    """支付检查类"""

    def get(self, request):
        return render(request, 'jdv_payment_check_list.html')

    def post(self, request):
        """支付状况确认页面数据"""
        if request.method == 'POST':
            super().post(request)
            q = Q()
            q.connector = 'and'
            owner_name = request.POST.get('owner_name')  # 归属客户姓名
            if owner_name:
                q.children.append(('owner_name', owner_name))
            product_name = request.POST.get('product_name')
            if product_name:
                q.children.append(('product_name', product_name))
            lot = request.POST.get('lot')
            if lot:
                q.children.append(('lot', lot))
            p_c_list = lot_info.objects.filter(q).values('id', 'tip_no', 'product_name','mask_name', 'lot_id', 'lot_owner_id',
                                                         'lot_owner_name', 'expire_date', 'payment_status')[
                       self.startIndex: self.endIndex]
            data = {'total': lot_info.objects.filter(q).count(), 'rows': list(p_c_list)}
            print(data)
            return JsonResponse(data, safe=False)


@gen_trail('release', '测试release', '测试测试release')
def release_lot(request):
    """release lot"""
    dp_operation = Constant.MES_OPERATION_ID_JVW
    ids = request.POST.getlist('ids')
    sum = 0
    s1 = transaction.savepoint()
    for id in ids:
        flag = lot_info.objects.filter(pk=id, release_status=0).update(release_status=1)
        sum += flag
    return JsonResponse(
        {'code': 200, 'message': '%d lots Release Success, %d lots Release Fail' % (sum, len(ids) - sum)},
        safe=False)
    # for id in ids:
    #     lot_id = lot_info.objects.get(pk=id).lot_id
    #     if mes_op_start(lot_id, dp_operation):
    #         flag = lot_info.objects.filter(pk=id, release_status=0).update(release_status=1)
    #         if mes_op_comp(lot_id, dp_operation):
    #             sum += flag
    #             return JsonResponse(
    #                 {'code': 200, 'message': '%d lots Release Success, %d lots Release Fail' % (sum, len(ids) - sum)},
    #                 safe=False)
    #         else:
    #             mes_op_start_cancel(lot_id, dp_operation)
    #             transaction.savepoint_rollback(s1)
    #             return JsonResponse(
    #                 {'code': 400, 'message': '过站失败'}, safe=False)
    #     else:
    #         transaction.savepoint_rollback(s1)
    #         return JsonResponse({'code': 400, 'message': 'op_start执行失败，过站失败'}, safe=False)


@require_GET
def download_sop_file(request):
    file = open(Constant.TOOLING_FORM_DOWNLOAD_DIR + Constant.JDV_LOT_LIST_SOP_TEMPLATE, 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="jdv_Sop.pdf"'
    return response


@require_POST
@gen_trail('payment mask', '测试payment mask', '测试测试payment mask')
def payment_mark(request):
    """标记支付状态"""
    l_i = lot_info()
    id = request.POST.get('id')
    user_id = request.session.get(Constant.SESSION_CURRENT_USER_ID)
    user_name = request.session.get(Constant.SESSION_CURRENT_USER_LOGINNAME)
    l_i.id = int(id)
    l_i.payment_user_id = user_id
    l_i.payment_user_name = user_name
    return jdvService().upd_payment_mark(l_i)


class MappingBlankCodeList(BaseView):

    def get(self, request):
        return render(request, 'jdv_mapping_blank_code_list.html')

    def post(self, request):
        super().post(request)
        customer = request.POST.get('customer')
        design_rule = request.POST.get('design_rule')
        layer_name = request.POST.get('layer_name')
        mask_type = request.POST.get('mask_type')
        wave_lenght = request.POST.get('WAVELENGHT')
        query_set = mes_blank_code.objects.filter(is_delete=0)
        if customer:
            query_set = query_set.filter(customer=customer)
        if design_rule:
            query_set = query_set.filter(design_rule=design_rule)
        if layer_name:
            query_set = query_set.filter(layer_name=layer_name)
        if mask_type:
            query_set = query_set.filter(mask_type=mask_type)
        if wave_lenght:
            query_set = query_set.filter(wave_lenght=wave_lenght)
        data = {}
        data['total'] = query_set.count()
        data['rows'] = list(query_set.values()[self.startIndex: self.endIndex])
        return JsonResponse(data, safe=False)


class MappingBlankCodeView(BaseView):

    def get(self, request):
        id = request.GET.get('id')
        print(id)
        if id:
            b_c = mes_blank_code.objects.get(id=id)
            return render(request, 'jdv_mapping_blank_code_form.html', {'method': 'view', 'b_c': b_c})
        else:
            b_c = mes_blank_code()
            return render(request, 'jdv_mapping_blank_code_form.html', {'method': 'view', 'b_c': b_c})


class MappingBlankCodeAdd(BaseView):

    def get(self, request):
        return render(request, 'jdv_mapping_blank_code_form.html', {'method': 'add', 'b_c': mes_blank_code()})

    def post(self, request):
        bc = mes_blank_code()
        bc.seq = request.POST.get('seq')
        bc.customer = request.POST.get('customer')
        bc.design_rule = request.POST.get('design_rule')
        bc.layer_name = request.POST.get('layer_name')
        bc.mask_type = request.POST.get('mask_type')
        bc.tone = request.POST.get('tone')
        bc.wave_lenght = request.POST.get('wave_lenght')
        bc.blank_code = request.POST.get('blank_code')
        bc.grade_from = request.POST.get('grade_from')
        bc.grade_to = request.POST.get('grade_to')
        bc.part_no = request.POST.get('part_no')
        bc.blank = request.POST.get('blank')
        c_l = maintain_change_log()
        new_data = {}
        new_data['seq'] = request.POST.get('seq')
        new_data['customer'] = request.POST.get('customer')
        new_data['design_rule'] = request.POST.get('design_rule')
        new_data['layer_name'] = request.POST.get('layer_name')
        new_data['mask_type'] = request.POST.get('mask_type')
        new_data['tone'] = request.POST.get('tone')
        new_data['wave_lenght'] = request.POST.get('wave_lenght')
        new_data['blank_code'] = request.POST.get('blank_code')
        new_data['grade_from'] = request.POST.get('grade_from')
        new_data['grade_to'] = request.POST.get('grade_to')
        new_data['part_no'] = request.POST.get('part_no')
        new_data['blank'] = request.POST.get('blank')
        c_l.new_data = new_data
        c_l.table = 'Blank Code'
        c_l.change_user = getCurrentSessionName(request)
        c_l.operation = 'Add'
        return MappingBlankCodeService().add_mapping_blank_code(bc, c_l)


class MappingBlankCodeDel(BaseView):
    def get(self, request):
        ids = request.GET.get('ids')
        print(ids)
        bc = mes_blank_code()
        bc.id = ids
        return MappingBlankCodeService().del_mapping_blank_code(bc, request)


class MappingBlankCodeEdit(BaseView):
    def get(self, request):
        id = request.GET.get('id')
        b_c = mes_blank_code.objects.get(id=id)
        return render(request, 'jdv_mapping_blank_code_form.html', {'method': 'edit', 'b_c': b_c})

    def post(self, request):
        bc = mes_blank_code()
        id = request.POST.get('id')
        bc = mes_blank_code.objects.get(pk=id)
        old_data = {}
        old_data['seq'] = bc.seq
        old_data['customer'] = bc.customer
        old_data['design_rule'] = bc.design_rule
        old_data['layer_name'] = bc.layer_name
        old_data['mask_type'] = bc.mask_type
        old_data['tone'] = bc.tone
        old_data['wave_lenght'] = bc.wave_lenght
        old_data['blank_code'] = bc.blank_code
        old_data['grade_from'] = bc.grade_from
        old_data['grade_to'] = bc.grade_to
        old_data['part_no'] = bc.part_no
        old_data['blank'] = bc.blank
        bc.seq = request.POST.get('seq')
        bc.customer = request.POST.get('customer')
        bc.design_rule = request.POST.get('design_rule')
        bc.layer_name = request.POST.get('layer_name')
        bc.mask_type = request.POST.get('mask_type')
        bc.tone = request.POST.get('tone')
        bc.wave_lenght = request.POST.get('wave_lenght')
        bc.blank_code = request.POST.get('blank_code')
        bc.grade_from = request.POST.get('grade_from')
        bc.grade_to = request.POST.get('grade_to')
        bc.part_no = request.POST.get('part_no')
        bc.blank = request.POST.get('blank')
        new_data = {}
        new_data['seq'] = request.POST.get('seq')
        new_data['customer'] = request.POST.get('customer')
        new_data['design_rule'] = request.POST.get('design_rule')
        new_data['layer_name'] = request.POST.get('layer_name')
        new_data['mask_type'] = request.POST.get('mask_type')
        new_data['tone'] = request.POST.get('tone')
        new_data['wave_lenght'] = request.POST.get('wave_lenght')
        new_data['blank_code'] = request.POST.get('blank_code')
        new_data['grade_from'] = request.POST.get('grade_from')
        new_data['grade_to'] = request.POST.get('grade_to')
        new_data['part_no'] = request.POST.get('part_no')
        new_data['blank'] = request.POST.get('blank')
        c_l = maintain_change_log()
        c_l.data_id = id
        c_l.operation = 'Edit'
        c_l.change_user = getCurrentSessionName(request)
        c_l.table = 'Blank Code'
        c_l.new_data = new_data
        c_l.old_data = old_data
        return MappingBlankCodeService().add_mapping_blank_code(bc, c_l)


@csrf_exempt
def check_length(request):
    blank_code = request.POST.get('blank_code')
    if len(blank_code) != 2:
        return JsonResponse({'success': False})
    else:
        return JsonResponse({'success': True})


run_jobs()  # 执行定时任务
