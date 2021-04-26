# coding:utf-8
"""Mask_DP URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url

from system import websocket_view
from system.maintain_change_log_view import MaintainChangeLog, MaintainChangeLogView, MaintainChangeLogRestore
from system.user_view import Login, Logout, UserList, UserAdd, UserView, UserEdit, UserDel, \
    UserCheckLoginName, UserSelect, UserInfoView, UserInfoForm, UserModifyPassword, Ztree, get_customer_code
from system.dict_view import DictList, DictAdd, DictView, DictEdit, DictDel, DictValueForm, \
    DictValueList, DictValueDel, DictValueListByParentType
from system.role_view import RoleList, RoleEdit, RoleDel, RoleCheckName, \
    RoleUserList, RoleUserOut, RolePermissionView, RolePersmissionTree, RolePersmissionSave, RoleAdd, RoleView

from system.office_view import OfficeList, OfficeAdd, OfficeView, OfficeEdit, OfficeDel, \
    OfficeTreeData, OfficeGetChildren
from system.views import TreeSelect, permission_error

from system.template_view import TemplateList, TemplateRowEdit, TemplateEdit, \
    TemplateAdd, TemplateView, TemplateDel

from system.log_view import LogList, LogForm
from system.menu_view import MenuList, MenuView, MenuAdd, MenuEdit, MenuDel, MenuTree, \
    GetChildren, MenuIconSelect, MenuSort, GenerateSubMenu
from system.data_rule_view import DataRuleAdd, DataRuleEdit, DataRuleDel, DataRuleList, \
    DataRuleView, DataRulePermissionView, DataRulePersmissionTree, DataRulePersmissionSave
from system.websocket_view import websocket_connect, message_resend

from system.tooling_upload_set_view import tooling_upload_set_list, tooling_upload_set_view, tooling_upload_set_add, \
    tooling_upload_set_edit, tooling_upload_set_del, tooling_upload_set_select, tooling_upload_error_msg_list, \
    tooling_upload_error_msg_view, tooling_upload_error_msg_add, tooling_upload_error_msg_edit, \
    tooling_upload_error_msg_del
from system.websocket_view import message_log_list

from system.sgd_view import sgd_user_list, sgd_user_account_list, sgd_user_account_add, \
    sgd_user_account_lock, sgd_user_account_unlock, sgd_user_account_del, sgd_user_account_pdf, \
    sgd_user_account_extension, sgd_user_account_send

from system.sync_view import sync_list, sync_view, sync_add, sync_edit, sync_del, sync_log_list, sync_log_view, \
    sync_log_detail_list

from system.upload_view import file_upload_check, file_upload, file_merge, file_check
from system.service.ldap_auth import ldap_auth

print('路由开始加载 system.urls........')
# from system.ip_view import IPEdit, AddIP, IPList, IPDel
from system.views import Index

urlpatterns = [

    # 用户操作
    url(r'^$', Index.as_view()),

    url(r'^login/$', Login.as_view()),
    url(r'^logout/$', Logout.as_view()),
    url(r'^user/list/$', UserList.as_view()),
    url(r'^user/add/$', UserAdd.as_view()),
    url(r'^user/view/$', UserView.as_view()),
    url(r'^user/edit/$', UserEdit.as_view()),
    url(r'^user/del/$', UserDel.as_view()),
    url(r'^user/get_customer_code/$', get_customer_code),
    url(r'^user_check_loginname/$', UserCheckLoginName.as_view()),
    url(r'^user/select/$', UserSelect.as_view()),
    url(r'^user/info/view/$', UserInfoView.as_view()),
    url(r'^user/info/edit/$', UserInfoForm.as_view()),
    url(r'^user/modify/password/$', UserModifyPassword.as_view()),
    url(r'^user/permission/tree/$', Ztree.as_view()),

    # 操作日志操作
    url(r'^log/list/$', LogList.as_view()),
    url(r'^log/form/$', LogForm.as_view()),

    # IP名单
    # url(r'^ip/list/$', IPList.as_view()),
    # url(r'^ip/add/$', AddIP.as_view()),
    # url(r'^ip/edit/$', IPEdit.as_view()),
    # url(r'^ip/del/$', IPDel.as_view()),

    # 脚本模板操作
    url(r'^template/list/$', TemplateList.as_view()),
    url(r'^template/add/$', TemplateAdd.as_view()),
    url(r'^template/view/$', TemplateView.as_view()),
    url(r'^template/edit/$', TemplateEdit.as_view()),
    url(r'^template/del/$', TemplateDel.as_view()),

    url(r'^template/row/edit/$', TemplateRowEdit.as_view()),

    # dictionary operation
    url(r'^dict/list/$', DictList.as_view()),
    url(r'^dict/add/$', DictAdd.as_view()),
    url(r'^dict/view/$', DictView.as_view()),
    url(r'^dict/edit/$', DictEdit.as_view()),
    url(r'^dict/del/$', DictDel.as_view()),
    url(r'^dict/value/form/$', DictValueForm.as_view()),
    url(r'^dict/value/list/$', DictValueList.as_view()),
    url(r'^dict/value/del/$', DictValueDel.as_view()),
    url(r'^dict/value/list/byParentType/$', DictValueListByParentType.as_view()),

    # role operation
    url(r'^role/list/$', RoleList.as_view()),
    url(r'^role/add/$', RoleAdd.as_view()),
    url(r'^role/view/$', RoleView.as_view()),
    url(r'^role/edit/$', RoleEdit.as_view()),
    url(r'^role/del/$', RoleDel.as_view()),
    url(r'^role/check/name/$', RoleCheckName.as_view()),
    url(r'^role/user/list/$', RoleUserList.as_view()),
    url(r'^role/user/out/$', RoleUserOut.as_view()),
    url(r'^role/permission/view/$', RolePermissionView.as_view()),
    url(r'^role/permission/tree/$', RolePersmissionTree.as_view()),
    url(r'^role/permission/save/$', RolePersmissionSave.as_view()),

    # office opration url
    url(r'^office/list/$', OfficeList.as_view()),
    url(r'^office/add/$', OfficeAdd.as_view()),
    url(r'^office/view/$', OfficeView.as_view()),
    url(r'^office/edit/$', OfficeEdit.as_view()),
    url(r'^office/del/$', OfficeDel.as_view()),
    url(r'^office/tree/data/$', OfficeTreeData.as_view()),
    url(r'^office/getChildren/$', OfficeGetChildren.as_view()),

    # tree select
    url(r'^tree/select/$', TreeSelect.as_view()),

    # menu url
    url(r'^menu/list/$', MenuList.as_view()),
    url(r'^menu/add/$', MenuAdd.as_view()),
    url(r'^menu/view/$', MenuView.as_view()),
    url(r'^menu/edit/$', MenuEdit.as_view()),
    url(r'^menu/del/$', MenuDel.as_view()),
    url(r'^menu/tree/$', MenuTree.as_view()),
    url(r'^menu/getChildren/$', GetChildren.as_view()),
    url(r'^menu/iconselect/$', MenuIconSelect.as_view()),
    url(r'^menu/sort/$', MenuSort.as_view()),
    url(r'^menu/generateSubMenu/$', GenerateSubMenu.as_view()),

    # permission error

    url(r'^permission_error/$', permission_error),

    # data rule url
    url(r'^data/rule/list/$', DataRuleList.as_view()),
    url(r'^data/rule/view/$', DataRuleView.as_view()),
    url(r'^data/rule/add/$', DataRuleAdd.as_view()),
    url(r'^data/rule/edit/$', DataRuleEdit.as_view()),
    url(r'^data/rule/del/$', DataRuleDel.as_view()),
    url(r'^data/rule/permission/view/$', DataRulePermissionView.as_view()),
    url(r'^data/rule/permission/tree/$', DataRulePersmissionTree.as_view()),
    url(r'^data/rule/permission/save/$', DataRulePersmissionSave.as_view()),

    # websocket
    url(r'websocket_connect/', websocket_connect),
    url(r'^message_history/list/$', message_log_list.as_view()),
    url(r'^message_history/resend/$', message_resend.as_view()),

    # tooling upload set
    url(r'^tooling_upload_set/list/$', tooling_upload_set_list.as_view()),
    url(r'^tooling_upload_set/view/$', tooling_upload_set_view.as_view()),
    url(r'^tooling_upload_set/add/$', tooling_upload_set_add.as_view()),
    url(r'^tooling_upload_set/edit/$', tooling_upload_set_edit.as_view()),
    url(r'^tooling_upload_set/del/$', tooling_upload_set_del.as_view()),
    url(r'^tooling_upload_set/select/$', tooling_upload_set_select.as_view()),

    # tooling upload error msg
    url(r'^tooling_upload_error_msg/list/$', tooling_upload_error_msg_list.as_view()),
    url(r'^tooling_upload_error_msg/view/$', tooling_upload_error_msg_view.as_view()),
    url(r'^tooling_upload_error_msg/add/$', tooling_upload_error_msg_add.as_view()),
    url(r'^tooling_upload_error_msg/edit/$', tooling_upload_error_msg_edit.as_view()),
    url(r'^tooling_upload_error_msg/del/$', tooling_upload_error_msg_del.as_view()),

    # sgd
    url(r'^sgd_user/list/$', sgd_user_list.as_view()),
    url(r'^sgd_user_account/list/$', sgd_user_account_list.as_view()),
    url(r'^sgd_user_account/add/$', sgd_user_account_add.as_view()),
    url(r'^sgd_user_account/lock/$', sgd_user_account_lock.as_view()),
    url(r'^sgd_user_account/unlock/$', sgd_user_account_unlock.as_view()),
    url(r'^sgd_user_account/del/$', sgd_user_account_del.as_view()),
    url(r'^sgd_user_account/extension/$', sgd_user_account_extension.as_view()),
    url(r'^sgd_user_account/pdf/$', sgd_user_account_pdf.as_view()),
    url(r'^sgd_user_account/send/$', sgd_user_account_send.as_view()),

    # sync
    url(r'^sync/list/$', sync_list.as_view()),
    url(r'^sync/view/$', sync_view.as_view()),
    url(r'^sync/add/$', sync_add.as_view()),
    url(r'^sync/edit/$', sync_edit.as_view()),
    url(r'^sync/del/$', sync_del.as_view()),
    url(r'^sync/log/list/$', sync_log_list.as_view()),
    url(r'^sync/log/view/$', sync_log_view.as_view()),
    url(r'^sync/log/detail/list/$', sync_log_detail_list.as_view()),

    # upload
    url(r'^upload/file_upload_check/$', file_upload_check),
    url(r'^upload/file_upload/$', file_upload),
    url(r'^upload/file_check/$', file_check),
    url(r'^upload/file_merge/$', file_merge),


    # maintain change log
    url(r'^maintain_change_log/list/$', MaintainChangeLog.as_view()),
    url(r'^maintain_change_log/view/$', MaintainChangeLogView.as_view()),
    url(r'^maintain_change_log/restore/$', MaintainChangeLogRestore.as_view()),
]
