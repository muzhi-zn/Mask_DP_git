from django.db import models

# Create your models here.
from utilslibrary.base.base import BaseModel


class tool_maintain(BaseModel):
    models.AutoField
    tool_id = models.CharField(default='', max_length=255, null=False)
    group_name = models.CharField(default='', max_length=255, null=False)
    exptool = models.CharField(default='', max_length=255, null=False)
    ip = models.CharField(default='', max_length=255, null=False)
    account = models.CharField(default='', max_length=255, null=False)
    password = models.CharField(default='', max_length=255, null=False)
    path = models.CharField(default='', max_length=255, null=False)
    tool_type = models.CharField(default='', max_length=255, null=False)


class group_maintain(BaseModel):
    models.AutoField
    group_id = models.CharField(default='', max_length=255, null=False)
    tool = models.CharField(default='', max_length=255, null=False)
    tool_name = models.CharField(default='', max_length=255, null=False)
    info_tree_name = models.CharField(default='', max_length=255, null=False)


class tool_name_route(BaseModel):
    models.AutoField
    catalog_tool_id = models.CharField(default='', max_length=255, null=False)
    writer_name = models.CharField(default='', max_length=255, null=False)
    info_tree_name = models.CharField(default='', max_length=255, null=False)
    machine_type = models.CharField(default='', max_length=255, null=False)


class alta_catalog_queue(BaseModel):
    models.AutoField
    lot_id = models.CharField(default='', max_length=255, null=False)
    level = models.IntegerField(default=0, null=False)
    ftp_status = models.IntegerField(default=0, null=False)# 0：未ftp， 1：ftp中， 2：ftp完成， 3：ftp错误
    catalog_status = models.IntegerField(default=0, null=False)# 0:未编锅，1：编锅中，2：编锅完成，3：编锅错误
    error_msg = models.CharField(default='', max_length=255, null=False)