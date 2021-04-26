# coding=utf-8
import logging
import traceback

from django.db import transaction
from django.shortcuts import render
import json
from django.template.context_processors import request
from django.http.response import JsonResponse, FileResponse
from django.db.models.query_utils import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from making.models import convert_status, convert_operate_log
from utilslibrary.base.base import BaseView
from utilslibrary.system_constant import Constant
from jdv.models import lot_info,lot_trail
from jdv.service.lot_trail_service import LotTrailService
from jdv.model.lot_info_model import LotInfoModel

log = logging.getLogger('LOGGING')


class ConvertStatusView(BaseView):
    """lot时间线"""
    def get(self, request):
        return render(request, 'making_convert_status.html')

    def post(self, request):
        tip_no = request.POST.get('tip_no')
        lot_id = request.POST.get('lot')
        lt_list = lot_trail.objects.values().filter(is_delete=0,lot_id=lot_id).order_by('-create_time')
        _o = lot_info.objects.get(id=lot_id)
        _o_lot_info_model = LotInfoModel()
        _o_lot_info_model.Id = _o.id
        _o_lot_info_model.Lot_Id = _o.lot_id
        _o_lot_info_model.Tip_No = _o.tip_no
        _o_lot_info_model.Status = _o.status
        _o_lot_info_model.Status_Desc = _o.status_dec
        _o_lot_info_model.Convert_Status = _o.convert_status
        _o_lot_info_model.Convert_Status_Desc = _o.convert_status_dec
        data = {}
        data['lot_trail_list'] = list(lt_list)
        _temp = json.dumps(_o_lot_info_model, default=_o_lot_info_model.conver_to_dict)
        data['lot_info'] =json.loads(_temp)

        return JsonResponse(data, safe=False)
