from django.http import JsonResponse
from django.shortcuts import render

from maintain.models import pellicle_mapping
from maintain.service.pellicle_service import PellicleService
from utilslibrary.base.base import BaseView


class PellicleList(BaseView):
    def get(self, request):
        return render(request, 'maintain/pellicle_list.html')

    def post(self, request):
        super().post(request)
        query_set = pellicle_mapping.objects.filter(is_delete=0)
        query_list = list(query_set.values())[self.startIndex: self.endIndex]
        data = {'total': query_set.count(), 'rows': query_list}
        return JsonResponse(data, safe=False)


class PellicleView(BaseView):
    def get(self, request):
        id = request.GET.get('id')
        pellicle = pellicle_mapping.objects.get(id=id)
        return render(request, 'maintain/pellicle_form.html', {'pellicle': pellicle, 'method': 'view'})


class PellicleAdd(BaseView):
    def get(self, request):
        return render(request, 'maintain/pellicle_form.html', {'pellicle': '', 'method': 'add'})
    def post(self, request):
        mt_form_pellicle = request.POST.get('mt_form_pellicle')
        mes_pellicle_code = request.POST.get('mes_pellicle')
        p_m = pellicle_mapping()
        p_m.mt_form_pellicle = mt_form_pellicle
        p_m.mes_pellicle_code = mes_pellicle_code
        return PellicleService().add_pellicle(p_m)

class PellicleEdit(BaseView):
    def get(self, request):
        id = request.GET.get('id')
        pellicle = pellicle_mapping.objects.get(id=id)
        return render(request, 'maintain/pellicle_form.html', {'pellicle': pellicle, 'method': 'edit'})
    def post(self, request):
        id = request.POST.get('id')
        mt_form_pellicle = request.POST.get('mt_form_pellicle')
        mes_pellicle_code = request.POST.get('mes_pellicle')
        p_m = pellicle_mapping.objects.get(id=id)
        p_m.mt_form_pellicle = mt_form_pellicle
        p_m.mes_pellicle_code = mes_pellicle_code
        return PellicleService().edit_pellicle(p_m)

class PellicleDel(BaseView):
    def get(self, request):
        ids = request.GET.get('ids')
        p_m = pellicle_mapping()
        p_m.id = ids
        return PellicleService().del_pellicle(p_m)


