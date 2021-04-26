import logging
import traceback
from datetime import datetime

from django.http import JsonResponse
from django.db import transaction

from jdv.models import lot_info
from utilslibrary.base.base import BaseService
from utilslibrary.proxy.log_db_proxy import InvocationHandler, ProxyFactory
from utilslibrary.system_constant import Constant
from jdv.models import lot_trail

from utilslibrary.utils.date_utils import getDateStr,getMilliSecond
from utilslibrary.utils.common_utils import getCurrentSessionID,getCurrentSessionName

log = logging.getLogger('log')


@ProxyFactory(InvocationHandler)
class LotTrailService(BaseService):

    #add lot_trail
    def insert_trail(self,user_id, user_name, lot_id,tip_no,stage,stage_desc,remark,is_error=0):
        _o = lot_trail()
        _o.lot_id = lot_id
        _o.stage = stage
        _o.stage_desc = stage_desc
        _o.stage_start_date = getDateStr()
        _o.create_date = getDateStr()
        _o.stage_start_date = getDateStr()
        _o.stage_end_date = getDateStr()
        _o.operate_date = getDateStr()
        _o.create_time = getMilliSecond()
        _o.operator_id = user_id
        _o.operator_name = user_name
        _o.remark = remark
        _o.tip_no = tip_no
        _o.is_error = is_error
        _o.save()

    # delete user by ids
    @transaction.atomic
    def del_lot_trail(self, obj):
        # return msg object
        data = {}
        data["success"] = False
        data["msg"] = "Failed"
        ids = obj.id
        if not ids:
            data["success"] = False
            data["msg"] = "Failed"
            return JsonResponse(data, safe=False)

        with transaction.atomic():
            id_list = ids.split(",")
            for id in id_list:
                if id:
                    _o = lot_trail.objects.get(id=id)
                    if _o:
                        # logic delete
                        _o.is_delete = 1
                        _o.save()

        data["success"] = True
        data["msg"] = "Success"
        return JsonResponse(data, safe=False)



