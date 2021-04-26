from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from maintain.models import customer_ftp_account,customer_code
from maintain.service.customer_ftp_service import CustomerFTPs
from utilslibrary.base.base import BaseView


class CustomerFTPView(BaseView):
    def get(self, request):
        return render(request, 'maintain/customer_ftp_list.html')

    def post(self, request):
        super().post(request)
        customer_code = request.POST.get('customer_code')
        ftp_ip = request.POST.get('ftp_ip')
        account = request.POST.get('account')
        password = request.POST.get('password')
        ftp_type = request.POST.get('ftp_type')
        ftp_port = request.POST.get('ftp_port')
        ftp_path = request.POST.get('ftp_path')
        product = request.POST.get('product')
        date = request.POST.get('date')
        enable = request.POST.get('enable')
        query_set = customer_ftp_account.objects.filter(is_delete=0)
        if customer_code:
            query_set = query_set.filter(customer_code=customer_code)
        if ftp_ip:
            query_set = query_set.filter(ftp_ip=ftp_ip)
        if account:
            query_set = query_set.filter(account=account)
        if password:
            query_set = query_set.filter(password=password)
        if ftp_type:
            query_set = query_set.filter(ftp_type=ftp_type)
        if ftp_port:
            query_set = query_set.filter(ftp_port=ftp_port)
        if ftp_path:
            query_set = query_set.filter(ftp_path=ftp_path)
        if product:
            query_set = query_set.filter(product=product)
        if date:
            query_set = query_set.filter(date=date)
        if enable:
            query_set = query_set.filter(enable=enable)
        query_list = query_set.values()[self.startIndex: self.endIndex]
        data = {'total': query_set.count(), 'rows': list(query_list)}
        return JsonResponse(data, safe=False)


class CustomerFTPAdd(BaseView):
    def get(self, request):
        return render(request, 'maintain/customer_ftp_form.html', {"method": 'add', 'cust_ftp': ''})

    def post(self, request):
        customer_code = request.POST.get('customer_code')
        ftp_ip = request.POST.get('ftp_ip')
        account = request.POST.get('account')
        password = request.POST.get('password')
        ftp_type = request.POST.get('ftp_type')
        ftp_port = request.POST.get('ftp_port')
        ftp_path = request.POST.get('ftp_path')
        product = request.POST.get('product')
        date = request.POST.get('date')
        enable = request.POST.get('enable')
        set_list = []
        query_set = ''
        query_set = customer_ftp_account.objects.filter(customer_code=customer_code, ftp_ip=ftp_ip, account=account, password=password, ftp_type=ftp_type, ftp_port=ftp_port, ftp_path=ftp_path,product=product,date=date,enable=enable, is_delete=0)
        if query_set or set_list:
            return JsonResponse({'success': False, 'message': 'Do not allow duplicates'})
        else:
            new_data = {}
            c_f = customer_ftp_account()
            c_f.customer_code = customer_code
            c_f.ftp_ip = ftp_ip
            c_f.account = account
            c_f.password = password
            c_f.ftp_type = ftp_type
            c_f.ftp_port = ftp_port
            c_f.ftp_path = ftp_path
            c_f.product = product
            c_f.date = date
            c_f.enable = enable
            new_data['customer_code'] = customer_code
            new_data['ftp_ip'] = ftp_ip
            new_data['account'] = account
            new_data['password'] = password
            new_data['ftp_type'] = ftp_type
            new_data['ftp_port'] = ftp_port
            new_data['ftp_path'] = ftp_path
            new_data['product'] = product
            new_data['date'] = date
            new_data['enable'] = enable
            return CustomerFTPs().add_customer_ftp(c_f, new_data, '', request)


class CustomerFTPEdit(BaseView):
    def get(self, request):
        id = request.GET.get('id')
        cust_ftp = customer_ftp_account.objects.get(id=id)
        return render(request, 'maintain/customer_ftp_form.html', {'cust_ftp': cust_ftp, 'method': 'edit'})

    def post(self, request):
        id = request.POST.get('id')
        customer_code = request.POST.get('customer_code')
        ftp_ip = request.POST.get('ftp_ip')
        account = request.POST.get('account')
        password = request.POST.get('password')
        ftp_type = request.POST.get('ftp_type')
        ftp_port = request.POST.get('ftp_port')
        ftp_path = request.POST.get('ftp_path')
        product = request.POST.get('product')
        date = request.POST.get('date')
        enable = request.POST.get('enable')
        query_set = customer_ftp_account.objects.exclude(id=id)
        query_set = query_set.filter(customer_code=customer_code, ftp_ip=ftp_ip, account=account, password=password, ftp_type=ftp_type, ftp_port=ftp_port, ftp_path=ftp_path,product=product,enable=enable,date=date, is_delete=0)
        if query_set:
            return JsonResponse({'success': False, 'message': 'Do not allow duplicates'})
        else:
            new_data = {}
            old_data = {}
            c_f = customer_ftp_account.objects.get(id=id)
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
            c_f.customer_code = customer_code
            c_f.ftp_ip = ftp_ip
            c_f.account = account
            c_f.password = password
            c_f.ftp_type = ftp_type
            c_f.ftp_port = ftp_port
            c_f.ftp_path = ftp_path
            c_f.product = product
            c_f.date = date
            c_f.enable = enable
            new_data['customer_code'] = customer_code
            new_data['ftp_ip'] = ftp_ip
            new_data['account'] = account
            new_data['password'] = password
            new_data['ftp_type'] = ftp_type
            new_data['ftp_port'] = ftp_port
            new_data['ftp_path'] = ftp_path
            new_data['product'] = product
            new_data['date'] = date
            new_data['enable'] = enable
            return CustomerFTPs().upt_customer_ftp(c_f, new_data, old_data, request)


class CustomerFTPDel(BaseView):
    def get(self, request):
        ids = request.GET.get('ids')
        c_f = CustomerFTPs()
        c_f.id = ids
        return CustomerFTPs().del_customer_ftp(c_f, request)


@csrf_exempt
def get_customer_code(request):
    cust_code = customer_code.objects.filter(is_delete='0')
    code_list = list()
    for code_ in cust_code:
        if code_.code not in code_list:
            code_list.append(code_.code)
    return JsonResponse({'success': True, 'data': code_list}, safe=False)
