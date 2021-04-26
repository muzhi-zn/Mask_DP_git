# --coding:utf-8 --

"""user and auth manage"""
import json
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from django.http import HttpResponse
from django.db.models import Q

from maintain.models import customer_code
from system.models import user, user_role, role
from system.service.role_service import RoleService
from system.service.user_service import UserService
from utilslibrary.system_constant import Constant
from utilslibrary.base.base import BaseView
from utilslibrary.utils.common_utils import getCurrentSessionID
from utilslibrary.utils.hashlib_util import get_sha256


# Create your views here.
class Login(BaseView):
    def get(self, request):
        return render(request, 'system_login.html')

    def post(self, request):
        username = request.POST['username']
        passwd = request.POST['password']
        _s = UserService()
        return _s.login(request, username, passwd)


class Logout(BaseView):
    def get(self, request):
        # if request.session.get(Constant.SESSION_CURRENT_USER):
        #     del request.session[Constant.SESSION_CURRENT_USER]
        # if request.session.get(Constant.SESSION_CURRENT_USER_LOGINNAME):
        #     del request.session[Constant.SESSION_CURRENT_USER_LOGINNAME]
        request.session.flush()
        return render(request, 'system_login.html')


class UserList(BaseView):

    def get(self, request):
        return render(request, 'system_user_list.html')

    def post(self, request):
        # -----------------------------
        # 需要获得翻页参数时添加
        # 代码中使用self.startIndex和self.endIndex获取相应范围的记录
        # ------------------------------
        super().post(request)
        # 执行查询
        # 接收查询参数---与页面上要查询的条件匹配
        loginname = request.POST.get('loginname', '')
        realname = request.POST.get('realname', '')
        isadmin = request.POST.get('isadmin', '')
        role_types = role.objects.all()
        user_roles = user_role.objects.all()
        """query by where1"""
        # 添加查询条件，设置为逻辑与查询
        if isadmin != '':
            # 获取对应isadmin下的用户列表
            users_id = list(user_role.objects.filter(role_id=isadmin).values('user_id'))
            id_list = []
            for user_id in users_id:
                id_list.append(user_id['user_id'])
            users = user.objects.filter(id__in=id_list)
        else:
            users = user.objects.filter()
        q = Q()
        q.connector = 'and '
        q.children.append(('is_delete', 0))
        # 通过loginname查询
        if loginname:
            q.children.append(('loginname__contains', loginname))
        # 通过realname查询
        if realname:
            q.children.append(('realname__contains', realname))

        print('startIndex{} endIndex{}'.format(self.startIndex, self.endIndex))
        # 执行查询
        u_list = users.filter(q).order_by('-id')[self.startIndex:self.endIndex].values()

        # 组装JSON数据
        data = {}
        # 设置总记录数
        data["total"] = users.filter(q).count()
        data["rows"] = list(u_list)
        print(data)

        return JsonResponse(data, safe=False)


class UserAdd(BaseView):

    def get(self, request):
        _o = user()
        return render(request, 'system_user_form.html', {"method": "add", "user_o": _o})

    def post(self, request):
        data = {}

        id = request.POST.get('id')
        loginname = request.POST.get('loginName', '')
        realname = request.POST.get('realName', '')
        passwd = request.POST.get('newPassword', '')
        passwd = get_sha256(passwd)
        # passwd = make_password(passwd, None, 'pbkdf2_sha256')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        mobile = request.POST.get('mobile', '')
        loginflag = request.POST.get('loginFlag', '')
        parent_id = request.POST.get('parent_id', '')
        parent_name = request.POST.get('parent_name', '')
        customer_code_id = request.POST.get('customer_code', '')
        c_code = customer_code.objects.get(id=customer_code_id).code
        remarks = request.POST.get('remarks')
        addr = request.POST.get('addr')

        if loginname == '' or realname == '' or passwd == '':
            data["success"] = False
            data["msg"] = "Input Data Error!"
            return JsonResponse(data, safe=False)

        # select customer code

        # check the record has exist
        _o = user.objects.filter(loginname=loginname, is_delete=0)
        if _o:
            data["success"] = False
            data["msg"] = "login name exists!"
            return JsonResponse(data, safe=False)
        _o = user()
        _o.loginname = loginname
        _o.realname = realname
        _o.passwd = passwd
        _o.email = email
        _o.phone = phone
        _o.mobile = mobile
        _o.loginflag = loginflag
        _o.office_id = parent_id
        _o.office_name = parent_name
        _o.customer_code_id = customer_code_id
        _o.customer_code = c_code
        _o.remarks = remarks
        _o.addr = addr
        _s = UserService()

        return _s.add_user(_o)


class UserView(BaseView):

    def get(self, request):
        id = request.GET.get("id")
        print(id)
        if not id:
            return render(request, 'system_user_form.html', {"method": "edit"})
        else:
            _o = user.objects.get(id=id)
            return render(request, 'system_user_form.html', {"user_o": _o, "method": "edit"})


