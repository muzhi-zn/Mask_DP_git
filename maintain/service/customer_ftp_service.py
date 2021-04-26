from django.db import transaction

from maintain.models import customer_ftp_account, maintain_change_log
from utilslibrary.base.base import BaseService
from django.http import JsonResponse

from utilslibrary.proxy.log_db_proxy import ProxyFactory, InvocationHandler
from utilslibrary.utils.common_utils import getCurrentSessionName


@ProxyFactory(InvocationHandler)
class CustomerFTPs(BaseService):

    def add_customer_ftp(self, c_f, new_data, old_data, request):
        data = {}
        try:
            c_f.save()
            c_l = maintain_change_log()
            c_l.data_id = c_f.id
            c_l.table = 'Customer FTP Account'
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

    def upt_customer_ftp(self, c_f, new_data, old_data, request):
        data = {}
        try:
            c_f.save()
            c_l = maintain_change_log()
            c_l.data_id = c_f.id
            c_l.table = 'Customer FTP Account'
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

    def del_customer_ftp(self, c_f, request):
        data = {}
        old_data = {}
        try:
            ids = c_f.id
            id_list = ids.split(',')
            with transaction.atomic():
                for id in id_list:
                    c_f = customer_ftp_account.objects.get(id=id)
                    c_f.is_delete = 1
                    old_data['customer_code'] = c_f.customer_code
                    old_data['ftp_ip'] = c_f.ftp_ip
                    old_data['account'] = c_f.account
                    old_data['password'] = c_f.password
                    old_data['ftp_type'] = c_f.ftp_type
                    old_data['ftp_port'] = c_f.ftp_port
                    old_data['ftp_path'] = c_f.ftp_path
                    old_data['product'] = c_f.product
                    old_data['date'] = c_f.date
                    old_data['enable'] = c_f.enable
                    c_f.save()
                    c_l = maintain_change_log()
                    c_l.data_id = c_f.id
                    c_l.table = 'Customer FTP Account'
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