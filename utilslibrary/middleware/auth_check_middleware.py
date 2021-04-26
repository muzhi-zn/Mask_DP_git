from django.utils.deprecation import MiddlewareMixin
from utilslibrary.system_constant import Constant
from django.http.response import HttpResponseRedirect
from django.conf import settings
from django.http.response import JsonResponse


# check auth
from utilslibrary.utils.common_utils import get_ip


class AuthCheckMiddleWare(MiddlewareMixin):
    white_list = [
        '/system/login/', \
        '/system/permission_error/', \
        '/system/menu/getChildren/', \
        '/system/role/user/list/', \
        '/system/office/getChildren/', \
        '/system/user/list/null', \
        '/system/tree/select/', \
        '/system/menu/tree/', \
        '/system/menu/iconselect/', \
        '/system/office/tree/data/', \
        '/system/user/select/', \
        '/system/role/permission/tree/', \
        '/system/menu/generateSubMenu/', \
        '/system/logout/', \
        '/system/menu/sort/', \
        '/tooling/state/msg/', \
        '/__debug__/render_panel/', \
        '/system/user/info/view/', \
        '/system/user/info/edit/', \
        '/system/user/modify/password/', \
        '/system/user/modifyPwd/',
        '/callback/calibrewb/',
        '/iems/callback/',
        '/machine/options/',
        '/system/websocket_connect/',
        '/system/user/permission/tree/',
        # api
        '/making/lot/fracture/callback/',
        '/making/jdv_compile_lot_list/compile_status/',
        '/tooling/test_layout/',
        '/making/call_back_log/list/',
        '/making/call_back_log/del/',
        '/api/auth_account/',
        '/api/ad_conn_test/',
        '/logout/', \
        '/login/', \
        '/making/lot/op_test/',
        # '/form_sop_download'\
        # '/system/role/list'\
        # '/system/menu/list'\
        #   '/system/office/list'\
        #   '/system/dict/list'\
        # '/system/log/list'\
        '/callback/calibrewb_test/',
        '/callback/frame_calibrewb/',
        '/workflow/maskdp/check/',
        '/maintain/customer_ftp/get_customer_code/',
        '/sap_webservice/notice_production_order/',
        '/sap_webservice/ship_or_unship/',
        '/query_system/jdv/test_create_jb_file/'
    ]

    def process_request(self, request):

        # print('AuthCheck process_request:{}'.format(request.path))
        # access login,pass
        if request.path in self.white_list:
            return None
        # check session
        if not request.session.get(Constant.SESSION_CURRENT_USER):
            return HttpResponseRedirect(settings.LOGIN_URL)
        permission_list = request.session.get(Constant.SESSION_CURRENT_USER_PERMISSION_LIST)
        if request.path not in permission_list:
            print("permission error:{}".format(request.path))
            return HttpResponseRedirect(settings.PERMISSION_ERROR_URL)

    def process_view(self, request, callback, callback_args, callback_kwargs):
        pass
        # get permission from session

        # check auth,in permission list
