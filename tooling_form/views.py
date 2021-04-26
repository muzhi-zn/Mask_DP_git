# -*- coding: utf-8 -*-
"""tooling form manage

"""
import logging

from django.views.decorators.http import require_POST
from django.shortcuts import render
import os
from django.http.response import JsonResponse, FileResponse

from Mask_DP.settings import PROJECT_NAME
from system.websocket_view import send_notice
from utilslibrary.decorators.auth_decorators import AuthCheck
from tooling_form.service.ftp_service import FtpService
from django.views.decorators.csrf import csrf_exempt
from utilslibrary.decorators.catch_exception_decorators import catch_exception
from utilslibrary.system_constant import Constant
from tooling_form.models import import_list
from django.db.models.query_utils import Q

# Create your views here.


# tooling form sop download
from utilslibrary.utils import ini_mds_utils
from utilslibrary.utils.common_utils import getCurrentSessionID

log = logging.getLogger('log')


@AuthCheck
def tooling_form_sop_download(request):
    # send_mail()
    return render(request, 'tooling_form/tooling_form_sop_download.html')


@catch_exception
def tooling_form_sop_download_file(request):
    cur_path = os.path.abspath(os.path.dirname(__file__)).split(PROJECT_NAME)[0]  # 获得项目同级目录
    temp_path = os.path.join(os.path.dirname(cur_path), Constant.TOOLING_FORM_DOWNLOAD_DIR)

    file = open(temp_path + Constant.TOOLING_FORM_SOP_TEMPLATE, 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="Mask_DP_SOP.pdf"'
    return response


# tooling_form_download
def tooling_form_download(request):
    return render(request, 'tooling_form/tooling_form_download.html')


@catch_exception
def tooling_form_download_file(request):
    cur_path = os.path.abspath(os.path.dirname(__file__)).split(PROJECT_NAME)[0]  # 获得项目同级目录
    temp_path = os.path.join(os.path.dirname(cur_path), Constant.TOOLING_FORM_DOWNLOAD_DIR)

    file = open(temp_path + Constant.TOOLING_FORM_TEMPLATE, 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="Mask_DP_Tooling_Form_Template.xlsx"'
    return response


# tooling_form_import_list,ftp service
def tooling_form_upload(request):
    # send_notice(getCurrentSessionID(request), '你打开了tooling form upload 页面', Constant.NOTICE_TYPE_SUCCESS)
    tip_no = request.GET.get("tip_no")

    return render(request, 'tooling_form/upload_tooling_form.html', {"tip_no": tip_no})


# tooling form uploading
@catch_exception
def tooling_form_uploading(request):
    if request.method == 'POST':
        obj = request.FILES.get('file')

        cur_path = os.path.abspath(os.path.dirname(__file__)).split(PROJECT_NAME)[0]  # 获得项目同级目录
        tooling_upload_path = os.path.join(os.path.dirname(cur_path), PROJECT_NAME + '_upload')
        if not os.path.exists(tooling_upload_path):
            os.mkdir(tooling_upload_path)  # 如果不存在这个logs文件夹，就自动创建一个

        # file_path=os.path.join('D:\\', 'upload', obj.name)
        file_path = os.path.join(tooling_upload_path, obj.name)
        print("file_path:" + file_path)

        f = open(file_path, 'wb')
        for chunk in obj.chunks():
            f.write(chunk)
        f.close()
        return JsonResponse({'filename': 'ok'}, safe=False)


# tooling ftp service view
def tooling_ftp_service(request):
    tip_no = request.GET.get('tip_no')
    return render(request, 'ftp_service.html', {'tip_no': tip_no})


@csrf_exempt
@catch_exception
def tooling_tip_no_options(request):
    if request.method == 'POST':
        user_id = request.session.get(Constant.SESSION_CURRENT_USER_ID)
        tip_no_list = import_list.objects.values('tip_no').filter(~Q(tip_no=''), create_by=user_id, is_delete=0,
                                                                  status__gte=2).distinct()
        return JsonResponse(list(tip_no_list), safe=False)


@csrf_exempt
def get_files_list(request):
    #     messages.success(request, "测试消息" + request.POST.get('tip_no'))
    return JsonResponse(FtpService().get_files_list(request), safe=False)


@csrf_exempt
def check_files_list(request):
    return JsonResponse(FtpService().check_files_list(request), safe=False)


@csrf_exempt
def file_upload_check(request):
    """判断是否允许该文件上传"""
    return FtpService().file_upload_check(request)


@csrf_exempt
def file_upload(request):
    """文件分片上传"""
    return FtpService().file_upload(request)


@csrf_exempt
def file_check(request):
    """文件分片上传"""
    return JsonResponse(FtpService().file_check(request))


@csrf_exempt
def file_merge(request):
    """文件上传完成合并"""
    return FtpService().file_merge(request)


@csrf_exempt
@require_POST
@catch_exception
def done(request):
    """ftp完成,生成lot信息"""
    return FtpService().done(request)


@csrf_exempt
@require_POST
@catch_exception
def create_lot_id(request):
    """测试生成lot_id"""
    # get_wip_for_tsak()
    return FtpService().create_lot_id(request)


@catch_exception
@csrf_exempt
def test_layout(request):
    tip_no = request.POST.get('tip_no')
    if not ini_mds_utils.mds(tip_no):
        return JsonResponse({"success": False, "msg": "MDS fail"}, safe=False)
    elif not ini_mds_utils.ini(tip_no):
        return JsonResponse({"success": False, "msg": "INI fail"}, safe=False)
    else:
        return JsonResponse({"success": True, "msg": "success"}, safe=False)
