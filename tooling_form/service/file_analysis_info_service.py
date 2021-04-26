# -*- coding: utf-8 -*-
from utilslibrary.base.base import BaseService 
from django.template.context_processors import request
from tooling_form.models import file_analysis_info
import json
from django.http.response import JsonResponse
from pandas._libs.lib import fast_multiget

class FileAnalysisInfoService(BaseService):
    
    def list_file_analysis_info(self,request):
        '''获取文件上传分析信息列表'''
        if request.method == 'POST':
            tip_no = request.POST.get('tip_no')
            fai_list = file_analysis_info.objects.filter(tip_no=tip_no)
            return json.dumps(list(fai_list))
    
    def get_file_analysis_info(self,request):
        '''根据id获取文件上传分析信息'''
        if request.method == 'POST':
            id = request.POST.get('id')
            fai = file_analysis_info.objects.get(id=id)
            return json.dumps(dict(fai))
        
    def del_file_analysis_info(self,request):
        '''删除文件上传分析信息'''
        if request.method == 'POST':
            id = request.POST.get('id')
            file_analysis_info.objects.filter(id=id).delete()
            return JsonResponse({'success':'true'},safe=False)
