from django.shortcuts import render
import json
import hashlib

from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from utilslibrary.system_constant import Constant
from system.models import user
from system.service.sync_service import LDAP_SYNC_SERVICE_TEST


# Create your views here.

@csrf_exempt
@require_POST
def auth_account(request):
    """帳號密碼驗證接口"""
    r_dict = {}
    params = request.body.decode('utf-8')
    param_json = json.loads(params)
    account = param_json.get('account')  # 帳號
    password = param_json.get('password')  # 密碼

    # 1.创建一个hash对象
    h = hashlib.sha256()
    # 2.填充要加密的数据
    password_str = password
    h.update(bytes(password_str, encoding='utf-8'))
    # 3.获取加密结果
    password_result = h.hexdigest()

    try:
        _o = user.objects.get(loginname=account, ldap=0, loginflag=1, is_delete=0)
        data = _o.passwd
    except Exception as e:
        print(e)
        r_dict['code'] = 200
        r_dict['message'] = "Error"
        return JsonResponse(json.dumps(r_dict), safe=False)

    if password_result == data:
        r_dict['code'] = 100
        r_dict['message'] = "OK"
    else:
        r_dict['code'] = 200
        r_dict['message'] = "Error"

    return JsonResponse(json.dumps(r_dict), safe=False)


@csrf_exempt
@require_POST
def ad_conn_test(request):
    """AD連線驗證接口"""
    r_dict = {}

    ldap_server_pool = request.POST.get('ldap_server_pool')
    ldap_server_port = request.POST.get('ldap_server_port')
    admin_dn = request.POST.get('admin_dn')
    admin_pwd = request.POST.get('admin_pwd')
    search_base = request.POST.get('search_base')
    group = request.POST.get('group')

    print(ldap_server_pool, ldap_server_port, admin_dn, admin_pwd, search_base, group)

    # res = LDAP_SYNC_SERVICE_TEST(ldap_server_pool,
    #                              ldap_server_port,
    #                              admin_dn,
    #                              admin_pwd,
    #                              search_base,
    #                              group).ldap_sync()
    #
    # if res:
    #     r_dict['code'] = 100
    #     r_dict['message'] = "success"
    # else:
    #     r_dict['code'] = 200
    #     r_dict['message'] = "error"

    return JsonResponse(json.dumps(r_dict), safe=False)
