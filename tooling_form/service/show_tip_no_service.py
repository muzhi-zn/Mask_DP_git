# coding:utf-8
import ftplib
import shutil
import time
import traceback
import os

import paramiko

from catalog.models import tool_maintain
from jdv.models import lot_info
from utilslibrary.base.base import BaseService
from django.http.response import JsonResponse
from utilslibrary.proxy.log_db_proxy import ProxyFactory, InvocationHandler
from django.db import transaction
from tooling_form.models import import_list, import_data_temp, product_info, tapeout_info, device_info, boolean_info, \
    layout_info, mlm_info, file_analysis_info, ccd_table, import_error_list, import_check_list
from utilslibrary.utils.ssh_utils import SSHManager
from utilslibrary.system_constant import Constant


class WrongService(BaseService):
    def update_wrong_data(self, request, import_error_message_log):
        data = {}

        try:
            import_error_message_log.save()
            data["success"] = "true"
            data["msg"] = "Success"
        except Exception as e:
            data["success"] = "false"
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)


@ProxyFactory(InvocationHandler)
class ShowTipNoListService(BaseService):
    def del_upload(self, obj):
        # return msg object
        print('aaa')
        data = {}
        data["success"] = False
        data["msg"] = "Failed"
        ids = obj.id
        if not ids:
            data["success"] = False
            data["msg"] = "Failed"
            return JsonResponse(data, safe=False)

        with transaction.atomic():
            id_list = ids.split(",")
            for id in id_list:
                if id:
                    status = import_list.objects.filter(id=id).values('check_status')[0]['check_status']
                    # if int(status) >= 7:
                    #     data["success"] = False
                    #     data["msg"] = "Unable to delete. step 7 has been performed !"
                    #     return JsonResponse(data, safe=False)

            for id in id_list:
                if id:
                    tip_no = import_list.objects.get(id=id).tip_no
                    if tip_no:
                        del_fracture_file(tip_no, False)
                        jdv_lot_info = lot_info.objects.filter(tip_no=tip_no)
                        if jdv_lot_info:
                            jdv_lot_info.delete()
                    # 修改上傳 tooling form 刪除狀態
                    _o = import_list.objects.get(id=id)
                    _o.is_delete = 1
                    _o.save()

                    # 删除errorlist
                    import_error_list.objects.filter(import_id=id).update(is_delete=1)

                    # 删除checklist
                    import_check_list.objects.filter(import_id=id).update(is_delete=1)

                    # 清除上傳的 tooling form 資料
                    _u = import_data_temp.objects.filter(tip_no=_o.tip_no).update(is_delete=1)
                    # _u = import_data_temp.objects.filter(tip_no=_o.tip_no).delete()

                    self.clear_excel_data(_o.tip_no)  # 清除冗余表数据

        data["success"] = True
        data["msg"] = "Success"
        return JsonResponse(data, safe=False)

    def clear_excel_data(self, tip_no):
        """清楚冗余表中tip_no相关数据"""
        product_info.objects.filter(tip_no=tip_no).delete()
        tapeout_info.objects.filter(tip_no=tip_no).delete()
        device_info.objects.filter(tip_no=tip_no).delete()
        ccd_table.objects.filter(tip_no=tip_no).delete()
        boolean_info.objects.filter(tip_no=tip_no).delete()
        layout_info.objects.filter(tip_no=tip_no).delete()
        mlm_info.objects.filter(tip_no=tip_no).delete()
        file_analysis_info.objects.filter(tip_no=tip_no).delete()

    def clear_lot_info_data(self, tip_no):
        lot_info.objects.filter(tip_no=tip_no).delete()


# def del_fracture_file(tip_no):
#     try:
#         lot_info_mask_name_list = lot_info.objects.filter(tip_no=tip_no).values('info_tree_tool_id',
#                                                                                 'mask_name').distinct()
#
#         if lot_info_mask_name_list.count() != 0:
#             for lot_info_mask_name in lot_info_mask_name_list:
#                 tool = lot_info_mask_name['info_tree_tool_id']
#                 machine_folder = Constant.CATALOG_MACHINE_DICT[tool]
#
#                 # 刪除本地文件
#                 local_path = os.path.join(Constant.CATALOG_LOCAL_PATH, lot_info_mask_name['mask_name'])
#                 if os.path.exists(local_path):
#                     shutil.rmtree(local_path)
#
#                 # 刪除服務器文件
#                 server_path = os.path.join(Constant.CATALOG_FTP_SERVER_SSH_PATH + machine_folder,
#                                            lot_info_mask_name['mask_name'])
#
#                 print("local_path =", local_path)
#                 print("server_path =", server_path)
#                 host = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_HOST']
#                 username = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_ACCOUNT']
#                 password = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_PASSWORD']
#
#                 _o = SSHManager(host, username, password)
#                 cmd_del = 'rm -rf ' + server_path
#                 _o.ssh_exec_cmd(cmd_del)
#                 _o.__del__()
#
#         return True, 'success'
#     except Exception as e:
#         traceback.print_exc()
#         print(e)
#         return False, str(e)


