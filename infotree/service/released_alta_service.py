# coding:utf-8

from utilslibrary.proxy.log_db_proxy import ProxyFactory, InvocationHandler
from django.http.response import JsonResponse
from django.db import transaction
from utilslibrary.base.base import BaseService
from infotree.models import released_info_alta
from utilslibrary.utils.date_utils import getDateStr, getMilliSecond
from utilslibrary.utils.common_utils import getCurrentSessionID, getCurrentSessionName


@ProxyFactory(InvocationHandler)
class released_alta_service(BaseService):

    def del_released(self, released_data):
        data = {}
        data["success"] = False
        data["msg"] = "Failed"

        customer = released_data.customer
        tool = released_data.tool
        node = released_data.node
        tone = released_data.tone
        blank = released_data.blank
        grade = released_data.grade
        pattern_density = released_data.pattern_density
        layer = released_data.layer

        if not (customer and tool and node and tone and blank and grade and pattern_density and layer):
            data["success"] = False
            data["msg"] = "Failed"
            return JsonResponse(data, safe=False)

        with transaction.atomic():
            _o = released_info_alta.objects.filter(tool=tool,
                                                   customer=customer,
                                                   node=node,
                                                   tone=tone,
                                                   blank=blank,
                                                   grade=grade,
                                                   pattern_density=pattern_density,
                                                   layer=layer,
                                                   is_delete=0).update(is_delete=1)

        data["success"] = True
        data["msg"] = "Success"
        return JsonResponse(data, safe=False)
