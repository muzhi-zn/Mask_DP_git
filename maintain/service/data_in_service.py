from django.db import transaction

from maintain.models import customer_ftp_account, maintain_change_log
from utilslibrary.base.base import BaseService
from django.http import JsonResponse

from utilslibrary.proxy.log_db_proxy import ProxyFactory, InvocationHandler
from utilslibrary.utils.common_utils import getCurrentSessionName
from maintain.models import data_in_table

@ProxyFactory(InvocationHandler)
class DataInService(BaseService):
    def pass_data_in(self, c_f, request):
        data = {}
        old_data = {}
        try:
            ids = c_f.id
            id_list = ids.split(',')
            with transaction.atomic():
                for id in id_list:
                    c_f = data_in_table.objects.get(id=id)
                    c_f.md5_pass = 'Y'
                    old_data['customer'] = c_f.customer
                    old_data['product_name'] = c_f.product_name
                    old_data['file_name_serial'] = c_f.file_name_serial
                    old_data['file_size'] = c_f.file_size
                    old_data['md5sum'] = c_f.md5sum
                    old_data['status'] = c_f.status
                    old_data['is_delete'] = c_f.is_delete
                    old_data['start_time'] = c_f.start_time
                    old_data['end_time'] = c_f.end_time
                    old_data['date'] = c_f.date
                    c_f.save()
                    c_l = maintain_change_log()
                    c_l.data_id = c_f.id
                    c_l.table = 'Customer Data In'
                    c_l.change_user = getCurrentSessionName(request)
                    c_l.operation = 'Pass'
                    c_l.new_data = ''
                    c_l.old_data = old_data
                    c_l.save()
            data['success'] = True
            data['msg'] = 'MD5SUM Pass Success'
            return JsonResponse(data, safe=False)
        except Exception as e:
            data['success'] = False
            data['msg'] = 'MD5SUM Pass Failed'
            print(e)
            return JsonResponse(data, safe=True)
    def cancel_pass_data_in(self, c_f, request):
        data = {}
        old_data = {}
        try:
            ids = c_f.id
            id_list = ids.split(',')
            with transaction.atomic():
                for id in id_list:
                    c_f = data_in_table.objects.get(id=id)
                    c_f.md5_pass = ''
                    old_data['customer'] = c_f.customer
                    old_data['product_name'] = c_f.product_name
                    old_data['file_name_serial'] = c_f.file_name_serial
                    old_data['file_size'] = c_f.file_size
                    old_data['md5sum'] = c_f.md5sum
                    old_data['status'] = c_f.status
                    old_data['is_delete'] = c_f.is_delete
                    old_data['start_time'] = c_f.start_time
                    old_data['end_time'] = c_f.end_time
                    old_data['date'] = c_f.date
                    c_f.save()
                    c_l = maintain_change_log()
                    c_l.data_id = c_f.id
                    c_l.table = 'Customer Data In'
                    c_l.change_user = getCurrentSessionName(request)
                    c_l.operation = 'Pass'
                    c_l.new_data = ''
                    c_l.old_data = old_data
                    c_l.save()
            data['success'] = True
            data['msg'] = 'MD5SUM Pass Cancel Success'
            return JsonResponse(data, safe=False)
        except Exception as e:
            data['success'] = False
            data['msg'] = 'MD5SUM Pass Cancel Failed'
            print(e)
            return JsonResponse(data, safe=True)