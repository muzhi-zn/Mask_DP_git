# coding:utf-8
"""system/role/ process method

"""
import traceback

from maintain.models import maintain_change_log
from utilslibrary.proxy.log_db_proxy import ProxyFactory, InvocationHandler
from django.http.response import HttpResponseRedirect, JsonResponse
from django.contrib.sessions.models import Session
from django.db import transaction

from django.db.models import F, Q
from django.db import transaction

from django.utils import timezone

from utilslibrary.system_constant import Constant
from utilslibrary.base.base import BaseService
from machine.models import machine_basic, machine_script_templates, writer_mapping
from utilslibrary.utils.common_utils import getCurrentSessionName


@ProxyFactory(InvocationHandler)
class MachineService(BaseService):
    def add_machine(self, machine_basic):
        # return msg object
        data = {}
        try:
            machine_basic.save()
            data["success"] = True
            data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    def upd_machine(self, machine_basic):
        data = {}
        try:
            machine_basic.save()
            data["success"] = True
            data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    # delete machine by ids
    def del_machine(self, obj):
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
                    _o = machine_basic.objects.get(id=id)
                    _o.is_delete = 1
                    _o.save()
                    # _o = machine_basic.objects.get(id=id)
                    # _o.delete()

        data["success"] = True
        data["msg"] = "Success"
        return JsonResponse(data, safe=False)


@ProxyFactory(InvocationHandler)
class WriterMappingService(BaseService):

    def add_writer_mapping(self, writer_mapping, c_l):
        """新增writer_mapping"""
        data = {}
        try:
            writer_mapping.save()
            c_l.data_id = writer_mapping.id
            c_l.save()
            data["success"] = True
            data["msg"] = "Add Success"
        except Exception as e:
            traceback.print_exc()
            data["success"] = False
            data["msg"] = "Add Failed"

        return JsonResponse(data, safe=False)

    def upd_writer_mapping(self, writer_mapping):
        """修改writer_mapping"""
        data = {}
        try:
            writer_mapping.save()
            data["success"] = True
            data["msg"] = "Edit Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Edit Failed"

        return JsonResponse(data, safe=False)

    def del_writer_mapping(self, wm, request):
        """删除writer_mapping"""
        ids = wm.id
        id_arr = ids.split(',')
        with transaction.atomic():
            for id in id_arr:
                wm = writer_mapping.objects.get(pk=id)
                old_data = {}
                old_data['seq'] = wm.seq
                old_data['customer'] = wm.customer
                old_data['design_rule'] = wm.design_rule
                old_data['product'] = wm.product
                old_data['layer_name'] = wm.layer_name
                old_data['product_type'] = wm.product_type
                old_data['grade_from'] = wm.grade_from
                old_data['grade_to'] = wm.grade_to
                old_data['mask_type'] = wm.mask_type
                old_data['tone'] = wm.tone
                old_data['machine_id'] = wm.machine_id
                old_data['exp_tool'] = wm.exp_tool
                old_data['comment'] = wm.comment
                old_data['book_user_id'] = wm.book_user_id
                old_data['book_user_name'] = wm.book_user_name
                old_data['book_time'] = wm.book_time
                old_data['info_tree_tool_id'] = wm.info_tree_tool_id
                old_data['catalog_tool_id'] = wm.catalog_tool_id
                c_l = maintain_change_log()
                c_l.operation = 'Delete'
                c_l.change_user = getCurrentSessionName(request)
                c_l.table = 'Writer Mapping'
                c_l.data_id = id
                c_l.old_data = old_data
                c_l.save()
                wm.is_delete = 1
                wm.save()
        return JsonResponse({'success': True, 'msg': 'Delete Success'}, safe=False)
