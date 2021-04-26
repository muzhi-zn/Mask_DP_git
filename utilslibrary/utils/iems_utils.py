import json

import requests

# url_89 = 'http://172.16.20.242:8089/api/'
# url_89 = 'http://172.16.20.226:8082/api/'
from system.service.dict_service import GetValueByType
from utilslibrary.system_constant import Constant
url = 'http://172.16.20.231:8089/api/'
# url_local = 'http://192.168.30.3:8001/api/execute_cmd/'

headers = {"Content-type": "application/json"}  # 指定提交的是json


def execute_cmd_url(exec_url, param=None):
    """执行指令"""
    try:
        param_json = json.dumps(param)
        result = requests.post(exec_url, data=param_json)
        return result.json()
    except Exception as e:
        print(e)
        return {"code": 400, "msg": str(e)}


# def execute_cmd(temp_no: str, params=None, result_file_path=None, ftp_info=None):
#     """执行指令"""
#     param_dict = {'temp_no': temp_no}
#     if params:
#         param_dict['params'] = params  # 提交模板参数
#     if result_file_path:
#         param_dict['result_file_path'] = result_file_path  # 结果获取文件
#     if ftp_info:
#         param_dict['ftp_info'] = ftp_info  # 上传文件相关信息
#     param_json = json.dumps(param_dict)
#     result = requests.post(url_89 + 'execute_cmd/', data=param_json, headers=headers)
#     return result.json()


def execute_cmd_wb(temp_no: str, params=None, result_file_path=None, ftp_info=None):
    """执行指令"""
    param_dict = {'temp_no': temp_no}
    if params:
        param_dict['params'] = params  # 提交模板参数
    if result_file_path:
        param_dict['result_file_path'] = result_file_path  # 结果获取文件
    if ftp_info:
        param_dict['ftp_info'] = ftp_info  # 上传文件相关信息
    param_json = json.dumps(param_dict)
    s = requests.session()
    s.keep_alive = False
    result = requests.post(url + 'execute_instruction/', data=param_json, headers=headers)
    return result.json()


def query_result(record_no):
    """查询指令执行结果"""
    param_dict = {'record_no': record_no}
    param_json = json.dumps(param_dict)
    result = requests.post(url + 'query_result/', data=param_json, headers=headers)
    return result.json()

# def kill_lsf_job(record_no):
#     """kill lsf job"""
#     param_dict = {'record_no': record_no}
#     param_json = json.dumps(param_dict)
#     result = requests.post(url_89 + 'kill_lsf_job/', data=param_json)
#     return result.json()


def pause_job(record_no):
    """停止任务"""
    param_dict = {'record_no':record_no}
    param_json = json.dumps(param_dict)
    url = GetValueByType().getValueByLabel(Constant.IEMS_SERVER_EXECUTE_CMD_URL)
    print(param_json)
    result = requests.post(url + 'pause_job/', data=param_json, headers=headers)
    print(result.json())
    return result.json()


if __name__ == "__main__":
    print(execute_cmd_wb("T00002", "/qxic/qxic/MaskData/Product/QEA012/Device/MP002/DB"
                                   "/1023smallmask_final_dummy_SRAFDB.oas"))
