from django.db import models

# Create your models here.
from utilslibrary.base.base import BaseModel


class jdv_data(models.Model):
    id = models.AutoField
    tip_no = models.CharField(max_length=255, null=False)
    lot_id = models.CharField(max_length=255, null=False)
    customer_code = models.CharField(max_length=10)
    product_name = models.CharField(max_length=255, null=False)
    mask_name = models.CharField(max_length=255, null=False)
    jdv_account = models.CharField(max_length=255, null=True)
    start_date = models.CharField(max_length=255, null=True)  # 开始时间
    end_date = models.CharField(max_length=255, null=True)  # 结束时间
    sgd_user_name = models.CharField(max_length=255, null=True)
    sgd_password = models.CharField(max_length=255, null=True)
    send_email_status = models.IntegerField(default=0)
    send_email_date = models.CharField(max_length=255, null=True)
    # 0: not release 1: release
    release_status = models.IntegerField(default=0)
    customer_release_date = models.CharField(max_length=255, null=True)
    # 0: not hold 1:hold
    hold_status = models.IntegerField(default=0)
    job_deck_name = models.CharField(max_length=255, null=True)
    job_deck_path = models.CharField(max_length=1000, null=True)
    dp_release_user = models.CharField(max_length=255, null=True)
    dp_release_date = models.CharField(max_length=255, null=True)
    note = models.TextField(null=True)


class jdv_data_device(models.Model):
    """device"""
    id = models.AutoField
    jdv_data_id = models.IntegerField()
    device = models.CharField(max_length=255)
    mask_name = models.CharField(max_length=255)
    is_need_upload = models.IntegerField(default=0)
    create_date = models.CharField(max_length=255)
    is_upload = models.IntegerField(default=0)
    upload_date = models.CharField(max_length=255, null=True)


class jdv_data_layer(models.Model):
    """jdv_data下的layer"""
    id = models.AutoField
    jdv_data_id = models.IntegerField()
    mask_name = models.CharField(max_length=255, null=True)
    layer = models.CharField(max_length=10)
    is_need_upload = models.IntegerField(default=0)
    create_date = models.CharField(max_length=255)
    is_upload = models.IntegerField(default=0)
    upload_date = models.CharField(max_length=255, null=True)
    is_release = models.IntegerField(default=0)
    release_date = models.CharField(max_length=255, null=True)
    release_user_id = models.IntegerField(null=True)
    release_user_name = models.CharField(max_length=255, null=True)