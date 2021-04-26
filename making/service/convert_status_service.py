from making.models import convert_status, convert_operate_log
from utilslibrary.base.base import BaseService
from utilslibrary.system_constant import Constant
from utilslibrary.utils.date_utils import getDateStr


class convertStatusService(BaseService):
    """convert_status相关方法"""
    def add_convert_status(self, c_s):
        """新增convert_status记录"""

        pass


class stageService(BaseService):
    """站点操作service"""

    def rework_mode1(self, convert_status_id, stage_name):
        """重新产生文件，但是不执行"""
        if stage_name == "Fracture":
            c_s = convert_status.objects.get(pk=convert_status_id)
            tip_no = c_s.tip_no
            """执行生成文件的方法"""
            pass

    def rework_mode2(self, convert_status_id, stage_name):
        """不重新产生文件，但是执行"""
        if stage_name == "Fracture":
            c_s = convert_status.objects.get(pk=id)
            tip_no = c_s.tip_no

            pass

    def rework_mode3(self, convert_status_id, stage_name):
        """重新产生文件，重新执行"""
        if stage_name == "Fracture":
            c_s = convert_status.objects.get(pk=id)
            tip_no = c_s.tip_no

            pass


class convertStatusLog(BaseService):
    """保存log日志"""
    def add_operation_log(self, convert_status_id, operation, user_id, user_name,
                          result, message, url, params, code, mask_name, device_name,
                          record_no, submit_time):
        """新增操作日志"""
        # maskname,devicename,record_no,operator,time,operation,result,params,url
        log = convert_operate_log()
        log.operation_time = getDateStr()
        log.operation_user_id = user_id
        log.operation_user_name = user_name
        log.convert_status_id = convert_status_id
        log.result = result
        log.message = message
        log.url = url
        log.params = params
        log.code = code
        log.mask_name = mask_name
        log.device_name = device_name
        log.record_no = record_no
        log.submit_time = submit_time
        if operation == Constant.CONVERT_OPERATION_RELEASE:
            log.operation = 'release'
        elif operation == Constant.CONVERT_OPERATION_SKIP:
            log.operation = 'skip'
        elif operation == Constant.CONVERT_OPERATION_HOLD:
            log.operation = 'hold'
        elif operation == Constant.CONVERT_OPERATION_REDECK:
            log.operation = 're deck'
        elif operation == Constant.CONVERT_OPERATION_REDO:
            log.operation = 're do'
        elif operation == Constant.CONVERT_OPERATION_REDECKANDDO:
            log.operation = 're deck&do'
        elif operation == Constant.CONVERT_OPERATION_AUTO_DECKANDDO:
            log.operation = 'auto deck&do'
        log.save()

    def add_rework_log(self, convert_status_id, rework, user_id, user_name):
        """新增操作日志"""
        log = convert_operate_log()
        log.convert_status_id = convert_status_id
        log.operation_time = getDateStr()
        log.operation_user_id = user_id
        log.operation_user_name = user_name
        if rework == 1:
            log.operation = 'rework mode1'
        elif rework == 2:
            log.operation = 'rework mode2'
        elif rework == 3:
            log.operation = 'rework mode3'
        log.save()