# def del_writer_ftp_file(tip_no):
#     try:
#         lot_info_mask_name_list = lot_info.objects.filter(tip_no=tip_no).values('info_tree_tool_id',
#                                                                                 'mask_name').distinct()
#
#         if lot_info_mask_name_list.count() != 0:
#             for lot_info_mask_name in lot_info_mask_name_list:
#                 tool = lot_info_mask_name['info_tree_tool_id']
#                 machine_folder = Constant.CATALOG_MACHINE_DICT[tool]
#
#                 # 刪除服務器文件
#                 server_path = os.path.join(Constant.CATALOG_FTP_SERVER_SSH_PATH + machine_folder,
#                                            lot_info_mask_name['mask_name'])
#
#                 print("server_path =", server_path)
#                 host = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_HOST']
#                 username = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_ACCOUNT']
#                 password = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_PASSWORD']
#
#                 _o = SSHManager(host, username, password)
#                 cmd_del = 'rm -rf ' + server_path
#                 _o.ssh_exec_cmd(cmd_del)
#                 _o.__del__()
#
#         return True, 'success'
#     except Exception as e:
#         traceback.print_exc()
#         print(e)
#         return False, str(e)

# def del_fracture_file(tip_no):
#     try:
#         lot_info_product_name_list = lot_info.objects.filter(tip_no=tip_no).values('info_tree_tool_id',
#                                                                                    'mask_name', 'exp_tool').distinct()
#
#         if lot_info_product_name_list.count() != 0:
#             for lot_info_product_name in lot_info_product_name_list:
#                 tool = lot_info_product_name['info_tree_tool_id']
#                 machine_folder = Constant.CATALOG_MACHINE_DICT[tool]
#
#                 # 刪除本地文件
#                 local_path = os.path.join(Constant.CATALOG_LOCAL_PATH, lot_info_product_name['mask_name'])
#                 if os.path.exists(local_path):
#                     shutil.rmtree(local_path)
#
#                 # 刪除暂存服務器文件
#                 server_path = os.path.join(Constant.CATALOG_FTP_SERVER_SSH_PATH + machine_folder,
#                                            lot_info_product_name['mask_name'])
#
#                 print("local_path =", local_path)
#                 print("server_path =", server_path)
#                 host = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_HOST']
#                 username = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_ACCOUNT']
#                 password = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_PASSWORD']
#
#                 _o = SSHManager(host, username, password)
#                 cmd_del = 'rm -rf ' + server_path
#                 _o.ssh_exec_cmd(cmd_del)
#                 _o.__del__()
#
#                 # 刪除机台服務器文件
#                 _tool_maintain = tool_maintain.objects.get(exptool=lot_info_product_name['exp_tool'])
#                 tool_maintain_path = _tool_maintain.path
#                 # catalog_machine_path = os.path.join(tool_maintain_path, Constant.NEW_CATALOG_MACHINE_DICT[tool]) + '/'
#                 catalog_machine_path = os.path.join(tool_maintain_path, Constant.CATALOG_MACHINE_DICT[tool]) + '/'
#                 print(tool_maintain_path, catalog_machine_path)
#
#                 machine_server_path = os.path.join(catalog_machine_path, lot_info_product_name['mask_name'])
#                 print("machine_server_path =", machine_server_path)
#
#                 host = _tool_maintain.ip
#                 username = _tool_maintain.account
#                 password = _tool_maintain.password
#
#                 _o_2 = SSHManager(host, username, password)
#                 # cmd_del = 'ls -al'
#                 cmd_del = 'rm -rf ' + machine_server_path
#                 print(_o_2.ssh_exec_cmd(cmd_del))
#                 _o_2.__del__()
#
#         return True, 'success'
#     except Exception as e:
#         traceback.print_exc()
#         print(e)
#         return False, str(e)


