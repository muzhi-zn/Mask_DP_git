from django.db import models
from utilslibrary.base.base import BaseModel


# Create your models here.
class lot_info(BaseModel):
    models.AutoField
    tip_no = models.CharField(max_length=255)
    product_name = models.CharField(max_length=255, null=True)
    customer = models.CharField(max_length=255, null=True)
    rule = models.CharField(max_length=255, null=True)
    grade = models.CharField(max_length=10, null=True)
    type = models.CharField(max_length=10, null=True)
    tone = models.CharField(max_length=10, null=True)
    clip = models.CharField(max_length=10, null=True)
    mes_step = models.CharField(max_length=100, null=True)
    mes_status = models.CharField(max_length=20, null=True)
    exp_tool_id = models.IntegerField(null=True)
    machine_id = models.IntegerField(null=True)
    exp_tool = models.CharField(max_length=100, null=True)
    blank_code = models.CharField(max_length=100, null=True)
    pellicle_code = models.CharField(max_length=100, null=True)
    wavelength = models.CharField(max_length=20, null=True)
    # 0/no 1/yes
    dispatch_flag = models.IntegerField(default=0)
    release_status = models.IntegerField(default=0)
    compile_status = models.IntegerField(default=0)
    lot_id = models.CharField(max_length=255)
    mask_name = models.CharField(max_length=255)
    lot_owner_id = models.CharField(max_length=255)
    lot_owner_name = models.CharField(max_length=255)
    ready_date = models.DateTimeField(null=True)
    expire_date = models.DateTimeField(null=True)
    # 0:默认 1:提交生成lot_id请求成功 2:提交失败 3:task获取lot成功
    status = models.IntegerField(default=0)
    status_dec = models.CharField(max_length=255)
    ##convert status: 0:默认状态，未生成脚本 10：已提交生成脚本，11：脚本生成失败 12：脚本生成成功，未fracture,
    # 20:已提交fracture 21:fracutre 失败 22:fracture 成功
    # 30:XOR已提交 31：xor失败 32:xor成功
    convert_status = models.IntegerField(default=0)
    convert_status_dec = models.CharField(max_length=255, null=True)
    result = models.CharField(max_length=255, null=True)
    payment_status = models.IntegerField(default=0)
    payment_user_id = models.CharField(max_length=255)
    payment_user_name = models.CharField(max_length=255)
    payment_check_date = models.DateTimeField(null=True)
    # mes相关参数
    mes_lot_type = models.CharField(max_length=255, null=True)
    mes_lot_status = models.CharField(max_length=255, null=True)
    mes_lot_state = models.CharField(max_length=255, null=True)
    mes_lot_production_state = models.CharField(max_length=255, null=True)
    mes_lot_hold_state = models.CharField(max_length=255, null=True)
    mes_lot_finished_state = models.CharField(max_length=255, null=True)
    mes_lot_process_state = models.CharField(max_length=255, null=True)
    mes_lot_inventory_state = models.CharField(max_length=255, null=True)
    mes_bank_id = models.CharField(max_length=255, null=True)
    mes_order_number = models.CharField(max_length=255, null=True)
    mes_customer_code = models.CharField(max_length=255, null=True)
    mes_product_id = models.CharField(max_length=255, null=True)
    mes_last_claimed_timestamp = models.CharField(max_length=255, null=True)
    mes_due_timestamp = models.CharField(max_length=255, null=True)
    mes_route_id = models.CharField(max_length=255, null=True)
    mes_operation_number = models.CharField(max_length=255, null=True)
    mes_total_wafer_count = models.IntegerField(null=True)
    mes_bank_in_required_flag = models.BooleanField(null=True)
    mes_control_use_state = models.CharField(max_length=255, null=True)
    mes_used_count = models.IntegerField(null=True)
    mes_completion_timestamp = models.CharField(max_length=255, null=True)
    mes_lot_family_id = models.CharField(max_length=255, null=True)
    mes_product_request_id = models.CharField(max_length=255, null=True)
    mes_sub_lot_type = models.CharField(max_length=255, null=True)
    mes_lot_owner_id = models.CharField(max_length=255, null=True)
    mes_required_cassette_category = models.CharField(max_length=255, null=True)
    mes_backup_processing_flag = models.BooleanField(null=True)
    mes_current_location_flag = models.BooleanField(null=True)
    mes_transfer_flag = models.BooleanField(null=True)
    mes_carrier_id = models.CharField(max_length=255, null=True)
    mes_equipment_id = models.CharField(max_length=255, null=True)
    mes_hold_reason_code_id = models.CharField(max_length=255, null=True)
    mes_sorter_job_exist_flag = models.BooleanField(null=True)
    mes_in_post_process_flag_of_cassette = models.BooleanField(null=True)
    mes_in_post_process_flag_of_lot = models.BooleanField(null=True)
    mes_inter_fab_xfer_state = models.CharField(max_length=255, null=True)
    mes_bonding_group_id = models.CharField(max_length=255, null=True)
    mes_auto_dispatch_controller_flag = models.BooleanField(null=True)
    mes_eqp_monitor_job_id = models.CharField(max_length=255, null=True)
    mes_operation_id = models.CharField(max_length=255, null=True)
    mes_pd_type = models.CharField(max_length=255, null=True)
    mes_schedule_mode = models.CharField(max_length=255, null=True)
    mes_plan_start_timestamp = models.CharField(max_length=255, null=True)
    mes_priority_class = models.IntegerField(null=True)
    mes_lot_info_change_flag = models.BooleanField(null=True)
    mes_get_wip_message = models.CharField(max_length=255, null=True)
    mes_get_wip_result = models.TextField(null=True)
    info_tree_tool_id = models.CharField(max_length=255, null=True)
    writer_create_file_status = models.IntegerField(default=0)
    writer_create_file_error_message = models.TextField(null=True)
    ftp_upload_status = models.IntegerField(default=0)
    ftp_upload_error_message = models.TextField(null=True)
    catalog_status = models.IntegerField(default=0, null=False)
    catalog_error_message = models.TextField(null=True)
    register_status = models.IntegerField(default=0, null=False)
    register_error_message = models.TextField(null=True)
    register_del_status = models.IntegerField(default=0, null=False)
    register_del_error_message = models.TextField(null=True)
    change_status = models.IntegerField(default=0, null=False)
    change_error_message = models.TextField(null=True)
    writer_op_status = models.IntegerField(default=0, null=False)
    writer_op_error_message = models.TextField(null=True)
    move_back_status = models.IntegerField(default=0, null=False)
    move_back_error_message = models.TextField(null=True)
    sap_dwerk = models.CharField(max_length=255, null=True)
    sap_charg = models.CharField(max_length=255, null=True)
    sap_aufnr = models.CharField(max_length=255, null=True)
    sap_auart = models.CharField(max_length=255, null=True)
    sap_kdauf = models.CharField(max_length=255, null=True)
    sap_kdpos = models.CharField(max_length=255, null=True)
    sap_matnr = models.CharField(max_length=255, null=True)
    sap_notice_status = models.IntegerField(null=True)


