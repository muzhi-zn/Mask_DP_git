from django.db.models import Q
from django.http.response import JsonResponse

from tooling_form.models import tapeout_info_temp, device_info_temp, ccd_table_temp, boolean_info_temp, \
    layout_info_temp, mlm_info_temp
from utilslibrary.base.base import BaseView


# tapeout_info temp
class ShowTipNo_tapeout_info_temp(BaseView):

    def post(self, request):
        super().post(request)

        tip_no = request.POST.get('tip_no')
        mask_name = request.POST.get('mask_name')

        q = Q()
        q.connector = 'and'
        q.children.append(('is_delete', 0))
        if tip_no:
            q.children.append(('tip_no', tip_no))
        if mask_name:
            q.children.append(('mask_name', mask_name))

        tapeout_info_data = tapeout_info_temp.objects.filter(q).order_by('id')[self.startIndex:self.endIndex].values()

        data = {"total": tapeout_info_temp.objects.filter(q).count(), "rows": list(tapeout_info_data)}

        return JsonResponse(data, safe=False)


# device_info temp
class ShowTipNo_device_info_temp(BaseView):

    def post(self, request):
        super().post(request)

        mask_name = request.POST.get('mask_name')

        res = boolean_info_temp.objects.filter(mask_name=mask_name)

        tip_no_list = []
        boolean_index_list = []
        source_db_list = []

        for loop in res:
            tip_no_list.append(loop.tip_no)
            boolean_index_list.append(loop.boolean_index)
            source_db_list.append(loop.source_db)

        q = Q()
        q.connector = 'and'
        q.children.append(('is_delete', 0))
        if tip_no_list:
            q.children.append(('tip_no__in', tip_no_list))
        if boolean_index_list:
            q.children.append(('boolean_index__in', boolean_index_list))
        if source_db_list:
            q.children.append(('source_db__in', source_db_list))

        device_info_data = device_info_temp.objects.filter(q).order_by('id')[self.startIndex:self.endIndex].values()

        data = {"total": device_info_temp.objects.filter(q).count(), "rows": list(device_info_data)}

        return JsonResponse(data, safe=False)


# ccd_table temp
class ShowTipNo_ccd_table_temp(BaseView):

    def post(self, request):

        super().post(request)

        tip_no = request.POST.get('tip_no')
        mask_name = request.POST.get('mask_name')

        q = Q()
        q.connector = 'and'
        q.children.append(('is_delete', 0))
        if tip_no:
            q.children.append(('tip_no', tip_no))
        if mask_name:
            q.children.append(('mask_name', mask_name))

        ccd_table_data = ccd_table_temp.objects.filter(q).order_by('id')[self.startIndex:self.endIndex].values()

        data = {"total": ccd_table_temp.objects.filter(q).count(), "rows": list(ccd_table_data)}

        return JsonResponse(data, safe=False)


# boolean_info temp
class ShowTipNo_boolean_info_temp(BaseView):

    def post(self, request):
        super().post(request)

        tip_no = request.POST.get('tip_no')
        mask_name = request.POST.get('mask_name')

        q = Q()
        q.connector = 'and'
        q.children.append(('is_delete', 0))
        if tip_no:
            q.children.append(('tip_no', tip_no))
        if mask_name:
            q.children.append(('mask_name', mask_name))

        boolean_info_data = boolean_info_temp.objects.filter(q).order_by('id')[self.startIndex:self.endIndex].values()

        data = {"total": boolean_info_temp.objects.filter(q).order_by('id').count(), "rows": list(boolean_info_data)}

        return JsonResponse(data, safe=False)


# layout_info temp
class ShowTipNo_layout_info_temp(BaseView):

    def post(self, request):

        super().post(request)

        tip_no = request.POST.get('tip_no')
        mask_name = request.POST.get('mask_name')

        q = Q()
        q.connector = 'and'
        q.children.append(('is_delete', 0))
        if tip_no:
            q.children.append(('tip_no', tip_no))
        if mask_name:
            q.children.append(('mask_name', mask_name))

        layout_info_data = layout_info_temp.objects.filter(q).order_by('id')[self.startIndex:self.endIndex].values()

        data = {"total": layout_info_temp.objects.filter(q).count(), "rows": list(layout_info_data)}

        return JsonResponse(data, safe=False)


# mlr_info temp
class ShowTipNo_mlm_info_temp(BaseView):

    def post(self, request):
        super().post(request)

        tip_no = request.POST.get('tip_no')
        mask_name = request.POST.get('mask_name')

        q = Q()
        q.connector = 'and'
        q.children.append(('is_delete', 0))
        if tip_no:
            q.children.append(('tip_no', tip_no))
        if mask_name:
            q.children.append(('mask_name', mask_name))

        mlm_info_data = mlm_info_temp.objects.filter(q).order_by('id')[self.startIndex:self.endIndex].values()

        data = {"total": mlm_info_temp.objects.filter(q).count(), "rows": list(mlm_info_data)}

        return JsonResponse(data, safe=False)