def del_fracture_file(lot_id, is_redo):
    try:
        lot_info_product_name = lot_info.objects.get(lot_id=lot_id)

        tool = lot_info_product_name.info_tree_tool_id
        machine_folder = Constant.CATALOG_MACHINE_DICT[tool]

        # 刪除本地文件
        local_path = os.path.join(Constant.CATALOG_LOCAL_PATH, lot_info_product_name.mask_name)
        if os.path.exists(local_path) and not is_redo:
            shutil.rmtree(local_path)

        # 刪除暂存服務器文件
        server_path = os.path.join(Constant.CATALOG_FTP_SERVER_SSH_PATH + machine_folder,
                                   lot_info_product_name.mask_name)

        print("local_path =", local_path)
        print("server_path =", server_path)
        host = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_HOST']
        username = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_ACCOUNT']
        password = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_PASSWORD']
        port = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_PORT']

        _o = SSHManager(host, username, password, True)
        print('delete ftp server file')
        result, msg = _o.ftp_rmd_file(server_path)
        _o.__del__()
        if not result:
            return False, msg
        print('delete ftp server file success')


        # 刪除机台服務器文件
        print('delete machine file')
        _tool_maintain = tool_maintain.objects.get(exptool=lot_info_product_name.exp_tool)
        tool_maintain_path = _tool_maintain.path
        catalog_machine_path = tool_maintain_path
        # catalog_machine_path = '/home/ebm9500' + os.path.join(tool_maintain_path,
        #                                                       Constant.CATALOG_MACHINE_DICT[tool]) + '/'
        print(tool_maintain_path, catalog_machine_path)

        machine_server_path = os.path.join(catalog_machine_path, lot_info_product_name.mask_name)
        print("machine_server_path =", machine_server_path)

        host = _tool_maintain.ip
        username = _tool_maintain.account
        password = _tool_maintain.password

        _o_2 = SSHManager(host, username, password)
        # cmd_del = 'ls -al'
        cmd_del = 'rm -rf ' + machine_server_path
        print(_o_2.ssh_exec_cmd(cmd_del))
        _o_2.__del__()

        return True, 'success'
    except Exception as e:
        traceback.print_exc()
        print(e)
        return False, str(e)


def del_writer_ftp_file(tip_no):
    try:
        lot_info_product_name_list = lot_info.objects.filter(tip_no=tip_no).values('info_tree_tool_id',
                                                                                   'mask_name', 'exp_tool').distinct()

        if lot_info_product_name_list.count() != 0:
            for lot_info_product_name in lot_info_product_name_list:
                tool = lot_info_product_name['info_tree_tool_id']
                machine_folder = Constant.CATALOG_MACHINE_DICT[tool]

                # 刪除暂存服務器文件
                server_path = os.path.join(Constant.CATALOG_FTP_SERVER_SSH_PATH + machine_folder,
                                           lot_info_product_name['mask_name'])

                print("server_path =", server_path)
                host = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_HOST']
                username = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_ACCOUNT']
                password = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_PASSWORD']

                _o = SSHManager(host, username, password)
                cmd_del = 'mv -r ' + server_path + ' /dev/null'
                _o.ssh_exec_cmd(cmd_del)
                _o.__del__()

                # 刪除机台服務器文件
                _tool_maintain = tool_maintain.objects.get(exptool=lot_info_product_name['exp_tool'])
                tool_maintain_path = _tool_maintain.path
                catalog_machine_path = tool_maintain_path + '/'
                # catalog_machine_path = '/home/ebm9500' + os.path.join(tool_maintain_path,
                #                                                       Constant.CATALOG_MACHINE_DICT[tool]) + '/'
                print(tool_maintain_path, catalog_machine_path)

                machine_server_path = os.path.join(catalog_machine_path, lot_info_product_name['mask_name'])
                print("machine_server_path =", machine_server_path)

                host = _tool_maintain.ip
                username = _tool_maintain.account
                password = _tool_maintain.password

                _o_2 = SSHManager(host, username, password)
                cmd_del = 'mv -r ' + machine_server_path + ' /dev/null'
                print(_o_2.ssh_exec_cmd(cmd_del))
                _o_2.__del__()

        return True, 'success'
    except Exception as e:
        traceback.print_exc()
        print(e)
        return False, str(e)
