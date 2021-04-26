from django.db import transaction
from maintain.models import customer_code
from utilslibrary.base.base import BaseService
from django.http import JsonResponse


class CustomerCodeService(BaseService):

    def add_customer_code(self, c_c):
        data = {}
        try:
            c_c.save()
            data['success'] = True
            data['message'] = 'success'
            return JsonResponse(data=data, safe=False)
        except Exception as e:
            data['success'] = False
            data['message'] = str(e)
            return JsonResponse(data=data, safe=False)

    def del_process_tooling(self, c_c):
        data = {}
        try:
            ids = c_c.id
            id_list = ids.split(',')
            with transaction.atomic():
                for id in id_list:
                    p_t = customer_code.objects.get(id=id)
                    p_t.is_delete = 1
                    p_t.save()
            data['success'] = True
            data['msg'] = 'Delete Success'
            return JsonResponse(data, safe=False)
        except Exception as e:
            data['success'] = False
            data['msg'] = 'Delete Failed'
            print(e)
            return JsonResponse(data, safe=True)
