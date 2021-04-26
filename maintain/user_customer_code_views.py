from django.shortcuts import render
from django.http import JsonResponse
from system.models import user
from utilslibrary.base.base import BaseView
from django.db.models.query_utils import Q


class user_customer_code_list(BaseView):

    def post(self, request):
        if request.method == 'POST':
            super().post(request)
            id = request.POST.get('id')

            data = {}

            q = Q()
            q.connector = 'and'
            q.children.append(('is_delete', 0))
            q.children.append(('customer_code_id', id))

            user_list = user.objects.filter(q).order_by('id').values()

            data['total'] = user.objects.filter(q).count()
            data['rows'] = list(user_list)

            return JsonResponse(data, safe=False)
