import logging
import traceback
from datetime import datetime

from django.http import JsonResponse

from jdv.models import lot_info
from utilslibrary.base.base import BaseService
from utilslibrary.mes_webservice.mes_webservice import mes_op_start, mes_op_start_cancel, mes_op_comp
from utilslibrary.proxy.log_db_proxy import InvocationHandler, ProxyFactory
from utilslibrary.system_constant import Constant

log = logging.getLogger('log')


@ProxyFactory(InvocationHandler)
class jdvService(BaseService):

    def upd_release(self, s_num, f_num):
        return JsonResponse(
            {'code': 200, 'message': '%d lots Release Success, %d lots Release Fail' % (s_num, f_num)},
            safe=False)

    def upd_payment_mark(self, l_i):
        """标记支付状态"""
        dp_operation = Constant.MES_OPERATION_ID_ODR
        lot = lot_info.objects.get(pk=l_i.id)
        lot_id = lot.lot_id
        flag = lot_info.objects.filter(pk=l_i.id, payment_status=0).update(payment_status=1,
                                                                           payment_user_id=l_i.payment_user_id,
                                                                           payment_user_name=l_i.payment_user_name,
                                                                           payment_check_date=datetime.now())
        return JsonResponse({'code': 200, 'message': 'update success'}, safe=False)
        # if lot.release_status == 1:
        #     if mes_op_start(lot_id, dp_operation):  # op_start调用成功
        #         flag = lot_info.objects.filter(pk=l_i.id, payment_status=0).update(payment_status=1,
        #                                                                            payment_user_id=l_i.payment_user_id,
        #                                                                            payment_user_name=l_i.payment_user_name,
        #                                                                            payment_check_date=datetime.now())
        #         if flag:
        #             if not mes_op_comp(lot_id, dp_operation):
        #                 mes_op_start_cancel(lot_id, dp_operation)
        #                 return JsonResponse({'code': 400, 'message': '过站失败'}, safe=False)
        #             return JsonResponse({'code': 200, 'message': 'update success'}, safe=False)
        #         else:
        #             mes_op_start_cancel(lot_id, dp_operation)
        #             return JsonResponse({'code': 400, 'message': 'update fail'}, safe=False)
        #     else:
        #         return JsonResponse({'code': 400, 'message': 'op_start执行失败，过站失败'}, safe=False)
        # else:
        #     return JsonResponse({'code': 400, 'message': '请先进行release操作'}, safe=False)
