# _*_ coding: utf-8 _*_
# from Mask_DP.settings import MEDIA_ROOT, CALIBREWB_ENV, CALIBREWB_SSH_IP, CALIBREWB_SSH_USR, CALIBREWB_SSH_PASSWD
import os
import logging

from tooling_form.models import product_info, device_info
from utilslibrary.system_constant import Constant

log = logging.getLogger('log')


# def create_folder(tip_no):
#     '''创建文件夹'''
#     if CALIBREWB_ENV == 'local':
#         return local_create_folder(tip_no)
#     else:
#         return ssh_create_folder(tip_no)


def local_create_folder(tip_no):  # Product/Product值/Device/device_list/DB and layer
    """创建本地文件夹"""
    try:
        tip_no_folder = Constant.TEMPLATE_FILE_GENERATE_PATH
        product = product_info.objects.get(tip_no=tip_no, is_delete=0).product
        product_folder = os.path.join(tip_no_folder, product)
        device_folder = os.path.join(product_folder, 'Device')
        jdv_folder = os.path.join(product_folder, 'JDV')
        os.makedirs(jdv_folder, exist_ok=True)
        device_list = device_info.objects.values("device_name").filter(tip_no=tip_no, is_delete=0).distinct()
        for device in device_list:
            device_name_folder = os.path.join(device_folder, device['device_name'])
            db_folder = os.path.join(device_name_folder, Constant.FILE_PATH_DB)
            os.makedirs(db_folder, exist_ok=True)
            layer_folder = os.path.join(device_name_folder, Constant.FILE_PATH_LAYER)
            os.makedirs(layer_folder, exist_ok=True)
        os.system('chmod -R 777 ' + product_folder)
        return True
    except Exception as e:
        log.error("tip_no=%s的请求创建本地文件夹出错，错误信息为" + str(e))
        return False


# def ssh_create_folder(tip_no):
#     '''创建远程服务器上的文件夹'''
#     try:
#         ssh = SSHManager(CALIBREWB_SSH_IP, CALIBREWB_SSH_USR, CALIBREWB_SSH_PASSWD)
#         tip_no_folder = Constant.TEMPLATE_FILE_GENERATE_PATH
#         product = import_data.objects.get(tip_no=tip_no, sheet_name='Product_Info', column_name='Product').import_data
#         product_folder = tip_no_folder + '/' + product
#         device_folder = product_folder + '/' + 'Device'
#         jdv_folder = product_folder + '/' + 'JDV'
#         ssh.ssh_exec_cmd('mkdir -p -m 777 ' + jdv_folder)
#         device_list = import_data.objects.filter(tip_no=tip_no, sheet_name=Constant.TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO
#                                                  , column_name=Constant
#                                                  .TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO_DEVICE_NAME) \
#             .values('import_data')
#         for device in device_list:
#             device_name_folder = device_folder + '/' + device['import_data']
#             db_folder = device_name_folder + '/' + Constant.FILE_PATH_DB
#             print(db_folder)
#             ssh.ssh_exec_cmd('mkdir -p -m 777 ' + db_folder)
#             layer_folder = device_name_folder + '/' + Constant.FILE_PATH_LAYER
#             print(layer_folder)
#             ssh.ssh_exec_cmd('mkdir -p -m 777 ' + layer_folder)
#         return True
#     except Exception as e:
#         log.error("tip_no=%s的请求创建远程文件夹出错，错误信息为" + e)
#         return False
