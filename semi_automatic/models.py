from django.db import models

# Create your models here.


class lot_record(models.Model):
    """手动启动的lot记录"""
    models.AutoField
    tip_no = models.CharField(max_length=100, null=False)
    mask_name = models.CharField(max_length=50, null=False)
    layer = models.CharField(max_length=20, null=False)
    tone = models.CharField(max_length=20, null=False)
    tip_tech = models.CharField(max_length=20, null=False)
    grade = models.CharField(max_length=20, null=False)
    product_type = models.CharField(max_length=100, null=False)
    customer_code = models.CharField(max_length=10, null=False)
    purpose = models.CharField(max_length=10, null=False)
    order_type = models.CharField(max_length=20, null=False)
    exp_tool = models.CharField(max_length=100, null=False)
    blank_code = models.CharField(max_length=20, null=False)
    pellicle_code = models.CharField(max_length=200, null=False)
    design_rule = models.CharField(max_length=20, null=False)
    delivery_fab = models.CharField(max_length=100, null=False)
    wave_length = models.IntegerField(null=False)
    lot_id = models.CharField(max_length=255)
    lot_result = models.CharField(max_length=255, null=True)
    is_delete = models.IntegerField(default=0)  # 删除标识


class writer_ftp_record(models.Model):
    """编锅操作记录"""
    id = models.AutoField
    lot_record_id = models.IntegerField(null=False)
    lot_id = models.CharField(max_length=255, null=False)
    level = models.IntegerField(null=False)
    writer_ftp_status = models.IntegerField(default=0)  # 0/未上传 1/上传中 2/上传失败 3/上传成功
    writer_local_path = models.CharField(max_length=500, null=True)
    writer_ftp_result = models.CharField(max_length=255, null=True)
    writer_ftp_start_time = models.CharField(max_length=255, null=True)
    writer_ftp_end_time = models.CharField(max_length=255, null=True)
    is_delete = models.IntegerField(default=0)  # 删除标识


class catalog_record(models.Model):
    """上传writer的操作记录"""
    id = models.AutoField
    lot_record_id = models.IntegerField(null=False)
    lot_id = models.CharField(max_length=255, null=False)
    level = models.IntegerField(null=False)
    catalog_status = models.IntegerField(default=0)  # 编锅状态 0/未编锅 1/编锅中 2/编锅失败 3/编锅成功
    catalog_result = models.CharField(max_length=500, null=True)
    catalog_start_time = models.CharField(max_length=255, null=True)
    catalog_end_time = models.CharField(max_length=255, null=True)
    is_delete = models.IntegerField(default=0)  # 删除标识


class LotCreateLog(models.Model):
    """生成lot的记录"""
    pass
