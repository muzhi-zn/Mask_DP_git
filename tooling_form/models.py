# coding:utf-8
from django.db import models
from utilslibrary.base.base import BaseModel


class tip_no_create(BaseModel):
    models.AutoField
    tip_no = models.CharField(max_length=255)


class product_info(BaseModel):
    models.AutoField
    tip_no = models.CharField(max_length=255)
    customer = models.CharField(max_length=255)
    fab = models.CharField(max_length=255)
    product = models.CharField(max_length=255)
    layout_type_application_type = models.CharField(max_length=255)
    mask_size = models.CharField(max_length=255)
    design_rule = models.CharField(max_length=255)
    mask_vendor = models.CharField(max_length=255)
    product_type = models.CharField(max_length=255)
    d_h = models.CharField(max_length=255)
    payment = models.CharField(max_length=255)
    tooling_version = models.CharField(max_length=255)
    delivery_fab = models.CharField(max_length=255)
    order_type = models.CharField(max_length=255)
    priority = models.CharField(max_length=255)
    security_type = models.CharField(max_length=255)
    tech_process = models.CharField(max_length=255)
    cr_border_extend = models.CharField(max_length=255, null=True)


class tapeout_info(BaseModel):
    models.AutoField
    tip_no = models.CharField(max_length=255)
    no = models.IntegerField(null=True)
    t_o = models.CharField(max_length=255)
    layer_name = models.CharField(max_length=255)
    version = models.CharField(max_length=255, default='')
    mask_name = models.CharField(max_length=255, default="")
    grade = models.CharField(max_length=255)
    mask_mag = models.CharField(max_length=255)
    mask_type = models.CharField(max_length=255)
    alignment = models.CharField(max_length=255)
    pellicle = models.CharField(max_length=255)
    light_sourse = models.CharField(max_length=255)
    rotation = models.CharField(max_length=255)
    barcode = models.CharField(max_length=255)
    inspection = models.CharField(max_length=255)
    # 0 没有执行过done 1 已经执行过done
    is_done = models.IntegerField(default=0)
    # 0 不需要重跑 1 需要重跑
    need_redo = models.IntegerField(default=0)


class device_info(BaseModel):
    models.AutoField
    tip_no = models.CharField(max_length=255)
    psm = models.CharField(max_length=255)
    source_db = models.CharField(max_length=255)
    device_type = models.CharField(max_length=255)
    device_name = models.CharField(max_length=255)
    boolean_index = models.CharField(max_length=255)
    bias_sequence = models.CharField(max_length=255)
    rotate = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255)
    top_structure = models.CharField(max_length=255)
    source_mag = models.CharField(max_length=255)
    shrink = models.CharField(max_length=255)
    lb_x = models.CharField(max_length=255)
    lb_y = models.CharField(max_length=255)
    rt_x = models.CharField(max_length=255)
    rt_y = models.CharField(max_length=255)
    check_method = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    file_size = models.BigIntegerField(default=0)
    mask_name = models.CharField(max_length=255, default="")


class ccd_table(BaseModel):
    models.AutoField
    no = models.CharField(max_length=10)
    tip_no = models.CharField(max_length=255)
    mask_name = models.CharField(max_length=255, default="")
    type = models.CharField(max_length=255)
    coor_x = models.CharField(max_length=255)
    coor_y = models.CharField(max_length=255)
    item = models.CharField(max_length=255)
    tone = models.CharField(max_length=255)
    direction = models.CharField(max_length=255)
    cd_4x_nm = models.CharField(max_length=255)



class boolean_info(BaseModel):
    models.AutoField
    tip_no = models.CharField(max_length=255)
    boolean_index = models.CharField(max_length=255)
    source_db = models.CharField(max_length=255)
    mask_name = models.CharField(max_length=255, default="")
    grid = models.CharField(max_length=255)
    operation = models.CharField(max_length=255)
    total_bias = models.CharField(max_length=255)
    tone = models.CharField(max_length=255)


class layout_info(BaseModel):
    models.AutoField
    tip_no = models.CharField(max_length=255)
    mask_name = models.CharField(max_length=255, default="")
    psm = models.CharField(max_length=255)
    device_name = models.CharField(max_length=255)
    mask_mag = models.CharField(max_length=255)
    source_mag = models.CharField(max_length=255)
    original = models.CharField(max_length=255)
    x1 = models.CharField(max_length=255)
    y1 = models.CharField(max_length=255)
    pitch_x = models.CharField(max_length=255)
    pitch_y = models.CharField(max_length=255)
    array_x = models.CharField(max_length=255)
    array_y = models.CharField(max_length=255)


