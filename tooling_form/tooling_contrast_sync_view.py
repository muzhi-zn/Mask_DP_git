from django.shortcuts import render

from tooling_form.service import tooling_contrast_sync_service
from utilslibrary.base.base import BaseView

from utilslibrary.utils.common_utils import getCurrentSessionID

'''
    同步数据 
    获取传入的import_id,调用service中同步的方法
'''
class toolingSheetContrast(BaseView):

    def get(self,request):

        tip_no = request.GET.get("tip_no", '')
        mask_name = request.GET.get("mask_name", '')

        u_id = getCurrentSessionID(request)

        if not u_id:
            return render(request, 'system_login.html')

        _o = tooling_contrast_sync_service

        return _o.toolingSheetContrast(tip_no, mask_name, u_id)
