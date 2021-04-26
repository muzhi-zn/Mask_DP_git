from django.db import models


# Create your models here.
class iems_execute_result(models.Model):
    id = models.AutoField
    record_no = models.CharField(max_length=255)
    result_log_file_path = models.CharField(max_length=255, null=True)
    execute_start_time = models.DateTimeField(null=True)
    execute_end_time = models.DateTimeField(null=True)
    # 1 正在执行 2 提交执行失败 3 执行完成（成功） 4 执行完成（失败）
    status = models.IntegerField()
    execute_result = models.TextField(null=True)
    process_result = models.CharField(max_length=255, default='', null=True)
    job_id = models.CharField(max_length=255)
    err_message = models.TextField(default='')  # 失败原因