class UserEdit(BaseView):

    def get(self, request):
        id = request.GET.get("id")
        if not id:
            return render(request, 'system_user_form.html', {"method": "edit"})
        else:
            _o = user.objects.get(id=id)
            return render(request, 'system_user_form.html', {"user_o": _o, "method": "edit"})

    def post(self, request):
        data = {}

        id = request.POST.get('id')
        loginname = request.POST.get('loginName', '')
        realname = request.POST.get('realName', '')
        passwd = request.POST.get('newPassword', '')
        passwd = get_sha256(passwd)
        # passwd = make_password(passwd, None, 'pbkdf2_sha256')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        mobile = request.POST.get('mobile', '')
        loginflag = request.POST.get('loginFlag', '')
        parent_id = request.POST.get('parent_id', '')
        parent_name = request.POST.get('parent_name', '')
        customer_code_id = request.POST.get('customer_code', '')
        c_code = customer_code.objects.get(id=customer_code_id).code
        remarks = request.POST.get('remarks')
        addr = request.POST.get('addr')

        if loginname == '' or realname == '' or passwd == '':
            data["success"] = False
            data["msg"] = "Input Data Error!"
            return JsonResponse(data, safe=False)

        if id:
            # update daota
            _o = user.objects.get(id=id)
            _o.loginname = loginname
            _o.realname = realname
            _o.passwd = passwd
            _o.email = email
            _o.phone = phone
            _o.mobile = mobile
            _o.loginflag = loginflag
            _o.office_id = parent_id
            _o.office_name = parent_name
            _o.customer_code_id = customer_code_id
            _o.customer_code = c_code
            _o.remarks = remarks
            _o.addr = addr

            _s = UserService()
            return _s.upd_user(_o)
        else:
            data["success"] = False
            data["msg"] = "ID Error!"
            return JsonResponse(data, safe=False)


# user delete
class UserDel(BaseView):

    def get(self, request):
        data = {}
        ids = request.GET.get("ids")
        data["success"] = True
        data["msg"] = "Success"
        _o = user()
        _o.id = ids
        _s = UserService()

        return _s.del_user(_o)


@csrf_exempt
def get_customer_code(request):
    cc_list = customer_code.objects.filter(is_delete=0).values('id', 'code')
    result_dict = {}
    i = 0
    for label in cc_list:
        print(label)
        result_dict[i] = label
        i += 1

    return JsonResponse(data=result_dict, safe=False)


# check login name
class UserCheckLoginName(BaseView):

    def get(self, request):
        ln = request.GET.get('loginName')
        oln = request.GET.get('oldLoginName')
        if ln == oln:
            return HttpResponse('true')
        _o_list = user.objects.filter(loginname=ln, is_delete=0)
        if _o_list:
            return HttpResponse('false')
        else:
            return HttpResponse('true')


class UserSelect(BaseView):

    def get(self, request):
        return render(request, 'system_user_select.html')

    def post(self, request):
        id = request.POST.get('id')
        ids = request.POST.get('ids')
        data = {}
        data["success"] = True
        data["msg"] = "Success"
        _s = RoleService()
        _s.assgin_user_role(id, ids)

        return JsonResponse(data, safe=False)


class UserInfoView(BaseView):

    def get(self, request):
        user_id = getCurrentSessionID(request)
        _o = user.objects.get(id=user_id)
        _user_role_list = _o.user_role_set.all()
        role_names = ''
        for _user_role in _user_role_list:
            role_names = role_names + ',' + _user_role.role.name
        return render(request, "system_user_info.html", {"user_o": _o, "role_names": role_names})


class UserInfoForm(BaseView):

    def get(self, request):
        user_id = getCurrentSessionID(request)
        _o = user.objects.get(id=user_id)

        return render(request, "system_user_info_form.html", {"user_o": _o})

    def post(self, request):
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        mobile = request.POST.get("mobile")
        remarks = request.POST.get("remarks")
        user_id = getCurrentSessionID(request)
        _o = user.objects.get(id=user_id)
        _o.realname = name
        _o.email = email
        _o.phone = phone
        _o.mobile = mobile
        _o.remarks = remarks
        _s = UserService()
        return _s.upd_user_info(_o)


class UserModifyPassword(BaseView):

    def get(self, request):
        return render(request, "system_user_up_passwd.html")

    def post(self, request):
        oldPassword = request.POST.get("oldPassword")
        newPassword = request.POST.get("newPassword")
        user_id = getCurrentSessionID(request)
        _s = UserService()
        return _s.modify_password(user_id, oldPassword, newPassword)


class Ztree(BaseView):

    def get(self, request):
        q = Q()
        q.connector = 'and '
        q.children.append(('is_delete', 0))
        # 执行查询
        role_list = role.objects.filter(q).order_by('-id').values()
        children_list = []
        data_list = []
        data = {"level": 1, "children": '0', "name": "UserType", "id": "1", "text": "UserType"}
        id = 0
        for role_each in role_list:
            children_dict = {}
            children_dict["name"] = role_each['name']
            children_dict["text"] = role_each['name']
            children_dict["id"] = role_each['id']
            children_list.append(children_dict)
        data["children"] = children_list
        data_list.append(data)
        final_data = json.dumps(data_list)
        print(final_data)
        return HttpResponse(final_data)


class CustomerLogin(BaseView):
    def get(self, request):
        return render(request, 'customer_login.html')

    def post(self, request):
        username = request.POST['username']
        passwd = request.POST['password']
        passwd = get_sha256(passwd)
        _s = UserService()
        return _s.customer_login(request, username, passwd)


class CustomerLogout(BaseView):
    def get(self, request):
        if request.session.get(Constant.SESSION_CURRENT_USER):
            del request.session[Constant.SESSION_CURRENT_USER]
        if request.session.get(Constant.SESSION_CURRENT_USER_LOGINNAME):
            del request.session[Constant.SESSION_CURRENT_USER_LOGINNAME]
        return render(request, 'customer_login.html')
