from django.shortcuts import render, HttpResponse
from django.http.response import JsonResponse

from tooling_form.models import product_info
from utilslibrary.base.base import BaseView
from system.models import user, sgd_user, sgd_pdf_log, sgd_email_log
from django.db.models import Q
from system.service.sgd_service import SGDService
from random import Random

from utilslibrary.system_constant import Constant
from utilslibrary.utils.ssh_utils import SSHManager, SGD_Account
from jdv.service.pdf_service import get_mail_pdf
from jdv.service.email_service import send_mail


# sgd_user_list
class sgd_user_list(BaseView):

    def get(self, request):
        if request.method == 'GET':
            return render(request, 'system_sgd_user_list.html')

    def post(self, request):
        """根据查询条件获取 tip_no list"""
        if request.method == 'POST':
            # user_id = request.session.get(Constant.SESSION_CURRENT_USER_ID)
            super().post(request)
            q = Q()
            q.connector = 'and'
            q.children.append(('is_delete', 0))

            product_info_list = product_info.objects.filter(q).order_by('id').values()[self.startIndex: self.endIndex]

            data = {}
            data['total'] = product_info.objects.filter(q).count()
            data['rows'] = list(product_info_list)

            print(data['total'], data['rows'])

            return JsonResponse(data, safe=False)


# sgd_user_list
class sgd_user_account_list(BaseView):

    def get(self, request):
        if request.method == 'GET':
            return render(request, 'system_sgd_user_list.html')

    def post(self, request):
        """根据查询条件获取 mdt_info"""
        if request.method == 'POST':
            # user_id = request.session.get(Constant.SESSION_CURRENT_USER_ID)
            tip_no = request.POST.get('tip_no')
            super().post(request)
            q = Q()
            q.connector = 'and'
            q.children.append(('is_delete', 0))

            if id:
                q.children.append(('tip_no', tip_no))

            print(q)
            user_account_list = sgd_user.objects.filter(q).order_by('id').values()[self.startIndex: self.endIndex]

            data = {}
            data['total'] = sgd_user.objects.filter(q).count()
            data['rows'] = list(user_account_list)

            print(data['total'], data['rows'])

            return JsonResponse(data, safe=False)


# sgd_user_account_add
class sgd_user_account_add(BaseView):

    def get(self, request):
        data = {}
        # sgd_user_add
        tip_no = request.GET.get('tip_no')

        result = create_sgd()

        if result[0] == 1:
            sgd_account = result[1]
            sgd_pwd = result[2]
            pdf_pwd = result[3]
            original_expire_date = result[4]

            print(sgd_account, sgd_pwd, pdf_pwd, original_expire_date)

            _o = sgd_user()

            _o.tip_no = tip_no
            _o.user_name = sgd_account
            _o.user_pwd = sgd_pwd
            _o.pdf_pwd = pdf_pwd
            _o.original_expire_date = original_expire_date
            _o.extension = 0
            _o.extension_expire_date = original_expire_date

            _s = SGDService()

            return _s.add_sgd_user(_o)
        else:
            data["success"] = False
            data["msg"] = result[1]
            return JsonResponse(data, safe=False)


# sgd_user_account_lock
class sgd_user_account_lock(BaseView):
    def get(self, request):
        data = {}
        # sgd_user_lock
        id = request.GET.get('id')
        print(id)
        user_name = sgd_user.objects.get(id=id).user_name
        result = sgd_user_lock(user_name)

        if result == 1:
            _o = sgd_user.objects.get(id=id)
            _o.is_lock = 1

            _s = SGDService()
            return _s.lock_sgd_user(_o)
        else:
            data["success"] = False
            data["msg"] = 'Failed'
            return JsonResponse(data, safe=False)


# sgd_user_account_unlock
class sgd_user_account_unlock(BaseView):
    def get(self, request):
        data = {}
        # sgd_user_unlock
        id = request.GET.get('id')
        print(id)
        user_name = sgd_user.objects.get(id=id).user_name
        result = sgd_user_unlock(user_name)

        if result == 1:
            _o = sgd_user.objects.get(id=id)
            _o.is_lock = 0

            _s = SGDService()
            return _s.unlock_sgd_user(_o)
        else:
            data["success"] = False
            data["msg"] = 'Failed'
            return JsonResponse(data, safe=False)