class mlm_info(BaseModel):
    models.AutoField
    tip_no = models.CharField(max_length=255)
    mlm_mask_id = models.CharField(max_length=255)
    mask_name = models.CharField(max_length=255, default="")
    field_name = models.CharField(max_length=255)
    shift_x = models.CharField(max_length=255)
    shift_y = models.CharField(max_length=255)


class file_analysis_info(BaseModel):
    models.AutoField
    tip_no = models.CharField(max_length=9)
    device_name = models.CharField(max_length=255)
    file_name = models.CharField(max_length=500)
    upload_status = models.IntegerField(default=0)
    file_md5 = models.CharField(max_length=32)
    md5_check_status = models.IntegerField(default=0)
    file_sha512 = models.CharField(max_length=255, default='')
    sha512_check_status = models.IntegerField(default=0)
    file_size = models.BigIntegerField(default=0)
    size_check_status = models.IntegerField(default=0)
    iems_record_no = models.CharField(max_length=20, null=True, blank=True)
    analysis_status = models.IntegerField(default=0)
    analysis_message = models.CharField(max_length=255, null=True, blank=True)
    result_file_name = models.CharField(max_length=500)
    result = models.CharField(max_length=500)
    precision = models.CharField(max_length=255)
    precision_check_status = models.IntegerField(default=0)
    topcell = models.CharField(max_length=255)
    topcell_check_status = models.IntegerField(default=0)
    layers = models.CharField(max_length=255)
    layers_check_status = models.IntegerField(default=0)
    bbox = models.CharField(max_length=255)
    bbox_check_status = models.IntegerField(default=0)
    analysis_check_status = models.IntegerField(default=0)


class upload_error_msg(BaseModel):
    id = models.AutoField(primary_key=True)
    set_id = models.IntegerField(default=0)
    message = models.CharField(max_length=255)
    remark = models.CharField(max_length=255)


# 临时表
class product_info_temp(BaseModel):
    models.AutoField
    tip_no = models.CharField(max_length=255, default="")
    import_id = models.IntegerField(default=0)
    customer = models.CharField(max_length=255)
    fab = models.CharField(max_length=255)
    product = models.CharField(max_length=255)
    layout_type_application_type = models.CharField(max_length=255)
    mask_size = models.CharField(max_length=255)
    design_rule = models.CharField(max_length=255)
    mask_vendor = models.CharField(max_length=255)
    product_type = models.CharField(max_length=255)
    d_h = models.CharField(max_length=255)
    payment = models.CharField(max_length=255)
    tooling_version = models.CharField(max_length=255)
    delivery_fab = models.CharField(max_length=255)
    order_type = models.CharField(max_length=255)
    priority = models.CharField(max_length=255)
    security_type = models.CharField(max_length=255)
    tech_process = models.CharField(max_length=255)
    cr_border_extend = models.CharField(max_length=255, null=True)
    data_status = models.CharField(max_length=2, default="0")

# 临时表
class tapeout_info_temp(BaseModel):
    models.AutoField
    tip_no = models.CharField(max_length=255, default="")
    import_id = models.IntegerField(default=0)
    t_o = models.CharField(max_length=255)
    layer_name = models.CharField(max_length=255)
    version = models.CharField(max_length=255, default='')
    mask_name = models.CharField(max_length=255, default="")
    grade = models.CharField(max_length=255)
    mask_mag = models.CharField(max_length=255)
    mask_type = models.CharField(max_length=255)
    alignment = models.CharField(max_length=255)
    pellicle = models.CharField(max_length=255)
    light_sourse = models.CharField(max_length=255)
    rotation = models.CharField(max_length=255)
    barcode = models.CharField(max_length=255)
    inspection = models.CharField(max_length=255)
    data_status = models.CharField(max_length=2, default="0")

# 临时表
class device_info_temp(BaseModel):
    models.AutoField
    tip_no = models.CharField(max_length=255, default="")
    import_id = models.IntegerField(default=0)
    psm = models.CharField(max_length=255)
    source_db = models.CharField(max_length=255)
    device_type = models.CharField(max_length=255)
    device_name = models.CharField(max_length=255)
    boolean_index = models.CharField(max_length=255)
    bias_sequence = models.CharField(max_length=255)
    rotate = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255)
    top_structure = models.CharField(max_length=255)
    source_mag = models.CharField(max_length=255)
    shrink = models.CharField(max_length=255)
    lb_x = models.CharField(max_length=255)
    lb_y = models.CharField(max_length=255)
    rt_x = models.CharField(max_length=255)
    rt_y = models.CharField(max_length=255)
    check_method = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    file_size = models.BigIntegerField(default=0)
    data_status = models.CharField(max_length=2, default="0")

