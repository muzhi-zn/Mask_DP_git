import functools
import logging
from datetime import datetime

from jdv.models import lot_trail
from utilslibrary.system_constant import Constant

log = logging.getLogger('log')


def gen_trail(stage, stage_desc, remark):
    """生成轨迹信息"""

    def wrapper(func):
        @functools.wraps(func)
        def in_func(request, *args, **kwargs):
            stage_start_date = datetime.now()
            fn = func(request, *args, **kwargs)
            stage_end_date = datetime.now()
            user_id = request.session.get(Constant.SESSION_CURRENT_USER_ID)
            user_name = request.session.get(Constant.SESSION_CURRENT_USER_LOGINNAME)
            lot_id = request.POST.get('id')
            ids = request.POST.getlist('ids')
            tip_no = request.POST.get('tip_no')
            if lot_id:
                operator_date = datetime.now()
                lot_trail.objects.create(lot_id=lot_id, stage=stage, stage_desc=stage_desc,
                                         stage_start_date=stage_start_date, stage_end_date=stage_end_date,
                                         operator_id=user_id, operator_name=user_name, operate_date=operator_date,
                                         remark=remark)
            if ids:
                for id in ids:
                    operator_date = datetime.now()
                    lot_trail.objects.create(lot_id=id, stage=stage, stage_desc=stage_desc,
                                             stage_start_date=stage_start_date, stage_end_date=stage_end_date,
                                             operator_id=user_id, operator_name=user_name, operate_date=operator_date,
                                             remark=remark)
            return fn
        return in_func

    return wrapper