# sgd_user_account_extension
class sgd_user_account_extension(BaseView):

    def get(self, request):
        data = {}
        # sgd_user_add
        id = request.GET.get('id')

        # 查詢 user_name & extension_expire_date
        sgd_user_data = sgd_user.objects.get(id=id)
        user_name = sgd_user_data.user_name
        extension_date = sgd_user_data.extension_expire_date
        extension = sgd_user_data.extension
        print(user_name, extension_date)

        result = extension_sgd(user_name, extension_date)
        print(result[0], result[1])

        if result[0] == 1:
            _o = sgd_user.objects.get(id=id)
            _o.id = id
            _o.extension = int(extension) + 1
            _o.extension_expire_date = result[1]

            _s = SGDService()
            return _s.extension_sgd_user(_o)
        else:
            data["success"] = False
            data["msg"] = 'Failed'
            return JsonResponse(data, safe=False)


# sgd_user_account_del
class sgd_user_account_del(BaseView):

    def get(self, request):
        data = {}
        # sgd_user_add
        ids = request.GET.get('ids')
        print('ididi = ', ids)
        user_name = sgd_user.objects.get(id=ids).user_name
        print(user_name)
        result = del_sgd(user_name)
        print(result)

        if result == 1:
            _o = sgd_user()
            _o.id = ids

            _s = SGDService()
            return _s.del_sgd_user(_o)
        else:
            data["success"] = False
            data["msg"] = 'Failed'
            return JsonResponse(data, safe=False)


# sgd_user_account_pdf
class sgd_user_account_pdf(BaseView):
    def get(self, request):
        data = {}
        # sgd_user_add
        id = request.GET.get('id')
        sgd_user_data = sgd_user.objects.get(id=id)
        user_name = sgd_user_data.user_name
        user_pwd = sgd_user_data.user_pwd
        pdf_pwd = sgd_user_data.pdf_pwd
        expire_date = sgd_user_data.extension_expire_date

        result = get_mail_pdf(user_name, user_pwd, pdf_pwd, expire_date)

        if result[0]:
            _o = sgd_pdf_log()
            _o.sgd_user_id = id
            _o.pdf_path = result[1]

            _s = SGDService()

            return _s.upd_pdf_sgd_user(_o)
        else:
            data["success"] = False
            data["msg"] = 'Failed'
            return JsonResponse(data, safe=False)


# sgd_user_account_send
class sgd_user_account_send(BaseView):

    def get(self, request):
        data = {}
        # sgd_user_add
        id = request.GET.get('id')
        sgd_user_data = sgd_user.objects.get(id=id)
        user_name = sgd_user_data.user_name
        pdf_pwd = sgd_user_data.pdf_pwd

        pdf_path = sgd_pdf_log.objects.filter(sgd_user_id=id).order_by('-id').values('pdf_path')[0]['pdf_path']
        pdf_name = pdf_path[pdf_path.rfind('\\') + 1:]
        print(user_name, pdf_pwd, pdf_path, pdf_name)

        try:
            send_mail(pdf_pwd, pdf_path, pdf_name)
            _o = sgd_email_log()
            _o.sgd_user_id = id

            _s = SGDService()
            return _s.upd_send_sgd_user(_o)
        except:
            data["success"] = False
            data["msg"] = 'Failed'
            return JsonResponse(data, safe=False)