# 临时表
class ccd_table_temp(BaseModel):
    models.AutoField
    tip_no = models.CharField(max_length=255, default="")
    no = models.CharField(max_length=10)
    import_id = models.IntegerField(default=0)
    mask_name = models.CharField(max_length=255, default="")
    type = models.CharField(max_length=255)
    coor_x = models.CharField(max_length=255)
    coor_y = models.CharField(max_length=255)
    item = models.CharField(max_length=255)
    tone = models.CharField(max_length=255)
    direction = models.CharField(max_length=255)
    cd_4x_nm = models.CharField(max_length=255)
    data_status = models.CharField(max_length=2, default="0")

# 临时表
class boolean_info_temp(BaseModel):
    models.AutoField
    tip_no = models.CharField(max_length=255, default="")
    import_id = models.IntegerField(default=0)
    boolean_index = models.CharField(max_length=255)
    source_db = models.CharField(max_length=255)
    mask_name = models.CharField(max_length=255, default="")
    grid = models.CharField(max_length=255)
    operation = models.CharField(max_length=255)
    total_bias = models.CharField(max_length=255)
    tone = models.CharField(max_length=255)
    data_status = models.CharField(max_length=2, default="0")

# 临时表
class layout_info_temp(BaseModel):
    models.AutoField
    tip_no = models.CharField(max_length=255, default="")
    import_id = models.IntegerField(default=0)
    mask_name = models.CharField(max_length=255, default="")
    psm = models.CharField(max_length=255)
    device_name = models.CharField(max_length=255)
    mask_mag = models.CharField(max_length=255)
    source_mag = models.CharField(max_length=255)
    original = models.CharField(max_length=255)
    x1 = models.CharField(max_length=255)
    y1 = models.CharField(max_length=255)
    pitch_x = models.CharField(max_length=255)
    pitch_y = models.CharField(max_length=255)
    array_x = models.CharField(max_length=255)
    array_y = models.CharField(max_length=255)
    data_status = models.CharField(max_length=2, default="0")

# 临时表
class mlm_info_temp(BaseModel):
    models.AutoField
    tip_no = models.CharField(max_length=255, default="")
    import_id = models.IntegerField(default=0)
    mlm_mask_id = models.CharField(max_length=255)
    mask_name = models.CharField(max_length=255, default="")
    field_name = models.CharField(max_length=255)
    shift_x = models.CharField(max_length=255)
    shift_y = models.CharField(max_length=255)
    data_status = models.CharField(max_length=2, default="0")


class setting(BaseModel):
    models.AutoField
    sort = models.IntegerField(default=0)
    sheet_no = models.IntegerField(default=0)
    sheet_name = models.CharField(max_length=255)
    column_no = models.IntegerField(default=0)
    column_name = models.CharField(max_length=255)
    required_field = models.IntegerField(default=1)
    row = models.IntegerField(default=0)
    column = models.IntegerField(default=0)
    parent_id = models.IntegerField(default=0)
    regex = models.IntegerField(default=0)
    regex_no = models.IntegerField(default=0)
    enable = models.IntegerField(default="1")


class import_list(BaseModel):
    models.AutoField
    tip_no = models.CharField(max_length=9)
    file_name = models.CharField(max_length=255)
    old_file_name = models.CharField(max_length=255)
    error_status = models.IntegerField(default=0)
    check_status = models.IntegerField(default=0)
    status = models.IntegerField(default=0)
    create_name = models.CharField(max_length=255)


class import_error_list(BaseModel):
    models.AutoField
    import_data_id = models.IntegerField()
    tip_no = models.CharField(max_length=9)
    import_id = models.IntegerField(default=0)
    sheet_name = models.CharField(max_length=255)
    column_name = models.CharField(max_length=255)
    import_data = models.CharField(max_length=255)
    required_field = models.CharField(max_length=255)
    parent_id = models.IntegerField(default=0)
    regex_no = models.IntegerField(default=0)
    error_code = models.CharField(max_length=255)
    error_description = models.CharField(max_length=255)
    error_type = models.CharField(max_length=255)
    validate_value = models.CharField(max_length=255)

class import_check_list(BaseModel):
    models.AutoField
    import_id = models.IntegerField(default=0)
    tip_no = models.CharField(max_length=9)
    product_name = models.CharField(max_length=255)
    mask_name = models.CharField(max_length=255, default="")
    lot_info_id = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    status = models.IntegerField(default=0)
    check_code = models.CharField(max_length=255)
    error_message = models.CharField(max_length=255)
    sheet_name = models.CharField(max_length=255)

# 临时表
class import_data_temp(BaseModel):
    models.AutoField
    tip_no = models.CharField(max_length=255)
    sheet_name = models.CharField(max_length=255)
    column_name = models.CharField(max_length=255)
    import_data = models.CharField(max_length=255)
    import_data_status = models.IntegerField(default="")
    data_key = models.CharField(max_length=255)
