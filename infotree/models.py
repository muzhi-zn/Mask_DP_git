from django.db import models

# Create your models here.

from django.db import models
from utilslibrary.base.base import BaseModel


class released_info(BaseModel):
    id = models.AutoField(primary_key=True)
    group = models.IntegerField(default=0)
    tool = models.CharField(max_length=256, null=True)
    node = models.CharField(max_length=256, null=True)
    tone = models.CharField(max_length=256, null=True)
    blank = models.CharField(max_length=256, null=True)
    grade = models.CharField(max_length=256, null=True)
    pattern_density = models.CharField(max_length=256, null=True)
    layer = models.CharField(max_length=256, null=True)
    type = models.CharField(max_length=256, null=True)
    cs_command = models.CharField(max_length=256, null=True)
    value = models.CharField(max_length=256, null=True)
    version = models.IntegerField(default=0)
    cd_map_id = models.IntegerField(default=0)
    cec_id = models.IntegerField(default=0)
    status = models.IntegerField(default=0)
    lock = models.IntegerField(default=0)
    customer = models.CharField(max_length=256, null=True)


class released_info_alta(BaseModel):
    id = models.AutoField(primary_key=True)
    group = models.IntegerField(default=0)
    tool = models.CharField(max_length=256, null=True)
    node = models.CharField(max_length=256, null=True)
    tone = models.CharField(max_length=256, null=True)
    blank = models.CharField(max_length=256, null=True)
    grade = models.CharField(max_length=256, null=True)
    pattern_density = models.CharField(max_length=256, null=True)
    layer = models.CharField(max_length=256, null=True)
    level = models.IntegerField(default=0)
    type = models.CharField(max_length=256, null=True)
    item = models.CharField(max_length=256, null=True)
    value = models.CharField(max_length=256, null=True)
    version = models.IntegerField(default=0)
    status = models.IntegerField(default=0)
    lock = models.IntegerField(default=0)
    customer = models.CharField(max_length=256, null=True)


class unreleased_info(BaseModel):
    id = models.AutoField(primary_key=True)
    group = models.IntegerField(default=0)
    tool = models.CharField(max_length=256, null=True)
    node = models.CharField(max_length=256, null=True)
    tone = models.CharField(max_length=256, null=True)
    blank = models.CharField(max_length=256, null=True)
    grade = models.CharField(max_length=256, null=True)
    pattern_density = models.CharField(max_length=256, null=True)
    layer = models.CharField(max_length=256, null=True)
    type = models.CharField(max_length=256, null=True)
    cs_command = models.CharField(max_length=256, null=True)
    value = models.CharField(max_length=256, null=True)
    limit_type = models.IntegerField(default=0)
    limit = models.CharField(max_length=256, null=True)
    version = models.IntegerField(default=0)
    cd_map_id = models.IntegerField(default=0)
    cec_id = models.IntegerField(default=0)
    # 1:add 2:edit 3:copy 4:import 5:delete
    status = models.IntegerField(default=0)
    lock = models.IntegerField(default=0)
    release = models.CharField(max_length=256, null=True)
    customer = models.CharField(max_length=256, null=True)


class info_tree_data_import_temp(BaseModel):
    id = models.AutoField(primary_key=True)
    group = models.IntegerField(default=0)
    tool = models.CharField(max_length=256, null=True)
    node = models.CharField(max_length=256, null=True)
    tone = models.CharField(max_length=256, null=True)
    blank = models.CharField(max_length=256, null=True)
    grade = models.CharField(max_length=256, null=True)
    pattern_density = models.CharField(max_length=256, null=True)
    layer = models.CharField(max_length=256, null=True)
    level = models.IntegerField(default=0)
    type = models.CharField(max_length=256, null=True)
    cs_command = models.CharField(max_length=256, null=True)
    value = models.CharField(max_length=256, null=True)
    limit_type = models.IntegerField(default=0)
    limit = models.CharField(max_length=256, null=True)
    customer = models.CharField(max_length=256, null=True)


class info_tree_data_export_log(BaseModel):
    id = models.AutoField(primary_key=True)
    tool = models.CharField(max_length=256, null=True)
    node = models.CharField(max_length=256, null=True)
    tone = models.CharField(max_length=256, null=True)
    blank = models.CharField(max_length=256, null=True)
    grade = models.CharField(max_length=256, null=True)
    pattern_density = models.CharField(max_length=256, null=True)
    layer = models.CharField(max_length=256, null=True)
    file_name = models.CharField(max_length=256, null=True)
    file_path = models.CharField(max_length=256, null=True)


class unreleased_mdt(BaseModel):
    id = models.AutoField(primary_key=True)
    # type 1: unreleased 2:unreleased_alta
    type = models.IntegerField(default=0)
    # lock 0:unlock 1:lock
    lock = models.IntegerField(default=0)
    unreleased_id = models.IntegerField(default=0)
    cad_layer = models.CharField(max_length=256, null=True)
    data_type = models.CharField(max_length=256, null=True)
    writer_mdt = models.CharField(max_length=256, null=True)
    writer_dose = models.CharField(max_length=256, null=True)


