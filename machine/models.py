from django.db import models
from utilslibrary.base.base import BaseModel


# Create your models here.


class machine_basic(BaseModel):
    id = models.AutoField(primary_key=True)
    machine_name = models.CharField(max_length=256, null=True)
    machine_ip = models.CharField(max_length=256, null=True)
    machine_type = models.CharField(max_length=256, null=True)
    machine_account = models.CharField(max_length=256, null=True)
    machine_password = models.CharField(max_length=256, null=True)
    machine_remark = models.CharField(max_length=256, null=True)
    ftp_ip = models.CharField(max_length=256, null=True)
    ftp_path = models.CharField(max_length=256, null=True)
    ftp_account = models.CharField(max_length=256, null=True)
    ftp_password = models.CharField(max_length=256, null=True)


class machine_script_templates(BaseModel):
    id = models.AutoField(primary_key=True)
    machine_basic_id = models.IntegerField(null=False, default=0)
    template_id = models.IntegerField(null=False, default=0)
    template_type = models.CharField(max_length=256, null=False, default='')


class writer_mapping(BaseModel):
    models.AutoField
    seq = models.IntegerField()
    customer = models.CharField(max_length=100, null=True)
    design_rule = models.CharField(max_length=100, null=True)
    product = models.CharField(max_length=100, null=True)
    layer_name = models.CharField(max_length=100, null=True)
    product_type = models.CharField(max_length=100, null=True)
    grade_from = models.CharField(max_length=100, null=True)
    grade_to = models.CharField(max_length=100, null=True)
    mask_type = models.CharField(max_length=100, null=True)
    tone = models.CharField(max_length=100, null=True)
    machine_id = models.IntegerField(null=True)
    exp_tool = models.CharField(max_length=100, null=True)
    comment = models.CharField(max_length=255, null=True)
    book_user_id = models.IntegerField()
    book_user_name = models.CharField(max_length=255)
    book_time = models.CharField(max_length=100, null=True)
    info_tree_tool_id = models.CharField(max_length=50, null=True)
    catalog_tool_id = models.CharField(max_length=50, null=True)
