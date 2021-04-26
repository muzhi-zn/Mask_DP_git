from django.db import transaction

from maintain.models import process_toolings, maintain_change_log
from utilslibrary.base.base import BaseService
from django.http import JsonResponse

from utilslibrary.proxy.log_db_proxy import ProxyFactory, InvocationHandler
from utilslibrary.utils.common_utils import getCurrentSessionName


@ProxyFactory(InvocationHandler)
class ProcessToolings(BaseService):

    def add_process_tooling(self, p_t, new_data, old_data, request):
        data = {}
        try:
            p_t.save()
            c_l = maintain_change_log()
            c_l.data_id = p_t.id
            c_l.table = 'Process Toolings'
            c_l.change_user = getCurrentSessionName(request)
            c_l.operation = 'Add'
            c_l.new_data = new_data
            c_l.old_data = old_data
            c_l.save()
            data['success'] = True
            data['message'] = 'success'
            return JsonResponse(data=data, safe=False)
        except Exception as e:
            data['success'] = False
            data['message'] = str(e)
            return JsonResponse(data=data, safe=False)

    def upt_process_tooling(self, p_t, new_data, old_data, request):
        data = {}
        try:
            p_t.save()
            c_l = maintain_change_log()
            c_l.data_id = p_t.id
            c_l.table = 'Process Toolings'
            c_l.change_user = getCurrentSessionName(request)
            c_l.operation = 'Edit'
            c_l.new_data = new_data
            c_l.old_data = old_data
            c_l.save()
            data['success'] = True
            data['message'] = 'success'
            return JsonResponse(data=data, safe=False)
        except Exception as e:
            data['success'] = False
            data['message'] = str(e)
            return JsonResponse(data=data, safe=False)

    def del_process_tooling(self, p_t, request):
        data = {}
        old_data = {}
        try:
            ids = p_t.id
            id_list = ids.split(',')
            with transaction.atomic():
                for id in id_list:
                    p_t = process_toolings.objects.get(id=id)
                    p_t.is_delete = 1
                    old_data['tech'] = p_t.tech
                    old_data['layer'] = p_t.layer
                    old_data['grade'] = p_t.grade
                    old_data['opc_tag'] = p_t.opc_tag
                    old_data['tone'] = p_t.tone
                    old_data['bias'] = p_t.bias
                    p_t.save()
                    c_l = maintain_change_log()
                    c_l.data_id = p_t.id
                    c_l.table = 'Process Toolings'
                    c_l.change_user = getCurrentSessionName(request)
                    c_l.operation = 'Delete'
                    c_l.new_data = ''
                    c_l.old_data = old_data
                    c_l.save()
            data['success'] = True
            data['msg'] = 'Delete Success'
            return JsonResponse(data, safe=False)
        except Exception as e:
            data['success'] = False
            data['msg'] = 'Delete Failed'
            print(e)
            return JsonResponse(data, safe=True)