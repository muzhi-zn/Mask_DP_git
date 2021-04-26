# coding=utf-8
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from tooling_form.models import file_analysis_info
from tooling_form.service import check_files_service
from utilslibrary.base.base import BaseView
from django.http.response import JsonResponse

class fileAnalysisInfoList(BaseView):
    
    def get(self,request):
        '''跳转页面'''
        return render(request, 'file_analysis_info_list.html')
    
    def post(self,request):
        '''获取文件分析信息列表'''
        super().post(request)
        tip_no = request.POST.get('tip_no')
        if tip_no:
            fai_list = file_analysis_info.objects.values().filter(tip_no=tip_no)
            data = {}
            data['total'] = fai_list.count()
            data['rows'] = list(fai_list)
            return JsonResponse(data,safe=False)
        else:
            fai_list = file_analysis_info.objects.values().all()
            data = {}
            data['total'] = fai_list.count()
            data['rows'] = list(fai_list)
            return JsonResponse(data,safe=False)


@csrf_exempt
def calibrewb_callback(request):
    """calibrewb命令的回调方法"""
    return check_files_service.calibrewb_callback(request)
