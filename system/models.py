from django.db import models
from django.db.models.fields import CharField
from django.template.defaultfilters import default
from utilslibrary.base.base import BaseModel
from datetime import datetime


# Create your models here.
class user(BaseModel):
    loginname = models.CharField(max_length=256, null=False, default='')
    passwd = models.CharField(max_length=256, null=False, default='')
    realname = models.CharField(max_length=256, null=False, default='')
    age = models.IntegerField(default=0, null=True)
    addr = models.CharField(max_length=256, null=True)
    email = models.CharField(max_length=128, null=True)
    mobile = models.CharField(max_length=128, null=True)
    phone = models.CharField(max_length=128, null=True)
    icon = models.CharField(max_length=512, null=True)
    office_id = models.CharField(max_length=512, null=True)
    office_name = models.CharField(max_length=512, null=True)

    isadmin = models.IntegerField(default=0)
    addr = models.CharField(max_length=512, null=True)

    remarks = models.CharField(max_length=512, null=True)
    loginflag = models.IntegerField(default=0, null=True)

    ldap = models.IntegerField(default=0)
    ldap_group = models.IntegerField(default=0)

    customer_code_id = models.IntegerField(default=0)
    customer_code = models.CharField(max_length=128, null=True)


# dictionary model
class dict(BaseModel):
    id = models.AutoField(primary_key=True)
    value = models.CharField(max_length=256, null=False, default='')
    label = models.CharField(max_length=256, null=False, default='')
    type = models.CharField(max_length=256, null=False, default='')
    description = models.CharField(max_length=256, null=True, default='')
    sort = models.IntegerField(null=False, default=0)
    parent_id = models.CharField(max_length=256, null=True, default='')


# log into db
class log(BaseModel):
    id = models.AutoField(primary_key=True)
    obj = models.CharField(max_length=256, null=False, default='')
    data_id = models.CharField(max_length=256, null=True, default='')
    user_id = models.CharField(max_length=256, null=False, default='')
    user_name = models.CharField(max_length=256, null=False, default='')
    action = models.CharField(max_length=256, null=False, default='')
    json = models.CharField(max_length=2048, null=False, default='')
    ip = models.CharField(max_length=56, null=False, default='')


# system role model
class role(BaseModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, null=False, default='')
    role_type = models.CharField(max_length=256, null=False, default='')
    useable = models.IntegerField(null=False, default=1)
    remarks = models.CharField(max_length=256, null=True, default='')


# office model
class office(BaseModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, null=False, default='')
    parent_id = models.CharField(max_length=256, null=True, default='')
    parent_ids = models.CharField(max_length=256, null=True, default='')
    parent_name = models.CharField(max_length=256, null=True, default='')

    type = models.CharField(max_length=64, null=True, default='')

    sort = models.IntegerField(null=False, default=0)
    area_id = models.CharField(max_length=256, null=True, default='')
    code = models.CharField(max_length=256, null=False, default='')
    useable = models.IntegerField(null=False, default=1)
    remarks = models.CharField(max_length=256, null=True, default='')


# user role correlation
class user_role(BaseModel):
    user = models.ForeignKey('user',
                             null=True,
                             on_delete=models.CASCADE)
    role = models.ForeignKey('role',
                             null=True,
                             on_delete=models.CASCADE)


class menu(BaseModel):
    id = models.AutoField(primary_key=True)
    parent_id = models.IntegerField(null=False, default=0)
    parent_name = models.CharField(max_length=256, null=True, default='')
    parent_ids = models.CharField(max_length=256, null=True, default='')
    name = models.CharField(max_length=256, null=False, default='')
    sort = models.IntegerField(null=False, default=0)
    href = models.CharField(max_length=256, null=True, default='')
    base_href = models.CharField(max_length=256, null=True, default='')
    is_show = models.IntegerField(null=False, default=0)
    type = models.IntegerField(null=False, default=0)
    has_children = models.CharField(max_length=256, null=True, default='false')
    icon = models.CharField(max_length=256, null=True, default='')
    remarks = models.CharField(max_length=256, null=True, default='')


class role_menu(BaseModel):
    id = models.AutoField(primary_key=True)
    role = models.ForeignKey('role',
                             null=False,
                             on_delete=models.CASCADE)

    menu = models.ForeignKey('menu',
                             null=True,
                             on_delete=models.CASCADE)
    # -----------------------------------------------
    # 为角色赋值菜单时，菜单保存类型为0，按钮为1，
    # 显示角色有哪些菜单权限时，只查询1
    # 首页左侧菜单显示时，查询所有
    # -----------------------------------------------
    type = models.IntegerField(null=False, default=0)


class template(BaseModel):
    id = models.AutoField(primary_key=True)
    template_type = models.CharField(max_length=256, null=False, default='')
    dict_type = models.CharField(max_length=256, null=False, default='')

    template_name = models.CharField(max_length=256, null=False, default='')
    file_name = models.CharField(max_length=256, null=False, default='')
    file_extension = models.CharField(max_length=256, null=True, default='')
    template_json = models.CharField(max_length=2048, null=False, default='')
    template_text = models.CharField(max_length=2048, null=False, default='')


