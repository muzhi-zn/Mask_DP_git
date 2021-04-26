from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from maintain.models import customer_code
from maintain.service.customer_code_service import CustomerCodeService
from utilslibrary.base.base import BaseView
from system.models import user


class CustomerCodeView(BaseView):
    def get(self, request):
        return render(request, 'customer_code/customer_code_list.html')

    def post(self, request):
        super().post(request)
        code = request.POST.get('code')
        customer = request.POST.get('customer')
        query_set = customer_code.objects.filter(is_delete='0')
        if code:
            query_set = query_set.filter(code=code)
        if customer:
            query_set = query_set.filter(customer=customer)
        query_list = list(query_set.values())[self.startIndex: self.endIndex]
        data = {'total': query_set.count(), 'rows': query_list}
        return JsonResponse(data, safe=False)


class CustomerCodeAdd(BaseView):
    def get(self, request):
        return render(request, 'customer_code/customer_code_form.html', {'method': 'add', 'c_c': ''})

    def post(self, request):
        c_c = customer_code()
        code = request.POST.get('code')
        customer = request.POST.get('customer')
        c_c.code = code
        c_c.customer = customer
        return CustomerCodeService().add_customer_code(c_c)


class CustomerCodeEdit(BaseView):
    def get(self, request):
        id = request.GET.get('id')
        c_c = customer_code.objects.get(id=id)
        return render(request, 'customer_code/customer_code_form.html', {'method': 'edit', 'c_c': c_c})

    def post(self, request):
        id = request.POST.get('id')
        c_c = customer_code.objects.get(id=id)
        code = request.POST.get('code')
        customer = request.POST.get('customer')
        c_c.code = code
        c_c.customer = customer
        return CustomerCodeService().add_customer_code(c_c)


class CustomerCodeDel(BaseView):
    def get(self, request):
        ids = request.GET.get('ids')
        c_c = customer_code()
        c_c.id = ids
        for id in ids:
            user_count = user.objects.filter(customer_code_id=id, is_delete=0).count()
            if not user_count == 0:
                data = {'success': False, 'msg': 'This code is in use'}
                return JsonResponse(data=data, safe=False)

        return CustomerCodeService().del_process_tooling(c_c)


@csrf_exempt
def check_code(request):
    code = request.POST.get('code')
    length = len(code)
    if length != 2:
        return JsonResponse({'success': True})
    else:
        if code[0].isupper() and code[-1].isdigit():
            query_set = customer_code.objects.filter(code=code, is_delete='0')
            if query_set:
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False})
        else:
            return JsonResponse({'success': True})