class released_mdt(BaseModel):
    id = models.AutoField(primary_key=True)
    # type 1: unreleased 2:unreleased_alta
    type = models.IntegerField(default=0)
    # lock 0:unlock 1:lock
    lock = models.IntegerField(default=0)
    released_id = models.IntegerField(default=0)
    cad_layer = models.CharField(max_length=256, null=True)
    data_type = models.CharField(max_length=256, null=True)
    writer_mdt = models.CharField(max_length=256, null=True)
    writer_dose = models.CharField(max_length=256, null=True)
    version = models.IntegerField(default=0)


class unreleased_info_alta(BaseModel):
    id = models.AutoField(primary_key=True)
    group = models.IntegerField(default=0)
    tool = models.CharField(max_length=256, null=True)
    node = models.CharField(max_length=256, null=True)
    tone = models.CharField(max_length=256, null=True)
    blank = models.CharField(max_length=256, null=True)
    grade = models.CharField(max_length=256, null=True)
    pattern_density = models.CharField(max_length=256, null=True)
    layer = models.CharField(max_length=256, null=True)
    level = models.IntegerField(default=0)
    type = models.CharField(max_length=256, null=True)
    item = models.CharField(max_length=256, null=True)
    value = models.CharField(max_length=256, null=True)
    limit_type = models.IntegerField(default=0)
    limit = models.CharField(max_length=256, null=True)
    version = models.IntegerField(default=0)
    # 1:add 2:edit 3:copy 4:import 5:delete
    status = models.IntegerField(default=0)
    lock = models.IntegerField(default=0)
    customer = models.CharField(max_length=256, null=True)


class group_create(models.Model):
    id = models.AutoField(primary_key=True)


class info_tree_data_version_list(BaseModel):
    id = models.AutoField(primary_key=True)
    group = models.IntegerField(default=0)


class release_check(BaseModel):
    id = models.AutoField(primary_key=True)
    group = models.IntegerField(default=0)
    tool = models.CharField(max_length=256, null=True)
    node = models.CharField(max_length=256, null=True)
    tone = models.CharField(max_length=256, null=True)
    blank = models.CharField(max_length=256, null=True)
    grade = models.CharField(max_length=256, null=True)
    pattern_density = models.CharField(max_length=256, null=True)
    layer = models.CharField(max_length=256, null=True)
    level = models.IntegerField(default=0)
    version = models.IntegerField(default=0)
    check_user_id = models.IntegerField(default=0)
    check_user_name = models.CharField(max_length=256, null=True)
    check_status = models.IntegerField(default=0)
    check_time = models.CharField(max_length=256, null=True)
    create_user = models.CharField(max_length=256, null=True)
    description = models.TextField(null=True)
    customer = models.CharField(max_length=256, null=True)


class maintain_table(BaseModel):
    id = models.AutoField(primary_key=True)
    tool = models.CharField(max_length=256, null=True)
    customer = models.CharField(max_length=256, null=True)
    node = models.CharField(max_length=256, null=True)
    tone = models.CharField(max_length=256, null=True)
    blank = models.CharField(max_length=256, null=True)
    grade = models.CharField(max_length=256, null=True)
    pattern_density = models.CharField(max_length=256, null=True)
    layer = models.CharField(max_length=256, null=True)
    mdt = models.CharField(max_length=256, null=True, default='N')
    remark = models.CharField(max_length=512, null=True)


class maintain_table_mdt(BaseModel):
    id = models.AutoField(primary_key=True)
    maintain_table_id = models.IntegerField(default=0)
    cad_layer = models.CharField(max_length=256, null=True)
    data_type = models.CharField(max_length=256, null=True)
    writer_mdt = models.CharField(max_length=256, null=True)
    writer_dose = models.CharField(max_length=256, null=True)


class info_tree_template(BaseModel):
    id = models.AutoField(primary_key=True)
    machine_type = models.CharField(max_length=256, null=True)
    level = models.IntegerField(default=0)
    type = models.CharField(max_length=256, null=True)
    cs_command = models.CharField(max_length=256, null=True)
    data_type = models.CharField(max_length=256, null=True)
    # limit_type, 0:不限制 1:字典 2:範圍
    limit_type = models.IntegerField(default=0)
    limit = models.CharField(max_length=256, null=True)


class info_tree_template_option(BaseModel):
    id = models.AutoField(primary_key=True)
    temp_id = models.IntegerField(default=0)
    sort = models.IntegerField(default=0)
    option = models.CharField(max_length=256, null=True)
    start = models.FloatField(null=True)
    end = models.FloatField(null=True)
    remark = models.CharField(max_length=256, null=True)


class tree(BaseModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, null=True)
    description = models.CharField(max_length=256, null=True)


class tree_option(BaseModel):
    id = models.AutoField(primary_key=True)
    tree_id = models.IntegerField(default=0)
    sort = models.IntegerField(default=0)
    value = models.CharField(max_length=256, null=True)


class cd_map(BaseModel):
    id = models.AutoField(primary_key=True)
    folder_name = models.CharField(max_length=32, null=True)
    cd_map_dat_name = models.CharField(max_length=512, null=True)
    index_prm_name = models.CharField(max_length=512, null=True)
    path = models.CharField(max_length=1024, null=True)
    create_name = models.CharField(max_length=128, null=True)


class cec(BaseModel):
    id = models.AutoField(primary_key=True)
    folder_name = models.CharField(max_length=32, null=True)
    cec_name = models.CharField(max_length=512, null=True)
    cec_path = models.CharField(max_length=1024, null=True)
    create_name = models.CharField(max_length=128, null=True)