class data_rule(BaseModel):
    id = models.AutoField(primary_key=True)
    menu_id = models.IntegerField(null=False, default=0)  # 所属按钮
    name = models.CharField(max_length=256, null=False, default='')  # 规则名称
    r_filed = models.CharField(max_length=256, null=False, default='')  # 规则字段
    r_express = models.CharField(max_length=256, null=False, default='')  # 规则条件
    r_value = models.CharField(max_length=256, null=False, default='')  # 规则值
    class_name = models.CharField(max_length=256, null=False, default='')  # 实体类名
    remarks = models.CharField(max_length=256, null=False, default='')  # remarks


class role_data_rule(BaseModel):
    id = models.AutoField(primary_key=True)
    role = models.ForeignKey('role',
                             null=True,
                             on_delete=models.CASCADE)
    data_rule = models.ForeignKey('data_rule',
                                  null=True,
                                  on_delete=models.CASCADE)


class message_log(BaseModel):
    """消息发送记录"""
    models.AutoField
    message_id = models.CharField(max_length=20, null=False)
    user_id = models.IntegerField()
    message_type = models.CharField(max_length=20)
    message_tag = models.CharField(max_length=255)
    message = models.TextField()
    # 0 未确认收到 1 已确认收到
    status = models.IntegerField(default=0)
    send_time = models.CharField(max_length=255)
    confirm_time = models.CharField(max_length=255)


# SGD User
class sgd_user(BaseModel):
    id = models.AutoField(primary_key=True)
    tip_no = models.CharField(max_length=255)
    user_name = models.CharField(max_length=255)
    user_pwd = models.CharField(max_length=255)
    pdf_pwd = models.CharField(max_length=255)
    original_expire_date = models.CharField(max_length=45, null=True, default="")  # SGD帳號原始到期日
    extension = models.IntegerField(default=0)  # 展延次數
    extension_expire_date = models.CharField(max_length=45, null=True, default="")  # SGD帳號目前到期日
    is_lock = models.IntegerField(default=0)


# PDF Log
class sgd_pdf_log(BaseModel):
    id = models.AutoField(primary_key=True)
    sgd_user_id = models.IntegerField(default=0)
    pdf_path = models.CharField(max_length=255)


# Email Log
class sgd_email_log(BaseModel):
    id = models.AutoField(primary_key=True)
    sgd_user_id = models.IntegerField(default=0)


# Sync
class sync_config(BaseModel):
    id = models.AutoField(primary_key=True)
    sync_name = models.CharField(max_length=255)
    enable = models.BooleanField(default=0)
    '''intreval, cron '''
    mode = models.CharField(max_length=255)
    mode_time = models.CharField(max_length=255)
    ldap_server_pool = models.CharField(max_length=255)
    ldap_server_port = models.CharField(max_length=255)
    admin_dn = models.CharField(max_length=255)
    admin_pwd = models.CharField(max_length=255)
    search_base = models.CharField(max_length=255)
    group = models.CharField(max_length=255)
    '''default user status 1:enable 0:disable '''
    default = models.BooleanField(default=0)


class sync_log(BaseModel):
    id = models.AutoField(primary_key=True)
    config_id = models.IntegerField(default=0)
    # 1: 成功 2:錯誤 3:同步中
    status = models.IntegerField(default=0)
    remark = models.CharField(max_length=255, default='')
    run_time = models.DateTimeField(default='1970-01-01')
    duration = models.FloatField(default=0)
    started = models.FloatField(default=0)
    finished = models.FloatField(default=0)
    add = models.IntegerField(default=0)
    enable = models.IntegerField(default=0)
    cancel = models.IntegerField(default=0)


class sync_log_detail(BaseModel):
    id = models.AutoField(primary_key=True)
    log_id = models.IntegerField(default=0)
    # status 0:add 1:cancel
    status = models.CharField(max_length=255)
    user = models.CharField(max_length=255)


# Upload
class upload_info(BaseModel):
    id = models.AutoField(primary_key=True)
    sub_id = models.CharField(max_length=255, default='')
    file_name = models.CharField(max_length=255, default='')
    file_size = models.CharField(max_length=255, default='')
    file_path = models.CharField(max_length=255, default='')
    file_type = models.CharField(max_length=255, default='')
    file_value = models.CharField(max_length=255, default='')
    file_size_check_status = models.IntegerField(default=0)
    file_type_check_status = models.IntegerField(default=0)
    iems_record_no = models.CharField(max_length=20, null=True, blank=True)
    analysis_status = models.IntegerField(default=0)
    analysis_message = models.CharField(max_length=255, null=True, blank=True)
    result_file_name = models.CharField(max_length=500, default='')
    result = models.CharField(max_length=5000, default='')
    precision = models.CharField(max_length=255, default='')
    precision_check_status = models.IntegerField(default=0)
    topcell = models.CharField(max_length=255, default='')
    topcell_check_status = models.IntegerField(default=0)
    layers = models.CharField(max_length=2500, default='')
    layers_check_status = models.IntegerField(default=0)
    bbox = models.CharField(max_length=255, default='')
    bbox_check_status = models.IntegerField(default=0)
    analysis_check_status = models.IntegerField(default=0)