def create_sgd():
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()

    # 生成pdf密碼
    pdf_pwd = ''
    for i in range(8):
        pdf_pwd += chars[random.randint(0, length)]
    print(pdf_pwd)

    # 生成SGD帳號
    sgd_account = ''
    for i in range(6):
        sgd_account += chars[random.randint(0, length)]
    print(sgd_account)

    # 生成SGD密碼
    sgd_pwd = ''
    for i in range(8):
        sgd_pwd += chars[random.randint(0, length)]
    print(sgd_pwd)

    server_ip = Constant.SGD_SERVER_IP
    root_name = Constant.SGD_SERVER_ROOT_ACCOUNT
    root_pwd = Constant.SGD_SERVER_ROOT_PASSWORD
    user_name = sgd_account
    user_pwd = sgd_pwd

    # 創建使用者
    cmd_user_add = 'useradd -p `openssl passwd -1 -salt "some" ' + user_pwd + '` ' + user_name
    _o = SGD_Account(server_ip, root_name, root_pwd)
    add_user_result = _o.ssh_exec_cmd(cmd_user_add)
    print(add_user_result)
    _o.__del__()

    # 查詢30天後日期(到期日)
    _o = SGD_Account(server_ip, root_name, root_pwd)
    cmd_check_expiredate = 'date -d "+30 days" +"%Y-%m-%d"'
    check_expiredate_result = _o.ssh_exec_cmd(cmd_check_expiredate).replace('\n', '')
    print(check_expiredate_result)

    # 設置帳號到期日
    cmd_expiredate = 'usermod -e ' + check_expiredate_result + ' ' + user_name
    print(cmd_expiredate)
    expiredate_result = _o.ssh_exec_cmd(cmd_expiredate)
    print(expiredate_result)
    _o.__del__()

    # # 查詢到期日
    # cmd_chage = 'chage -l ' + user_name
    # chage_result = _o.ssh_exec_cmd(cmd_chage)

    if add_user_result == '':
        # 確認使用者家目錄是否存在
        cmd_check_home = "/home/" + user_name + "/"
        _o = SGD_Account(server_ip, root_name, root_pwd)
        check_home_result = _o.ssh_exec_cmd(cmd_check_home)[-15:].replace('\n', '')
        _o.__del__()

        if check_home_result == 'Is a directory':

            # 修改 .bashrc
            # _o = SGD_Account(server_ip, user_name, user_pwd)
            # edit_bashrc = "sed -i '$a\\\\nLM_LICENSE_FILE=27019@license01;export LM_LICENSE_FILE\\nHOTSCOPE_HOME=/App/ver7.22.0/;export HOTSCOPE_HOME\\nsource $HOTSCOPE_HOME/setup.sh' .bashrc"
            # edit_bashrc_result = _o.ssh_exec_cmd(edit_bashrc)
            _o.__del__()
        else:
            del_sgd(sgd_account)
            return 0, check_home_result
    else:
        del_sgd(sgd_account)
        return 0, add_user_result

    return 1, sgd_account, sgd_pwd, pdf_pwd, check_expiredate_result


def sgd_user_lock(sgd_account):
    server_ip = Constant.SGD_SERVER_IP
    root_name = Constant.SGD_SERVER_ROOT_ACCOUNT
    root_pwd = Constant.SGD_SERVER_ROOT_PASSWORD
    user_name = sgd_account

    # 鎖定使用者
    _o = SSHManager(server_ip, root_name, root_pwd)
    cmd_lock = 'passwd -l ' + user_name
    kill_process_result = _o.ssh_exec_cmd(cmd_lock)
    print(kill_process_result)
    _o.__del__()

    return 1


def sgd_user_unlock(sgd_account):
    server_ip = Constant.SGD_SERVER_IP
    root_name = Constant.SGD_SERVER_ROOT_ACCOUNT
    root_pwd = Constant.SGD_SERVER_ROOT_PASSWORD
    user_name = sgd_account

    # 解鎖
    _o = SSHManager(server_ip, root_name, root_pwd)
    cmd_unlock = 'passwd -u ' + user_name
    kill_process_result = _o.ssh_exec_cmd(cmd_unlock)
    print(kill_process_result)
    _o.__del__()

    return 1


def extension_sgd(sgd_account, extension_date):
    server_ip = Constant.SGD_SERVER_IP
    root_name = Constant.SGD_SERVER_ROOT_ACCOUNT
    root_pwd = Constant.SGD_SERVER_ROOT_PASSWORD
    user_name = sgd_account
    extension_expire_date = extension_date

    # 查詢30天後日期(到期日)
    _o = SGD_Account(server_ip, root_name, root_pwd)
    cmd_check_expiredate = 'date -d "' + extension_expire_date + ' +30 days" +"%Y-%m-%d"'
    check_expiredate_result = _o.ssh_exec_cmd(cmd_check_expiredate).replace('\n', '')
    print(check_expiredate_result)

    # 設置帳號到期日
    cmd_expiredate = 'usermod -e ' + check_expiredate_result + ' ' + user_name
    print(cmd_expiredate)
    expiredate_result = _o.ssh_exec_cmd(cmd_expiredate)
    print(expiredate_result)
    _o.__del__()

    return 1, check_expiredate_result


def del_sgd(sgd_account):
    server_ip = Constant.SGD_SERVER_IP
    root_name = Constant.SGD_SERVER_ROOT_ACCOUNT
    root_pwd = Constant.SGD_SERVER_ROOT_PASSWORD
    user_name = sgd_account

    # 刪除使用者所有進程
    _o = SSHManager(server_ip, root_name, root_pwd)
    cmd_kill = 'pkill -u ' + user_name
    kill_process_result = _o.ssh_exec_cmd(cmd_kill)
    print(kill_process_result)
    _o.__del__()

    # 刪除帳號與家目錄
    _o = SSHManager(server_ip, root_name, root_pwd)
    cmd_del = 'userdel ' + user_name + ' -r'
    del_user_result = _o.ssh_exec_cmd(cmd_del)
    print(del_user_result)
    _o.__del__()

    return 1
