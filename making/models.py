from django.db import models
from utilslibrary.base.base import BaseModel


class convert_status_stage(models.Model):
    """convert_status 站点相关信息表"""
    models.AutoField()
    stage_name = models.CharField(max_length=20, null=True)
    flow = models.CharField(max_length=20, null=True)
    pre_stage = models.CharField(max_length=255, null=True)
    # 0 顶级站点
    parent_stage_id = models.IntegerField(default=0)
    operation = models.CharField(max_length=255, null=True)
    # 站点类型 1 需要显示的站点
    type = models.IntegerField(default=1)
    device_type = models.CharField(max_length=255, null=True)
    order = models.FloatField(null=True)
    link = models.CharField(max_length=255, null=True)


class convert_status(models.Model):
    """device相关convert status"""
    models.AutoField()
    tip_no = models.CharField(max_length=255, null=True)
    mask_name = models.CharField(max_length=255, null=True)
    lot_id = models.CharField(max_length=255, null=True)
    device_name = models.CharField(max_length=255)
    stage_id = models.IntegerField(null=True)
    stage = models.CharField(max_length=20, null=True)
    location = models.CharField(max_length=255, null=True)
    file_name = models.CharField(max_length=255, null=True)
    # 0:wait 1:o/g(on going) 2:done 3:job fail 4:noclean
    status = models.IntegerField(default=0)
    # 0:release 1:skip 2:hold
    operation_status = models.IntegerField(default=0)
    progress = models.CharField(max_length=255, default='0.00%')
    progress_history = models.TextField(default='0.00%')
    remark = models.CharField(max_length=255)
    operator = models.CharField(default='', max_length=255)
    record_no = models.CharField(default='', max_length=255)
    alta_name = models.CharField(max_length=50, null=True)
    err_message = models.CharField(max_length=1000, null=True)
    jdv_status = models.IntegerField(default=0)

class convert_operate_log(BaseModel):
    """convert status 操作日志"""
    # maskname,devicename,record_no,operator,time,operation,result,params,url
    models.AutoField()
    convert_status_id = models.IntegerField()
    operation = models.CharField(max_length=255)
    operation_time = models.CharField(max_length=255)
    operation_user_id = models.IntegerField(null=True)
    operation_user_name = models.CharField(max_length=255)
    remark = models.CharField(max_length=255)
    # 0:操作成功 1:操作失败
    status = models.IntegerField(default=0)
    result = models.TextField(null=True)
    message = models.TextField(null=True)
    url = models.CharField(default='', max_length=255)
    params = models.CharField(default='', max_length=500)
    code = models.CharField(default='', max_length=255)
    mask_name = models.CharField(default='', max_length=255)
    device_name = models.CharField(default='', max_length=255)
    record_no = models.CharField(default='', max_length=255)
    submit_time = models.DateTimeField(null=True)


class fracture_callback(BaseModel):
    models.AutoField()
    record_no = models.CharField(max_length=255)  # correspond to IEMS instruction_record:record_no
    result_code = models.IntegerField(null=True, default=0)
    result_content = models.TextField(max_length=255)
    callback_date = models.CharField(max_length=20, null=False, default='')
    callback_time = models.IntegerField(default=0, null=False)
    callback_return_status = models.IntegerField(default=0)  # 0donot return anny value ，1has been return value


class record(BaseModel):
    models.AutoField()
    lot_id = models.CharField(max_length=255)
    convert_status_id = models.CharField(max_length=255)
    tip_no = models.CharField(max_length=255)
    mask_name = models.CharField(max_length=255)
    device_name = models.CharField(max_length=255)
    record_no = models.CharField(max_length=255)
    param = models.CharField(max_length=1000)
    # 0:未提交 1:提交成功 2:提交失敗 3:執行完成 4:執行失敗
    status = models.IntegerField(default=0)
    result = models.TextField()
    message = models.CharField(max_length=255)
    submit_time = models.DateTimeField(null=True)
    callback_time = models.DateTimeField(null=True)
    type = models.CharField(max_length=255)


class deck_para(models.Model):
    id = models.AutoField(primary_key=True)
    node = models.CharField(max_length=10, null=False)
    stage = models.CharField(max_length=50, null=False)
    writer = models.CharField(max_length=50, null=True)
    db_count = models.IntegerField(null=False, default=1)
    function = models.CharField(max_length=50, null=True)
    item = models.CharField(max_length=255, null=False)
    ref1 = models.CharField(max_length=255, null=True)
    ref2 = models.CharField(max_length=255, null=True)
    ref3 = models.CharField(max_length=255, null=True)
    ref4 = models.CharField(max_length=255, null=True)
    value_in = models.CharField(max_length=255, null=True)
    value_out = models.CharField(max_length=255, null=True)


class fracture_deck(models.Model):
    id = models.AutoField(primary_key=True)
    path = models.CharField(max_length=255, null=True)
    file = models.CharField(max_length=50, null=True)
    layer = models.CharField(max_length=255, null=True)
    format = models.CharField(max_length=50, null=True)
    db_count = models.IntegerField(null=False, default=1)
    stage_name = models.CharField(max_length=50, null=True)

class convert_table(models.Model):
    id = models.AutoField(primary_key=True)
    tip_no = models.CharField(max_length=50, null=False)
    mask_name = models.CharField(max_length=50, null=False)
    device_name = models.CharField(max_length=50, null=False)
    stage_list = models.CharField(max_length=255, null=False)
    status = models.CharField(max_length=50, null=True)
    opc_tool = models.CharField(max_length=50, null=True)

class convert_table_time(models.Model):
    id = models.AutoField(primary_key=True)
    convert_table_id = models.IntegerField(null=False)
    stage = models.CharField(max_length=50, null=False)
    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)
    result = models.CharField(max_length=50, null=True)

class alta_naming_table(models.Model):
    id = models.AutoField(primary_key=True)
    submit_date = models.DateTimeField(null=True)
    prod_name = models.CharField(max_length=50, null=False)
    prod_serial = models.CharField(max_length=50, null=False)
    device_name = models.CharField(max_length=50, null=False)
    device_serial = models.CharField(max_length=50, null=False)
    layer = models.CharField(max_length=50, null=False)
    version = models.CharField(max_length=50, null=False)
    version_serial = models.CharField(max_length=50, null=True)
    alta_name = models.CharField(max_length=50, null=False)
    tip_no = models.CharField(max_length=50, null=True)
    mask_name = models.CharField(max_length=50, null=True)