class lot_op_record(models.Model):
    """lot进行op_start、op_start_cancel、op_com操作的记录"""
    models.AutoField
    lot_id = models.CharField(max_length=255)
    equipment_id = models.CharField(max_length=255, null=True)
    dp_operation = models.CharField(max_length=255, null=True)
    mes_operation = models.CharField(max_length=255, null=True)
    control_job_id = models.CharField(max_length=255, null=True)
    # 1 opstart 2 opcom 3 opstartcancel
    op_operation_type = models.IntegerField(default=0)
    op_operation = models.CharField(max_length=255, null=True)
    # 0 未调用成功 1 调用成功
    op_operation_status = models.IntegerField(default=0)
    mes_transaction_id = models.CharField(max_length=255, null=True)
    op_operation_message = models.CharField(max_length=255, null=True)
    op_operationt_date = models.CharField(max_length=255, null=True)


class lot_status(models.Model):
    """lot 信息"""
    models.AutoField
    product_name = models.CharField(max_length=255)  # 产品名称
    tip_no = models.CharField(max_length=20)  # TipNo
    lot_id = models.CharField(max_length=255)  # lotId
    lot_name = models.CharField(max_length=255)
    lot_owner_id = models.IntegerField()
    lot_owner_name = models.CharField(max_length=255)
    lot_id_create_date = models.DateTimeField()
    lot_status = models.IntegerField(default=0)
    lot_now_stage = models.CharField(max_length=255)
    lot_trail = models.CharField(max_length=255)
    lot_ready_date = models.DateTimeField()
    lot_expire_date = models.DateTimeField()


class lot_trail(BaseModel):
    """lot 轨迹列表"""
    models.AutoField
    tip_no = models.CharField(max_length=20, null=True)
    lot_id = models.CharField(max_length=32)  # lot ID
    stage = models.CharField(max_length=255)  # 阶段
    stage_status = models.IntegerField(default=0)  # 阶段状态
    # 0：默认，无错，在界面不可删除该记录; 1:为处理出错记录，可在界面删除
    is_error = models.IntegerField(default=0)  # 是否处理出错
    stage_desc = models.CharField(max_length=1024)  # 阶段信息描述
    stage_start_date = models.DateTimeField()  # 阶段开始时间
    stage_end_date = models.DateTimeField()  # 阶段结束时间
    operator_id = models.IntegerField()  # 操作人id
    operator_name = models.CharField(max_length=255)  # 操作人名称
    operate_date = models.DateTimeField()  # 操作时间
    remark = models.CharField(max_length=255)  # 备注信息


class email_group(models.Model):
    """email组视图"""
    office_id = models.IntegerField(default=0)
    office_name = models.CharField(max_length=255)
    user_id = models.IntegerField(primary_key=True)
    user_loginname = models.CharField(max_length=255)
    email = models.CharField(max_length=255)

    class Meta:
        db_table = 'email_group'
        managed = False


class mes_blank_code(BaseModel):
    '''mes_blankcode查询条件表'''
    models.AutoField
    seq = models.IntegerField()
    customer = models.CharField(max_length=255)
    design_rule = models.CharField(max_length=255)
    grade_from = models.CharField(max_length=255, null=True)
    grade_to = models.CharField(max_length=255, null=True)
    layer_name = models.CharField(max_length=255)
    mask_type = models.CharField(max_length=255)
    tone = models.CharField(max_length=255)
    wave_lenght = models.CharField(max_length=255)
    blank_code = models.CharField(default='', max_length=255, null=False)
    part_no = models.CharField(default='', max_length=255, null=False)
    blank = models.CharField(default='', max_length=255, null=False)


class mes_operation_info(models.Model):
    """mes站点相关信息"""
    models.AutoField
    seq_no = models.IntegerField()
    route_id = models.CharField(max_length=255, null=True)
    operation_id = models.CharField(max_length=255, null=True)
    operation_number = models.CharField(max_length=255, null=True)
    pdType = models.CharField(max_length=255, null=True)
    stage_id = models.CharField(max_length=255, null=True)
    stage_group_id = models.CharField(max_length=255, null=True)
    machines = models.CharField(max_length=255, null=True)
