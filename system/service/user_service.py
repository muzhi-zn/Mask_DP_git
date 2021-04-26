# coding:utf-8
"""system/user/ process method

"""
from django.shortcuts import render

from utilslibrary.proxy.log_db_proxy import ProxyFactory, InvocationHandler
from django.http.response import HttpResponseRedirect, JsonResponse
from django.contrib.sessions.models import Session
from django.db.models import F, Q
from django.contrib.auth.hashers import make_password, check_password
import json
from django.conf import settings

from django.db import transaction
from system.models import log

from django.utils import timezone
from utilslibrary.models.userInfo_model import UserInfo

from utilslibrary.system_constant import Constant
from utilslibrary.base.base import BaseService
from system.models import user, user_role
from utilslibrary.utils.common_utils import get_ip
from utilslibrary.utils.date_utils import getDateStr, getMilliSecond
from system.service.ldap_auth import ldap_auth
from utilslibrary.utils.hashlib_util import get_sha256


@ProxyFactory(InvocationHandler)
class UserService(BaseService):

    def login(self, request, username, passwd):
        # 判断是否为域账户
        # if username[:5] == 'qxic\\':
        #     username = username[5:]
        #     print(username, passwd)

        # 如果帳號為administrator則例外
        if username == 'administrator':
            user_list = user.objects.filter(loginname=username, loginflag=1)
            passwd = get_sha256(passwd)
        else:
            user_list = user.objects.filter(loginname=username, loginflag=1, ldap=1)
        # else:
        #     user_list = user.objects.filter(loginname=username, loginflag=1)

        # 判斷回傳值數量是否等於1
        if len(user_list) == 1:
            user_o = user_list[0]
            # 判斷是否為ad帳戶
            if user_o.ldap:
                # 域用戶密碼驗證
                if user_o.ldap and user_o.ldap_group and user_o.loginflag and not user_o.is_delete:
                    ad_check_result = ldap_auth().user_auth(username, passwd)
                    if not ad_check_result[0]:
                        return render(request, 'system_login.html',
                                      {'login_error': ad_check_result[1]})
            else:
                # 非域用戶密碼驗證(僅限管理員)
                if not user_o.passwd or passwd != user_o.passwd:
                    return render(request, 'system_login.html',
                                  {'login_error': 'Password error ! Retry Please !'})

            # delete other session key of current user id
            u_s = UserService()
            UserService.deleteSessionKey(request, user_o.id)

            user_i = UserInfo()
            user_i.Id = user_o.id
            user_i.LoginName = user_o.loginname
            userinfo = UserInfo()
            userinfo.Id = user_o.id
            userinfo.LoginName = user_o.loginname
            user_json = json.dumps(userinfo, default=userinfo.conver_to_dict)
            # save data to session
            request.session[Constant.SESSION_CURRENT_USER] = user_json
            request.session[Constant.SESSION_CURRENT_USER_LOGINNAME] = user_o.loginname
            request.session[Constant.SESSION_CURRENT_USER_ID] = user_o.id
            # query role_menu
            permission_list = []
            permission_menu_id_list = []
            permission_dict_data_rule_id_list = []

            # check data_rule dict enable
            # query dict data rule id list
            _user_role_list = user_o.user_role_set.all()
            for _o_user_role in _user_role_list:
                _o_role = _o_user_role.role
                _role_menu_list = _o_role.role_menu_set.all()
                for _o_role_menu in _role_menu_list:
                    _o_menu = _o_role_menu.menu
                    permission_list.append(_o_menu.href)
                    permission_menu_id_list.append(_o_menu.id)
                if settings.DATA_RULE_DICT_ENABLE:
                    # query data rule id list
                    _role_data_rule_list = _o_role.role_data_rule_set.all()
                    for _role_data_role in _role_data_rule_list:
                        _data_rule = _role_data_role.data_rule
                        if _data_rule.class_name == 'dict':
                            permission_dict_data_rule_id_list.append(_data_rule.id)
            request.session[
                Constant.SESSION_CURRENT_USER_PERMISSION_DICT_DATARULE_ID_LIST] = permission_dict_data_rule_id_list
            request.session[Constant.SESSION_CURRENT_USER_PERMISSION_LIST] = permission_list

            # 存储当前用户有权访问的所有按钮ID
            request.session[Constant.SESSION_CURRENT_USER_PERMISSION_MENU_ID_LIST] = permission_menu_id_list

            # log login info
            log_o = log()
            log_o.ip = get_ip(request)
            log_o.obj = 'user'
            log_o.data_id = user_o.id
            log_o.user_id = user_o.id
            log_o.user_name = user_o.loginname
            log_o.action = 'login'
            log_o.create_date = getDateStr()
            log_o.create_time = getMilliSecond()
            log_o.save()
            return HttpResponseRedirect('/system/')
        return render(request, 'system_login.html', {'login_error': 'Login Name error ! Retry Please !'})

    def add_user(self, user):
        # return msg object
        data = {}
        try:
            user.save()
            data["success"] = True
            data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    def que_user(self, request, user):
        print('{} que data:{}')

    def upd_user(self, user):
        data = {}
        try:
            user.save()
            data["success"] = True
            data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    def upd_user_info(self, user):
        data = {}
        user.save()

        return HttpResponseRedirect('/system/user/info/')
        # del_

    # upd_

    # delete other session key of current user id
    def deleteSessionKey(self, request, user_id):
        # single user login
        # query session list from db when login,delete it when has current user old session,
        session_key = request.session.session_key
        for session in Session.objects.filter(~Q(session_key=session_key), expire_date__gte=timezone.now()):
            data = session.get_decoded()
            u_id = data.get(Constant.SESSION_CURRENT_USER_ID, None)
            if u_id == user_id:
                session.delete()

    # delete user by ids
    @transaction.atomic
    def del_user(self, obj):
        # return msg object
        data = {}
        data["success"] = False
        data["msg"] = "Failed"
        ids = obj.id
        if not ids:
            data["success"] = False
            data["msg"] = "Failed"
            return JsonResponse(data, safe=False)

        with transaction.atomic():
            id_list = ids.split(",")
            for id in id_list:
                if id:
                    _o = user.objects.get(id=id)
                    if _o:
                        # logic delete
                        _o.is_delete = 1
                        _o.save()

        data["success"] = True
        data["msg"] = "Success"
        return JsonResponse(data, safe=False)

    def modify_password(self, id, oldpass, newpass):
        data = {}
        data["success"] = False
        data["msg"] = "Error"

        _o = user.objects.get(id=id)
        if not _o.passwd or not check_password(oldpass, _o.passwd):
            data["success"] = False
            data["msg"] = "Old password error!"
            return JsonResponse(data, safe=False)

        newpass = make_password(newpass, None, 'pbkdf2_sha256')
        _o.passwd = newpass
        _o.save()
        data["success"] = True
        data["msg"] = "Success"
        return JsonResponse(data, safe=False)

    def customer_login(self, request, username, passwd):
        user_list = user.objects.filter(loginname=username, loginflag=1);
        if user_list and user_list.__len__() > 0:
            user_o = user_list[0]
            # check password

            if not user_o.passwd or passwd != user_o.passwd:
                return render(request, 'customer_login.html',
                              {'login_error': 'Login Name or Password error! Retry Please!'})
            user_i = UserInfo()
            user_i.Id = user_o.id
            user_i.LoginName = user_o.loginname
            userinfo = UserInfo()
            userinfo.id = user_o.id
            userinfo.LoginName = user_o.loginname
            user_json = json.dumps(userinfo, default=userinfo.conver_to_dict)
            # save data to session
            request.session[Constant.SESSION_CURRENT_USER] = user_json
            request.session[Constant.SESSION_CURRENT_USER_LOGINNAME] = user_o.loginname
            request.session[Constant.SESSION_CURRENT_USER_ID] = user_o.id
            # delete other session key of current user id
            u_s = UserService()
            UserService.deleteSessionKey(request, user_o.id)
            # query role_menu
            permission_list = []
            permission_menu_id_list = []
            permission_dict_data_rule_id_list = []

            # check data_rule dict enable
            # query dict data rule id list
            _user_role_list = user_o.user_role_set.all()
            for _o_user_role in _user_role_list:
                _o_role = _o_user_role.role
                _role_menu_list = _o_role.role_menu_set.all()
                for _o_role_menu in _role_menu_list:
                    _o_menu = _o_role_menu.menu
                    permission_list.append(_o_menu.href)
                    permission_menu_id_list.append(_o_menu.id)
                if settings.DATA_RULE_DICT_ENABLE:
                    # query data rule id list
                    _role_data_rule_list = _o_role.role_data_rule_set.all()
                    for _role_data_role in _role_data_rule_list:
                        _data_rule = _role_data_role.data_rule
                        if _data_rule.class_name == 'dict':
                            permission_dict_data_rule_id_list.append(_data_rule.id)
            request.session[
                Constant.SESSION_CURRENT_USER_PERMISSION_DICT_DATARULE_ID_LIST] = permission_dict_data_rule_id_list
            request.session[Constant.SESSION_CURRENT_USER_PERMISSION_LIST] = permission_list

            # 存储当前用户有权访问的所有按钮ID
            request.session[Constant.SESSION_CURRENT_USER_PERMISSION_MENU_ID_LIST] = permission_menu_id_list

            # log login info
            log_o = log()
            log_o.ip = get_ip(request)
            log_o.obj = 'user'
            log_o.data_id = user_o.id
            log_o.user_id = user_o.id
            log_o.user_name = user_o.loginname
            log_o.action = 'login'
            log_o.create_date = getDateStr()
            log_o.create_time = getMilliSecond()
            log_o.save()
            return HttpResponseRedirect('/')
        return render(request, 'customer_login.html', {'login_error': 'Login Name or Password error!Retry Please!'})
