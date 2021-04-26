import datetime

import django
from django.db import models

# Create your models here.
from utilslibrary.base.base import BaseModel


class customer_code(BaseModel):
    models.AutoField
    code = models.CharField(default='', max_length=10, null=False)
    customer = models.CharField(default='', max_length=50, null=False)
    remark = models.CharField(max_length=255, null=True)


class pellicle_mapping(BaseModel):
    models.AutoField
    mt_form_pellicle = models.CharField(max_length=100, null=False)
    mes_pellicle_code = models.CharField(max_length=100, null=False)


class maintain_change_log(models.Model):
    id = models.AutoField
    table = models.CharField(max_length=255)
    data_id = models.IntegerField()
    operation = models.CharField(max_length=255, default='')
    upt_time = models.DateTimeField(default=django.utils.timezone.now)
    change_user = models.CharField(max_length=255)
    old_data = models.TextField(default="{'No': 'Data'}")
    new_data = models.TextField(default="{'No': 'Data'}")


class customer_ftp_account(BaseModel):
    id = models.AutoField
    customer_code = models.CharField(max_length=255)
    ftp_ip = models.CharField(max_length=255)
    account = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    ftp_type = models.CharField(max_length=255, null=True)
    ftp_port = models.CharField(max_length=255, null=True)
    ftp_path = models.CharField(max_length=255, null=True)
    product = models.CharField(max_length=255, null=True)
    enable = models.CharField(max_length=255)
    date = models.IntegerField(null=True,default=0)

class data_in_table(models.Model):
    id = models.AutoField
    ftp_data_id = models.IntegerField(null=True)
    customer = models.CharField(max_length=255)
    product_name = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255)
    file_name_serial = models.CharField(max_length=255)
    file_size = models.CharField(max_length=255,null=True)
    md5sum = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    is_delete = models.IntegerField(default=0)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    date = models.IntegerField(null=True)
    md5_pass = models.CharField(max_length=255,null=True)
    last_check_size = models.CharField(max_length=255,null=True)
    upt_time = models.DateTimeField(default=django.utils.timezone.now)
    downloaded = models.IntegerField(default=0)
    temp_name = models.CharField(max_length=255,null=True)
    serial_path = models.CharField(max_length=255,null=True)

class ftp_data_table(models.Model):
    id = models.AutoField
    customer = models.CharField(max_length=255)
    product_name = models.CharField(max_length=255)
    ftp_path = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255)
    file_size = models.CharField(max_length=255,null=True)
    md5sum = models.CharField(max_length=255, null=True)
    md5_pass = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=255)
    is_delete = models.IntegerField(default=0)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    date = models.IntegerField(null=True)
    last_check_size = models.CharField(max_length=255,null=True)
    upt_time = models.DateTimeField(default=django.utils.timezone.now)
    downloaded = models.IntegerField(default=0)
    file_name_decrypt = models.CharField(max_length=255,null=True)
    ftp_type = models.CharField(max_length=255, null=True)

class retention_data_table(models.Model):
    id = models.AutoField
    ftp_data_id =  models.IntegerField(null=True)
    customer = models.CharField(max_length=255)
    product_name = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255)
    file_size = models.CharField(max_length=255,null=True)
    status = models.CharField(max_length=255)
    is_delete = models.IntegerField(default=0)
    ship_time = models.DateTimeField(null=True)
    expire_time = models.DateTimeField(null=True)
    date = models.IntegerField(null=True)

