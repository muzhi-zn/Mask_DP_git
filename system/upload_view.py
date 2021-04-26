from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from system.service.upload_service import upload_service


@csrf_exempt
def file_upload_check(request):
    """判断是否允许该文件上传"""
    return upload_service().file_upload_check(request)


@csrf_exempt
def file_upload(request):
    """文件分片上传"""
    return upload_service().file_upload(request)


@csrf_exempt
def file_check(request):
    """文件分片上传"""
    return JsonResponse(upload_service().file_check(request))


@csrf_exempt
def file_merge(request):
    """文件上传完成合并"""
    return upload_service().file_merge(request)
