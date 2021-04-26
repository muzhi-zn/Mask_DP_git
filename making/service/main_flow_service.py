import logging
import smtplib
import traceback
import os
import shutil
import ftplib
from email.header import Header
from email.mime.text import MIMEText

from django.db import close_old_connections
from django.db.models import Q
from Mask_DP.settings import E_MAIL_CONFIG
from jdv.models import lot_info, mes_blank_code
from making.models import convert_status_stage, convert_status
from making.service.convert_status_service import convertStatusLog
from making.service.fracture_service import GenerateFileService
from system.models import user
from system.service.dict_service import GetValueByType
from tooling_form.models import device_info, layout_info
from tooling_form.service.show_tip_no_service import del_fracture_file, del_writer_ftp_file
from utilslibrary.system_constant import Constant
from utilslibrary.utils import iems_utils
from utilslibrary.utils.date_utils import getDateStr
from utilslibrary.utils.file_utils import get_fracture_log_file_name, get_fracture_xor_file_name, \
    get_fracture_xor_log_file_name
from infotree.models import released_info_alta, released_info, released_mdt, unreleased_mdt, cd_map, cec
from utilslibrary.system_constant import Constant
from catalog.models import tool_maintain
from utilslibrary.mes_webservice.mes_webservice import mes_op_start, mes_op_comp, mes_op_start_cancel, get_wip_for_task
from utilslibrary.utils.ssh_utils import SSHManager

log = logging.getLogger('log')


class mainFlow:
    trail_user_id = 0
    trail_user_name = "Auto"

    def run(self):
        """执行主流程方法"""
        log.info("开始执行自动化流程。。。")
        try:
            mail_dict = {}
            # 获取需要执行自动化流程的lot信息, DIS站点之后的不需要执行
            lot_list = lot_info.objects.filter(status=3, mes_operation_number__lte=Constant.MES_OPERATION_NUM_DIS)
            for lot in lot_list:
                if lot.mes_operation_id:  # 如果operation_id不为空
                    flag, content = self.run_flow(lot)
                    owner_id = lot.lot_owner_id
                    if not flag:
                        if lot.lot_owner_id not in mail_dict:
                            mail_dict[owner_id] = content
                        else:
                            mail_dict[owner_id] = mail_dict[owner_id] + content
            for k, v in mail_dict.items():
                self.send_notice_mail('Convert Status Run Fail', v, k)
        except:
            traceback.print_exc()

    def run_flow(self, lot: lot_info):
        """执行device主流程"""
        send_mail_flag = True
        content = ''
        try:
            device_list = device_info.objects.values('device_type',
                                                     'device_name').filter(tip_no=lot.tip_no, is_delete=0).distinct()
            for device in device_list:
                if device['device_type'] == "Main":
                    stage_list = convert_status_stage.objects.filter(
                        ~Q(stage_name=Constant.MAKING_CONVERT_STATUS_STAGE_NAME_WRITER), type=1, device_type="Main",
                        order__gt=1).order_by(
                        'order')
                else:
                    stage_list = convert_status_stage.objects.filter(
                        ~Q(stage_name=Constant.MAKING_CONVERT_STATUS_STAGE_NAME_WRITER), type=1, order__gt=1).order_by(
                        'order')
                for stage in stage_list:
                    # 查询出wait状态下的convert_status
                    c_s = convert_status.objects.filter(tip_no=lot.tip_no, mask_name=lot.mask_name, lot_id=lot.lot_id,
                                                        device_name=device['device_name'], stage_id=stage.id,
                                                        status=Constant.CONVERT_STATUS_WAIT).first()
                    pre_c_s = convert_status.objects.filter(tip_no=lot.tip_no, mask_name=lot.mask_name,
                                                            lot_id=lot.lot_id,
                                                            device_name=device['device_name'],
                                                            stage=stage.pre_stage).first()
                    if c_s and (pre_c_s.status == Constant.CONVERT_STATUS_DONE or
                                pre_c_s.operation_status == Constant.CONVERT_OPERATION_SKIP) and \
                            pre_c_s.operation_status != Constant.CONVERT_OPERATION_HOLD:  # 查询到的convert_status不为空且上级站点状态不为hold
                        if c_s.operation_status != Constant.CONVERT_OPERATION_SKIP:  # 状态不为skip
                            flag, err_msg = self.flow_operation(stage, c_s)
                            if flag:
                                lot.convert_status_dec = c_s.stage + ' O/G'
                                lot.save()
                            send_mail_flag = send_mail_flag & flag
                            if not flag:
                                content += "TipNo: %s\r\nMaskName: %s\r\nLotID: %s\r\nDeviceName : %s\r\n%s\r\n\r\n" % \
                                           (lot.tip_no, lot.mask_name, lot.lot_id, device['device_name'], err_msg)
                        else:  # skip状态
                            c_s.status = Constant.CONVERT_STATUS_DONE  # skip直接过站
                            c_s.save()
        except Exception as e:
            log.error(traceback.format_exc())
            send_mail_flag = False
            content += "TipNo: %s\r\nMaskName: %s\r\nLotID: %s\r\nDeviceName : %s\r\n%s\r\n\r\n" % \
                       (lot.tip_no, lot.mask_name, lot.lot_id, device.device_name, str(e))
        return send_mail_flag, content

    def flow_operation(self, stage: convert_status_stage, c_s: convert_status):
        """执行流程中的操作"""
        log.info(c_s.tip_no + "|" + c_s.mask_name + "|" + c_s.device_name + "|" + stage.stage_name + "|执行flow")
        exec_url = GetValueByType().getValueByLabel(Constant.IEMS_SERVER_EXECUTE_CMD_URL)
        # exec_url = 'http://127.0.0.1:8001/api/execute_cmd/'
        f_temp_no = GetValueByType().getValueByLabel(Constant.IEMS_FRACTURE_TEMPLATE_ID)
        f_callback_url = GetValueByType().getValueByLabel(Constant.FRACTURE_CALLBACK_URL)
        x_temp_no = GetValueByType().getValueByLabel(Constant.IEMS_FRACTURE_XOR_TEMPLATE_ID)
        x_callback_url = GetValueByType().getValueByLabel(Constant.FRACTURE_XOR_CALLBACK_URL)
        if stage.stage_name == Constant.MAKING_CONVERT_STATUS_STAGE_NAME_FRACTURE:  # fracture站点
            return self.operation_fracture(c_s, exec_url, f_temp_no, f_callback_url)
        elif stage.stage_name == Constant.MAKING_CONVERT_STATUS_STAGE_NAME_XOR:  # XOR站点
            return self.operation_fracture_xor(c_s, exec_url, x_temp_no, x_callback_url)
        elif stage.stage_name == Constant.MAKING_CONVERT_STATUS_STAGE_NAME_JDV:  # JDV站点
            c_s.status = Constant.CONVERT_STATUS_DONE
            c_s.remark = 'Auto Main Flow Do Fail'
            c_s.save()
            return False, 'JDV TODO'
        elif stage.stage_name == Constant.MAKING_CONVERT_STATUS_STAGE_NAME_CCD:  # CCD站点
            c_s.status = Constant.CONVERT_STATUS_DONE
            c_s.remark = 'Auto Main Flow Do Fail'
            c_s.save()
            return False, 'CCD TODO'

    def operation_fracture(self, c_s: convert_status, exec_url, f_temp_no, f_callback_url):
        """fracture操作"""
        c_s.status = Constant.CONVERT_STATUS_ON_GOING
        c_s.operator = self.trail_user_name
        c_s.save()
        # redeck 操作
        tool_id = lot_info.objects.get(lot_id=c_s.lot_id).info_tree_tool_id
        _s = GenerateFileService()
        data = _s.fracture_deck(self.trail_user_id, self.trail_user_name, c_s.lot_id, c_s.tip_no,
                                c_s.mask_name, c_s.device_name, Constant.STAGE_FRACTURE, tool_id)
        if data['success']:  # redeck成功进行redo操作
            f_fracture_log_file = get_fracture_log_file_name(c_s.mask_name[0:6], c_s.mask_name[-5:],
                                                             c_s.device_name)
            param = {'temp_no': f_temp_no,
                     'params': c_s.location + ',' + c_s.file_name + ',' + f_fracture_log_file,
                     'callback_url': f_callback_url}
            result_json = iems_utils.execute_cmd_url(exec_url, param)
            if result_json.get('code') == 200:  # 执行IEMS请求成功
                record_no = result_json.get('data')[0] if result_json.get('data') else ''
                c_s.record_no = record_no
                c_s.save()
                code = result_json.get('code')
                result = 'success'
                message = result_json.get('msg')
                convertStatusLog().add_operation_log(c_s.id, Constant.CONVERT_OPERATION_AUTO_DECKANDDO,
                                                     self.trail_user_id, self.trail_user_name,
                                                     result, message, exec_url, param, code,
                                                     c_s.mask_name, c_s.device_name, record_no,
                                                     getDateStr())
                return True, ''
            else:
                c_s.status = Constant.CONVERT_STATUS_JOB_FAIL
                c_s.remark = 'Auto Main Flow Do Fail'
                c_s.save()
                return False, '执行Fracture命令失败'
        else:
            c_s.status = Constant.CONVERT_STATUS_JOB_FAIL
            c_s.remark = 'Auto Main Flow Deck Fail'
            c_s.save()
            return False, '生成Fracture文件失败'

    def operation_fracture_xor(self, c_s: convert_status, exec_url, x_temp_no, x_callback_url):
        """xor操作"""
        c_s.operator = self.trail_user_name
        c_s.status = Constant.CONVERT_STATUS_ON_GOING
        c_s.save()
        _s = GenerateFileService()
        data = _s.fracture_xor_deck(self.trail_user_id, self.trail_user_name, c_s.lot_id, c_s.device_name)
        if data['success']:
            x_fracture_log_file = get_fracture_xor_log_file_name(c_s.mask_name[0:6], c_s.mask_name[-5:],
                                                                 c_s.device_name)
            param = {'temp_no': x_temp_no, 'params': c_s.location + ',' + 'mrcexe_lsf.sh' + ',' +
                                                     c_s.file_name + ',' + x_fracture_log_file,
                     'callback_url': x_callback_url}
            result_json = iems_utils.execute_cmd_url(exec_url, param)
            if result_json.get('code') == 200:  # 执行IEMS请求成功
                record_no = result_json.get('data')[0] if result_json.get('data') else ''
                c_s.record_no = record_no
                c_s.save()
                code = result_json.get('code')
                result = 'success'
                message = result_json.get('msg')
                convertStatusLog().add_operation_log(c_s.id, Constant.CONVERT_OPERATION_AUTO_DECKANDDO,
                                                     self.trail_user_id, self.trail_user_name,
                                                     result, message, exec_url, param, code,
                                                     c_s.mask_name, c_s.device_name, record_no,
                                                     getDateStr())
                return True, ''
            else:
                c_s.status = Constant.CONVERT_STATUS_JOB_FAIL
                c_s.remark = 'Auto Main Flow Do Fail'
                c_s.save()
                return False, '执行Fracture XOR命令失败'
        else:
            c_s.status = Constant.CONVERT_STATUS_JOB_FAIL
            c_s.remark = 'Auto Main Flow Deck Fail'
            c_s.save()
            return False, '生成Fracture XOR文件失败'

    def run_writer_flow(self):
        """执行上传writer操作的定时任务"""
        log.info("执行上传writer的自动化流程")
        try:
            lot_list = lot_info.objects.filter(status=3, writer_create_file_status=0,
                                               mes_operation_number__lte=Constant.MES_OPERATION_NUM_DIS)
            print("Count = ", lot_list.count())
            for lot in lot_list:
                # print("mask_name = ", lot.writer_create_file_status)
                # 每个lot下的所有device的的每个writer站点之前的状态都要为Done
                flag = True
                device_list = device_info.objects.filter(tip_no=lot.tip_no, mask_name=lot.mask_name)
                print("tip_no =", lot.tip_no)
                try:
                    for device in device_list:
                        if device.device_type == "Main":
                            stage_list = convert_status_stage.objects.filter(
                                ~Q(stage_name=Constant.MAKING_CONVERT_STATUS_STAGE_NAME_WRITER), type=1,
                                device_type="Main",
                                order__gt=1).order_by(
                                'order')
                        else:
                            stage_list = convert_status_stage.objects.filter(
                                ~Q(stage_name=Constant.MAKING_CONVERT_STATUS_STAGE_NAME_WRITER), type=1,
                                order__gt=1).order_by(
                                'order')
                        for stage in stage_list:
                            c_s = convert_status.objects.get(lot_id=lot.lot_id, device_name=device.device_name,
                                                             stage_id=stage.id)
                            if c_s.status != Constant.CONVERT_STATUS_DONE:
                                if c_s.operation_status != Constant.CONVERT_OPERATION_SKIP:
                                    flag = False
                                    break
                        if not flag:
                            break
                except:
                    traceback.print_exc()

                # 前置条件校验通过开始执行上传writer操作 TODO
                if flag:
                    log.info(lot.lot_id + "开始执行上传writer操作")
                    print("mask_name = ", lot.mask_name)
                    try:
                        # writer_create_file_status:
                        # 0: 未生成文件    1: 生成文件中    2: 生成失敗     3: 生成成功
                        query_set = convert_status.objects.filter(lot_id=lot.lot_id, stage='Writer')
                        for query in query_set:
                            query.status = 1
                            query.save()
                        lot_info.objects.filter(id=lot.id).update(writer_create_file_status=1)
                        result = create_catalog_file(lot.id, lot.lot_id, lot.mask_name, lot.tip_no, lot.exp_tool,
                                                     lot.mes_carrier_id, lot.info_tree_tool_id).main()
                        if result['result']:
                            update_writer_stage_status(lot, Constant.CONVERT_STATUS_DONE, "")
                            convert_status.objects.filter(lot_id=lot.lot_id, stage_id="5").update(progress="100.00%")
                            lot_info.objects.filter(id=lot.id).update(writer_create_file_status=3)
                        else:
                            del_fracture_file(lot.lot_id, False)
                            update_writer_stage_status(lot, Constant.CONVERT_STATUS_JOB_FAIL, result['data'])
                            lot_info.objects.filter(id=lot.id).update(writer_create_file_status=2,
                                                                      writer_create_file_error_message=result['data'])
                            print(result['data'])
                    except Exception as e:
                        print(e)
                        del_fracture_file(lot.lot_id, False)
                        update_writer_stage_status(lot, Constant.CONVERT_STATUS_JOB_FAIL, str(e))
                        lot_info.objects.filter(id=lot.id).update(writer_create_file_status=2,
                                                                  writer_create_file_error_message="Writer create file failed")

            dispatch_lot_list = lot_info.objects.filter(writer_create_file_status=3, dispatch_flag=1,
                                                        ftp_upload_status=0)
            print("dispatch_Count = ", dispatch_lot_list.count())

            for dispatch_lot in dispatch_lot_list:
                try:
                    print("mes_op_start_cancel =================")
                    mes_op_start_cancel_100_700_result = mes_op_start_cancel(dispatch_lot.lot_id,
                                                                             dispatch_lot.mes_operation_id)
                    print("mes_op_start_cancel =", mes_op_start_cancel_100_700_result)
                    print("mes_op_start_cancel =================")

                    print("mes_op_start =================")
                    op_start_100_700_result = mes_op_start(dispatch_lot.lot_id, dispatch_lot.mes_operation_id)
                    # get_wip_for_task()
                    print("mes_op_start =", op_start_100_700_result)
                    print("mes_op_start =================")
                    if op_start_100_700_result:
                        lot_info.objects.filter(id=dispatch_lot.id).update(ftp_upload_status=1)
                        ftp_result = writer_file_move(dispatch_lot).main()

                        if ftp_result['result']:
                            lot_info.objects.filter(id=dispatch_lot.id).update(ftp_upload_status=3)
                            print("mes_op_comp =================")
                            mes_op_comp_100_700_result = mes_op_comp(dispatch_lot.lot_id, dispatch_lot.mes_operation_id)
                            print("mes_op_comp =", mes_op_comp_100_700_result)
                            print("mes_op_comp =================")
                        else:
                            del_writer_ftp_file(dispatch_lot.lot_id)
                            lot_info.objects.filter(id=dispatch_lot.id).update(ftp_upload_status=2,
                                                                               ftp_upload_error_message=ftp_result[
                                                                                   'data'])
                            print("mes_op_start_cancel =================")
                            mes_op_start_cancel_100_700_result = mes_op_start_cancel(dispatch_lot.lot_id,
                                                                                     dispatch_lot.mes_operation_id)
                            print("mes_op_start_cancel =", mes_op_start_cancel_100_700_result)
                            print("mes_op_start_cancel =================")
                    else:
                        del_writer_ftp_file(dispatch_lot.lot_id)
                        lot_info.objects.filter(id=dispatch_lot.id).update(ftp_upload_status=2,
                                                                           ftp_upload_error_message="mes op start error")
                except Exception as e:
                    print(traceback.format_exc())
                    print(e)
                    del_writer_ftp_file(dispatch_lot.lot_id)
                    lot_info.objects.filter(id=dispatch_lot.id).update(ftp_upload_status=2,
                                                                       ftp_upload_error_message="FTP upload failed")
                    print("mes_op_start_cancel =================")
                    mes_op_start_cancel_100_700_result = mes_op_start_cancel(dispatch_lot.lot_id,
                                                                             dispatch_lot.mes_operation_id)
                    print("mes_op_start_cancel =", mes_op_start_cancel_100_700_result)
                    print("mes_op_start_cancel =================")
        except:
            traceback.print_exc()

        # rigester_list = lot_info.objects.filter(writer_create_file_status=3, dispatch_flag=1, ftp_upload_status=0)

    def send_notice_mail(self, title, content, user_id):
        """发送通知邮件"""
        u = user.objects.get(pk=user_id)
        if u.email:
            receivers = [u.email]
        else:
            receivers = [E_MAIL_CONFIG['USER']]
        host = E_MAIL_CONFIG['HOST']
        sender = E_MAIL_CONFIG['USER']
        message = MIMEText(content, 'plain', 'utf-8')
        message['From'] = Header("DP Automation", 'utf-8')
        message['To'] = Header("Dear customer", 'utf-8')
        message['Subject'] = Header(title, 'utf-8')
        try:
            smtpObj = smtplib.SMTP(host=host)
            smtpObj.connect(host, 465)  # 25 为 SMTP 端口号
            smtpObj.ehlo()
            smtpObj.starttls()
            smtpObj.login(E_MAIL_CONFIG['USER'], E_MAIL_CONFIG['PASSWORD'])
            smtpObj.sendmail(sender, receivers, message.as_string())
            log.info("通知邮件发送成功")
            return True
        except Exception as e:
            print(traceback.format_exc())
            log.error("发送通知邮件出现错误：" + str(e))
            return False


class create_catalog_file:

    def __init__(self, lot_info_id, lot_id, mask_name, tip_no, exp_tool, mes_carrier_id, info_tree_tool_id):
        machine_folder = Constant.CATALOG_MACHINE_DICT[info_tree_tool_id]
        self.lot_info_id = lot_info_id
        self.lot_id = lot_id
        self.catalog_local_path = Constant.CATALOG_LOCAL_PATH
        self.catalog_ftp_server_path = Constant.CATALOG_FTP_SERVER_PATH + machine_folder + "/"
        self.mask_name = mask_name
        self.tip_no = tip_no
        self.exp_tool = exp_tool
        self.mes_carrier_id = mes_carrier_id
        self.product = mask_name.split("-")[0] + "/"
        self.layer = mask_name.split("-")[1] + "/"
        self.catalog_ftp_host = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_HOST']
        self.catalog_ftp_port = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_PORT']
        self.catalog_ftp_account = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_ACCOUNT']
        self.catalog_ftp_password = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_PASSWORD']

    def main(self):
        try:
            # 刪除現存文件
            del_current_file_result = self.del_current_file()
            print("del_current_file_result =", del_current_file_result['result'])
            if not del_current_file_result['result']:
                return del_current_file_result

            convert_status.objects.filter(lot_id=self.lot_id, stage_id="5").update(progress="10.00%")

            # writer_create_file_status:
            #   0: 未生成文件
            #   1: 生成文件中
            #   2: 生成失敗create_temp_result
            #   3: 生成成功

            # create_fracture_path
            fracture_path_result = self.create_fracture_path()
            print("fracture_path_result =", fracture_path_result['result'])
            if not fracture_path_result['result']:
                return fracture_path_result
            else:
                fracture_path_dict = fracture_path_result['data']

            convert_status.objects.filter(lot_id=self.lot_id, stage_id="5").update(progress="20.00%")

            # get_info_tree_param
            info_tree_param_result = self.get_info_tree_param()
            print("info_tree_param_result =", info_tree_param_result['result'])
            if not info_tree_param_result['result']:
                return info_tree_param_result
            else:
                info_tree_param_dict = info_tree_param_result['data']

            convert_status.objects.filter(lot_id=self.lot_id, stage_id="5").update(progress="30.00%")

            # create_temp
            create_temp_result = self.create_temp()
            print("create_temp_result =", create_temp_result['result'])
            if not create_temp_result['result']:
                return create_temp_result

            convert_status.objects.filter(lot_id=self.lot_id, stage_id="5").update(progress="40.00%")

            # create_main_folder
            create_main_folder_result = self.create_main_folder()
            print("create_main_folder_result =", create_main_folder_result['result'])
            if not create_main_folder_result['result']:
                return create_main_folder_result
            else:
                main_folder_path = create_main_folder_result['data']

            convert_status.objects.filter(lot_id=self.lot_id, stage_id="5").update(progress="50.00%")

            # create_chip_ini
            create_chip_ini_result = self.create_chip_ini(main_folder_path)
            print("create_chip_ini_result =", create_chip_ini_result['result'])
            if not create_chip_ini_result['result']:
                return create_chip_ini_result
            else:
                chip_ini_path = create_chip_ini_result['data']

            convert_status.objects.filter(lot_id=self.lot_id, stage_id="5").update(progress="60.00%")

            # create_layout_ini
            create_layout_ini_result = self.create_layout_ini(main_folder_path, info_tree_param_dict)
            print("create_layout_ini_result =", create_layout_ini_result['result'])
            if not create_layout_ini_result['result']:
                return create_layout_ini_result

            convert_status.objects.filter(lot_id=self.lot_id, stage_id="5").update(progress="70.00%")

            # create_layout_folder
            create_layout_folder_result = self.create_layout_folder(main_folder_path, info_tree_param_dict)
            print("create_layout_folder_result =", create_layout_folder_result['result'])
            if not create_layout_folder_result['result']:
                return create_layout_folder_result
            else:
                layout_folder_path = create_layout_folder_result['data']

            convert_status.objects.filter(lot_id=self.lot_id, stage_id="5").update(progress="80.00%")

            # create_chip_data
            create_chip_data_result = self.create_chip_data(main_folder_path, chip_ini_path, fracture_path_dict,
                                                            info_tree_param_dict)
            print("create_chip_data_result =", create_chip_data_result['result'])
            if not create_chip_data_result['result']:
                return create_chip_data_result

            convert_status.objects.filter(lot_id=self.lot_id, stage_id="5").update(progress="90.00%")

            # create_aw_xml
            if info_tree_param_dict['mdt_value'] == "Y":
                create_aw_xml_result = self.create_aw_xml(layout_folder_path, info_tree_param_dict)
                print("create_aw_xml_result =", create_aw_xml_result['result'])
                if not create_aw_xml_result['result']:
                    return create_aw_xml_result

            convert_status.objects.filter(lot_id=self.lot_id, stage_id="5").update(progress="95.00%")

            return {"result": True, "data": "success"}
        except Exception as e:
            print("create_catalog_file main failed\n", str(e))
            return {"result": False, "data": "create_catalog_file main failed\n" + str(e)}

    def del_current_file(self):
        try:
            del_fracture_file_result = del_fracture_file(self.lot_id, False)
            if del_fracture_file_result[0]:
                return {"result": True, "data": "success"}
            else:
                return {"result": False, "data": "del_current_file failed\n" + str(del_fracture_file_result[1])}
        except Exception as e:
            print("del_current_file failed\n", str(e))
            return {"result": False, "data": "del_current_file failed\n" + str(e)}

    def create_fracture_path(self):
        try:
            DEVICE_INFO_FILE_BASE_PATH = Constant.TEMPLATE_FILE_GENERATE_PATH
            fracture_base_dir = DEVICE_INFO_FILE_BASE_PATH + self.product + "Device/"
            # fracture_base_dir_list = os.listdir(fracture_base_dir)
            # print(fracture_base_dir_list)

            aaa = os.listdir(fracture_base_dir)
            print(aaa)

            device_list = device_info.objects.filter(tip_no=self.tip_no, mask_name=self.mask_name).values('device_name')
            print("===" * 20)
            print(device_list)
            print(device_list.count())
            print("===" * 20)
            fracture_base_dir_list = []
            for index in device_list:
                fracture_base_dir_list.append(index['device_name'])

            fracture_path_dict = {'fracture_base_dir': fracture_base_dir,
                                  'fracture_base_dir_list': fracture_base_dir_list}

            return {"result": True, "data": fracture_path_dict}
        except Exception as e:
            print("create_fracture_path failed\n", str(e))
            return {"result": False, "data": "create_fracture_path failed\n" + str(e)}

    def get_info_tree_param(self):
        try:
            lot_info_data = lot_info.objects.get(id=self.lot_info_id)
            customer = lot_info_data.customer
            tool = lot_info_data.info_tree_tool_id
            # print("tool", tool)
            node = lot_info_data.rule
            # print("node", node)
            tone = lot_info_data.tone
            # print("tone", tone)
            grade = lot_info_data.grade
            # print("grade", grade)
            pattern_density = "0-100"
            # print("pattern_density", pattern_density)
            layer = lot_info_data.mask_name.split("-")[1]
            print("layer", layer)

            # en_list = ['A', 'B', 'C', 'D', 'E', 'D', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            #            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
            # # _mes_blank = mes_blank_code.objects.get(layer_name=layer[0:3], is_delete=0)
            # _mes_blank = mes_blank_code.objects.filter(~Q(layer_name=layer[0:3]), ~Q(layer_name="*"),
            #                                            tone=tone,
            #                                            is_delete=0).order_by("seq")[0]
            #
            # grade_from = _mes_blank.grade_from
            # grade_to = _mes_blank.grade_to
            # grade_range = en_list[en_list.index(grade_from):en_list.index(grade_to) + 1]
            # print("layer =", layer[0:3])
            # blank = _mes_blank.blank_code
            blank = lot_info_data.blank_code
            if tool == 'MS03':
                info_tree_group = \
                released_info_alta.objects.filter(customer=customer, tool=tool, node=node, tone=tone, grade=grade,
                                                  blank=blank, pattern_density=pattern_density,
                                                  layer=layer[0:3],
                                                  is_delete=0).values('group').distinct()[0]['group']
                mdt_data = released_info_alta.objects.get(group=info_tree_group, item='MDT')
                cd_map_id = 0
                cec_id = 0
            else:
                print('customer=' + customer)
                print('tool=' + tool)
                print('node=' + node)
                print('tone=' + tone)
                print('grade=' + grade)
                print('blank=' + blank)
                print('pattern_density=' + pattern_density)
                print('layer=' + layer[0:3])
                info_tree_group = released_info.objects.filter(customer=customer, tool=tool, node=node, tone=tone,
                                                               grade=grade,
                                                               blank=blank, pattern_density=pattern_density,
                                                               layer=layer[0:3],
                                                               is_delete=0).values('group').distinct()[0]['group']
                mdt_data = released_info.objects.get(group=info_tree_group, cs_command='MDT', is_delete=0)
                cd_map_id = released_info.objects.get(group=info_tree_group, cs_command='CS_POSITIONAL_CD_MAP',
                                                      is_delete=0).cd_map_id
                cec_id = released_info.objects.get(group=info_tree_group, cs_command='CEC_PARAM', is_delete=0).cec_id

            info_tree_param_dict = {"tool": tool,
                                    "customer": customer,
                                    "node": node,
                                    "tone": tone,
                                    "grade": grade,
                                    "blank": blank,
                                    "pattern_density": pattern_density,
                                    "layer": layer,
                                    "info_tree_group": info_tree_group,
                                    "mdt_id": mdt_data.id,
                                    "mdt_value": mdt_data.value,
                                    "cd_map_id": cd_map_id,
                                    "cec_id": cec_id}

            return {"result": True, "data": info_tree_param_dict}
        except Exception as e:
            traceback.print_exc()
            print("get_info_tree_param failed\n", str(e))
            return {"result": False, "data": "get_info_tree_param failed\n" + str(e)}

    def create_temp(self):
        try:
            if not os.path.exists(self.catalog_local_path):
                os.mkdir(self.catalog_local_path)
            return {"result": True, "data": "success"}
        except Exception as e:
            print("create_temp failed\n", str(e))
            return {"result": False, "data": "create_temp failed\n" + str(e)}

    def create_main_folder(self):
        try:
            main_folder_path = os.path.join(self.catalog_local_path, self.mask_name + "/")
            print(main_folder_path)
            if not os.path.exists(main_folder_path):
                os.mkdir(main_folder_path)
            return {"result": True, "data": main_folder_path}
        except Exception as e:
            print("create_main_folder failed\n", str(e))
            return {"result": False, "data": "create_main_folder failed\n" + str(e)}

    def create_chip_ini(self, main_folder_path):
        try:
            print("main_folder_path =", main_folder_path)
            chip_ini_path = main_folder_path + "chip.ini"
            if not os.path.exists(chip_ini_path):
                os.mknod(chip_ini_path)
            return {"result": True, "data": chip_ini_path}
        except Exception as e:
            print("create_chip_ini failed\n", str(e))
            return {"result": False, "data": "create_chip_ini failed\n" + str(e)}

    def create_layout_ini(self, main_folder_path, info_tree_param_dict):
        try:
            layout_ini_path = main_folder_path + "layout.ini"
            layout_ini_hide_path = main_folder_path + ".layout.ini"
            # print(layout_ini_path)
            if not os.path.exists(layout_ini_path):
                os.mknod(layout_ini_path)

                layout_ini_fp = open(layout_ini_path, "w+")
                layout_ini_seq = ["[layout]\n",
                                  'layout_name = "' + self.mask_name + '";\n',
                                  'script = "level1.mds";']

                if info_tree_param_dict['mdt_value'] == 'Y':
                    layout_ini_seq.append('\naw_file = "level1.aw.xml";')
                layout_ini_fp.writelines(layout_ini_seq)
                layout_ini_fp.close()

                shutil.copyfile(layout_ini_path, layout_ini_hide_path)

            return {"result": True, "data": "success"}
        except Exception as e:
            print("create_layout_ini failed\n", str(e))
            return {"result": False, "data": "create_layout_ini failed\n" + str(e)}

    def create_layout_folder(self, main_folder_path, info_tree_param_dict):
        try:
            layout_folder_path = os.path.join(main_folder_path, "layout/")

            if not os.path.exists(layout_folder_path):
                # Get path
                os.mkdir(layout_folder_path)
                source_mds_path = '/Mask_DP_download/mds_template.mds'
                new_mds_path = layout_folder_path + "level1.mds"
                new_mds_hide_path = layout_folder_path + ".level1.mds"

                shutil.copyfile(source_mds_path, new_mds_path)

                f_1 = open(new_mds_path, "r", encoding="utf-8")
                f_1_data = f_1.readlines()

                f_1.close()
                f_2 = open(new_mds_path, "w+", encoding="utf-8")

                print(f_1_data)
                for i in f_1_data:
                    if 'layout_name="X"' in i:
                        f_2.write(i.replace('layout_name="X"', 'layout_name="' + self.mask_name + '"'))
                    elif 'devices1="X"' in i:
                        device_info_list = device_info.objects.filter(tip_no=self.tip_no,
                                                                      mask_name=self.mask_name,
                                                                      is_delete=0).values('device_name', 'lb_x', 'lb_y',
                                                                                          'rt_x', 'rt_y')
                        x_y_list = []
                        for data in device_info_list:
                            x_y_dict = {'Device_Name': data['device_name'],
                                        'LB_X': data['lb_x'],
                                        'LB_Y': data['lb_y'],
                                        'RT_X': data['rt_x'],
                                        'RT_Y': data['rt_y']}
                            x_y_list.append(x_y_dict)

                        devices_data_list = []
                        for x_y in x_y_list:
                            Device_Name = x_y['Device_Name']
                            LB_X = x_y['LB_X']
                            LB_Y = x_y['LB_Y']
                            RT_X = x_y['RT_X']
                            RT_Y = x_y['RT_Y']

                            layout_info_list = layout_info.objects.filter(tip_no=self.tip_no,
                                                                          device_name=Device_Name,
                                                                          mask_name=self.mask_name,
                                                                          is_delete=0).values('x1', 'y1', 'pitch_x',
                                                                                              'pitch_y', 'array_x',
                                                                                              'array_y')
                            for layout_info_data in layout_info_list:
                                X1 = layout_info_data['x1']
                                Y1 = layout_info_data['y1']
                                Pitch_X = layout_info_data['pitch_x']
                                Pitch_Y = layout_info_data['pitch_y']
                                Array_X = layout_info_data['array_x']
                                Array_Y = layout_info_data['array_y']
                                print(X1, Y1, Pitch_X, Pitch_Y, Array_X, Array_Y)
                                if Pitch_X == 'nan' or Pitch_Y == 'nan' or Array_X == 'nan' or Array_Y == 'nan' or \
                                        Pitch_X == '' or Pitch_Y == '' or Array_X == '' or Array_Y == '':
                                    print(111)
                                    print(X1, Y1, RT_X, LB_X, RT_Y, LB_Y)
                                    # X_cor = -X1 * 4 - [2 * (RT(X) - LB(X))]
                                    # Y_cor = Y1 * 4 - [2 * (RT(Y) - LB(Y))]
                                    X_cor = format(-float(X1) * 4 - (2 * (float(RT_X) - float(LB_X))), ".3f")
                                    Y_cor = format(float(Y1) * 4 - (2 * (float(RT_Y) - float(LB_Y))), ".3f")
                                    print("X_cor =", X_cor)
                                    print("Y_cor =", Y_cor)
                                    print(33)
                                    devices_data_list.append("  put " + str(X_cor) + " " + str(Y_cor) + " 1 0 $" +
                                                             self.mask_name.replace("-",
                                                                                    "_") + "_" + Device_Name + ";\n")
                                    print(44)
                                else:
                                    print(222)
                                    # device size(X) = 4 * [RT(X) - LB(X)]
                                    # device size(Y) = 4 * [RT(Y) - LB(Y)]
                                    # X_cor = -[device size(X) * (0.5 * Array_X) +
                                    #   (Pitch_X - device size(X))*(0.5 * Array_X - 0.5)]
                                    # Y_cor = -[device size(Y) * (0.5 * Array_Y) +
                                    #   (Pitch_Y - device size(Y))*(0.5 * Array_Y - 0.5)]

                                    device_size_x = 4 * (float(RT_X) - float(LB_X))
                                    device_size_y = 4 * (float(RT_Y) - float(LB_Y))
                                    X_cor = -(device_size_x * (0.5 * float(Array_X)) + (
                                            float(Pitch_X) - device_size_x) * (
                                                      0.5 * float(Array_X) - 0.5))
                                    Y_cor = -(device_size_y * (0.5 * float(Array_Y)) + (
                                            float(Pitch_Y) - device_size_y) * (
                                                      0.5 * float(Array_Y) - 0.5))
                                    print(device_size_x, device_size_y, X_cor, Y_cor)
                                    devices_data_list.append("  matrixput " + str(X_cor) + " " + str(Y_cor) + " " +
                                                             str(float(Pitch_X)) + " " +
                                                             str(float(Pitch_Y)) + " " +
                                                             str(float(Array_X)) + " " +
                                                             str(float(Array_X)) + " 1 0 $" +
                                                             self.mask_name.replace("-",
                                                                                    "_") + "_" + Device_Name + ";\n")

                        print(devices_data_list)
                        for aa in devices_data_list:
                            print(aa)
                        f_2.writelines(devices_data_list)
                    else:
                        f_2.write(i)
                f_2.close()

                shutil.copyfile(new_mds_path, new_mds_hide_path)

            return {"result": True, "data": layout_folder_path}
        except Exception as e:
            print("create_layout_folder failed\n", str(e))
            return {"result": False, "data": "create_layout_folder failed\n" + str(e)}

    def create_aw_xml(self, layout_folder_path, info_tree_param_dict):
        try:
            tool = info_tree_param_dict['tool']
            mdt_id = info_tree_param_dict['mdt_id']

            # aw_xml_path = layout_folder_path + "level1.aw.xml"
            aw_xml_path = os.path.join(layout_folder_path, "level1.aw.xml")
            # print(aw_xml_path)
            if tool == 'MS03':
                type = 2
            else:
                type = 1

            dose_list = released_mdt.objects.filter(type=type, released_id=mdt_id, is_delete=0).values(
                'writer_mdt', 'writer_dose').order_by("writer_mdt").distinct()

            print("dose list-------")
            print(dose_list)
            print(dose_list.count())
            print("dose list-------")

            if not os.path.exists(aw_xml_path):
                os.mknod(aw_xml_path)
                aw_xml_fp = open(aw_xml_path, "w+")
                aw_xml_seq = ['<WritingConditionLinkTable version="1.0">\n',
                              '<Function name="DoseModulation1">\n']

                for dose_data in dose_list:
                    print(dose_data)
                    aw_xml_seq.append('<Mapping>\n')
                    aw_xml_seq.append('<Name>default' + str(dose_data['writer_mdt']) + '</Name>\n')
                    aw_xml_seq.append('<Value type="dose">' + str(dose_data['writer_dose']) + '</Value>\n')
                    aw_xml_seq.append('</Mapping>\n')

                aw_xml_seq.append('</Function>\n')
                aw_xml_seq.append('</WritingConditionLinkTable>')
                aw_xml_fp.writelines(aw_xml_seq)
                aw_xml_fp.close()

            return {"result": True, "data": "success"}
        except Exception as e:
            print("create_aw_xml failed\n", str(e))
            return {"result": False, "data": "create_aw_xml failed\n" + str(e)}

    def create_chip_data(self, main_folder_path, chip_ini_path, fracture_path_dict, info_tree_param_dict):
        try:
            fracture_base_dir = fracture_path_dict['fracture_base_dir']
            fracture_base_dir_list = fracture_path_dict['fracture_base_dir_list']
            mdt_value = info_tree_param_dict['mdt_value']

            sum_chip_ini_seq = []
            for device_name in fracture_base_dir_list:

                source_chip_dir = fracture_base_dir + device_name + "/layer/" + self.layer + "fracture/" + \
                                  self.mask_name.replace("-", "_") + "_" + device_name + "/"
                new_chip_dir = main_folder_path + self.mask_name.replace("-", "_") + "_" + device_name + "/"
                if not os.path.exists(new_chip_dir):
                    shutil.copytree(source_chip_dir, new_chip_dir)
                if mdt_value == 'Y':
                    chip_ini_seq = ["[" + self.mask_name.replace("-", "_") + "_" + device_name + "]\n",
                                    'chip_name = "' + self.mask_name.replace("-", "_") + "_" + device_name + '";\n',
                                    # 'chip_dir = "' + self.ftp_server_base_path + '";\n',
                                    'chip_dir = "' + self.mask_name.replace("-", "_") + "_" + device_name + '";\n',
                                    'chip_data_format = "VSB-12i";\n',
                                    'writing_function = "DoseModulation1";\n',
                                    'attribution = "enable";\n']
                    # self.create_aux_xml(new_chip_dir)
                else:
                    chip_ini_seq = ["[" + self.mask_name.replace("-", "_") + "_" + device_name + "]\n",
                                    'chip_name = "' + self.mask_name.replace("-", "_") + "_" + device_name + '";\n',
                                    'chip_dir = "' + self.mask_name.replace("-", "_") + "_" + device_name + '";\n',
                                    'chip_data_format = "VSB-12";\n']

                sum_chip_ini_seq = sum_chip_ini_seq + chip_ini_seq

            chip_ini_fp = open(chip_ini_path, "a")
            chip_ini_fp.writelines(sum_chip_ini_seq)
            chip_ini_fp.close()

            return {"result": True, "data": "success"}
        except Exception as e:
            print("create_chip_data failed\n", str(e))
            return {"result": False, "data": "create_chip_data failed\n" + str(e)}

    def create_aux_xml(self, chip_path):
        try:
            aux_path = chip_path + "aux.xml"
            if not os.path.exists(aux_path):
                os.mknod(aux_path)

            aux_xml_fp = open(aux_path, "w+")
            aux_xml_seq = ['<AttributeInfoLinkTable version"1.0">\n',
                           '<Mapping type="ai">\n',
                           '<Value type="list">1</Value>\n',
                           '<Name>Main</Name>\n',
                           '</Mapping>\n',
                           '<Mapping type="ai">\n',
                           '<Value type="list">2</Value>\n',
                           '<Name>SB</Name>\n',
                           '</Mapping>\n',
                           '</AttributeInfoLinkTable>\n']
            aux_xml_fp.writelines(aux_xml_seq)
            aux_xml_fp.close()

            return {"result": True, "data": "success"}
        except Exception as e:
            print("create_aux_xml failed\n", str(e))
            return {"result": False, "data": "create_aux_xml failed\n" + str(e)}


def update_writer_stage_status(lot: lot_info, status, err_message):
    """更新writer状态
    status: wait 传 Constant.CONVERT_STATUS_WAIT
            ongoing 传 Constant.CONVERT_STATUS_ON_GOING
            job fail 传 Constant.CONVERT_STATUS_JOB_FAIL
            done 传 Constant.CONVERT_STATUS_DONE
    """
    try:
        tip_no = lot.tip_no
        mask_name = lot.mask_name
        convert_status.objects.filter(tip_no=tip_no, mask_name=mask_name, stage="Writer").update(status=status,
                                                                                                 err_message=err_message)
    except Exception as e:
        print(traceback.format_exc())
        log.error("更新writer状态出现错误：" + str(e))


class writer_file_move:
    def __init__(self, dispatch_lot):
        machine_folder = Constant.CATALOG_MACHINE_DICT[dispatch_lot.info_tree_tool_id]
        self.lot_info_id = dispatch_lot.id
        self.lot_id = dispatch_lot.lot_id
        self.tip_no = dispatch_lot.tip_no
        self.exp_tool = dispatch_lot.exp_tool
        self.info_tree_tool_id = dispatch_lot.info_tree_tool_id
        self.catalog_local_path = Constant.CATALOG_LOCAL_PATH
        self.catalog_ftp_server_path = Constant.CATALOG_FTP_SERVER_PATH + machine_folder + "/"
        self.product = dispatch_lot.mask_name.split("-")[0] + "/"
        self.mask_name = dispatch_lot.mask_name + "/"
        self.catalog_ftp_host = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_HOST']
        self.catalog_ftp_port = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_PORT']
        self.catalog_ftp_account = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_ACCOUNT']
        self.catalog_ftp_password = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_PASSWORD']

    def main(self):
        try:
            # delete writer ftp server file
            del_current_file_result = self.del_current_file()
            print("del_current_file_result =", del_current_file_result['result'])
            if not del_current_file_result['result']:
                return del_current_file_result

            # get local path tree
            get_local_path_tree_result = self.get_local_path_tree()
            print("get_local_path_tree_result =", get_local_path_tree_result['result'])
            if not get_local_path_tree_result['result']:
                return get_local_path_tree_result
            else:
                dir_list = get_local_path_tree_result['data']

            # connect ftp server
            connect_ftp_server_result = self.connect_ftp_server()
            print("connect_ftp_server_result =", connect_ftp_server_result['result'])
            if not connect_ftp_server_result['result']:
                return connect_ftp_server_result
            else:
                f = connect_ftp_server_result['data']

            # move_to_ftp_server
            move_to_ftp_server_result = self.move_to_ftp_server(dir_list, f)
            print("move_to_ftp_server_result =", move_to_ftp_server_result['result'])
            if not move_to_ftp_server_result['result']:
                return move_to_ftp_server_result
            close_old_connections()
            # connect machine
            connect_machine_result = self.connect_machine()
            print("connect_machine_result =", connect_machine_result['result'])
            if not connect_machine_result['result']:
                return connect_machine_result
            else:
                m_f = connect_machine_result['data']

            # move_to_machine
            move_to_machine_result = self.move_to_machine(dir_list, m_f)
            print("move_to_machine_result =", move_to_machine_result['result'])
            if not move_to_machine_result['result']:
                return move_to_machine_result

            return {"result": True, "data": "success"}
        except Exception as e:
            print("writer_file_move main failed\n", str(e))
            return {"result": False, "data": "writer_file_move main failed\n" + str(e)}

    def del_current_file(self):
        try:
            del_fracture_file_result = del_writer_ftp_file(self.lot_id)
            if del_fracture_file_result[0]:
                return {"result": True, "data": "success"}
            else:
                return {"result": False, "data": "del_current_file failed\n" + str(del_fracture_file_result[1])}
        except Exception as e:
            print("del_current_file failed\n", str(e))
            return {"result": False, "data": "del_current_file failed\n" + str(e)}

    def get_local_path_tree(self):
        try:
            main_folder_path = os.path.join(self.catalog_local_path, self.mask_name)

            main_dir = main_folder_path
            dir_list = ["M_" + main_dir]

            for i in os.listdir(main_dir):
                if os.path.isdir(main_dir + i):
                    dir_list.append("D_" + main_dir + i + "/")
                    L_2_path = main_dir + i + "/"
                    for L_2 in os.listdir(L_2_path):
                        if os.path.isdir(L_2_path + L_2):
                            dir_list.append("D_" + L_2_path + L_2 + "/")
                            L_3_path = L_2_path + i + "/"
                            for L_3 in os.listdir(L_3_path):
                                if os.path.isdir(L_3_path + L_3):
                                    dir_list.append("D_" + L_3_path + L_3 + "/")
                                if os.path.isfile(L_3_path + L_3):
                                    dir_list.append("F_" + L_3_path + L_3)

                        if os.path.isfile(L_2_path + L_2):
                            dir_list.append("F_" + L_2_path + L_2)

                if os.path.isfile(main_dir + i):
                    dir_list.append("F_" + main_dir + i)

            return {"result": True, "data": dir_list}
        except Exception as e:
            traceback.print_exc()
            print("get_local_path_tree failed\n", str(e))
            return {"result": False, "data": "get_local_path_tree failed\n" + str(e)}

    def connect_ftp_server(self):
        try:
            ftp = ftplib.FTP
            host = self.catalog_ftp_host
            ftp_port = self.catalog_ftp_port
            username = self.catalog_ftp_account
            password = self.catalog_ftp_password

            print(host, ftp_port, username, password)

            f = ftp()
            f.encoding = "utf-8"
            f.connect(host, ftp_port)
            f.login(username, password)
            f.set_pasv(0)

            return {"result": True, "data": f}
        except Exception as e:
            print("connect_ftp_server failed\n", str(e))
            return {"result": False, "data": "connect_ftp_server failed\n" + str(e)}

    def move_to_ftp_server(self, dir_list, f):
        try:
            bufsize = 1024
            print(self.catalog_local_path)
            print(self.catalog_ftp_server_path)
            i = 1
            pass_list = ['.layout.ini', '.level1.mds']
            for dir_path in dir_list:
                # progress_data = str(i / len(dir_list) * 89 + 10)[:5] + "%"
                # print(progress_data)
                if dir_path[dir_path.rfind('/') + 1:] in pass_list:
                    print("======================")
                    print(dir_path[dir_path.rfind('/') + 1:])
                    print("======================")
                    pass
                elif dir_path[0:2] == "M_" or dir_path[0:2] == "D_":
                    print("+++" *10)
                    ftp_folder_path = dir_path[2:].replace(self.catalog_local_path, self.catalog_ftp_server_path)
                    print(ftp_folder_path)
                    print("+++" * 10)
                    # print(ftp_folder_path)
                    f.mkd(ftp_folder_path)
                elif dir_path[0:2] == "F_":
                    fp = open(dir_path[2:], 'rb')
                    remote_path = dir_path[2:].replace(self.catalog_local_path, self.catalog_ftp_server_path)
                    # print(remote_path)
                    f.storbinary('STOR ' + remote_path, fp, bufsize)
                    fp.close()

                # convert_status.objects.filter(lot_id=self.lot_id, stage_id="5").update(progress=progress_data)
                i += 1

            f.set_debuglevel(0)
            f.quit

            return {"result": True, "data": "success"}
        except Exception as e:
            traceback.print_exc()
            print("move_to_ftp_server failed\n", str(e))
            return {"result": False, "data": "move_to_ftp_server failed\n" + str(e)}

    def connect_machine(self):
        try:
            # 获取ftp连接参数，如IP HOST username pwd
            # ftp = ftplib.FTP
            _o = tool_maintain.objects.get(exptool=self.exp_tool)
            # host = _o.ip
            # ftp_port = 21
            # username = _o.account
            # password = _o.password
            #
            # print(host, ftp_port, username, password)
            #
            # f = ftp()
            # f.encoding = "utf-8"
            # f.connect(host, ftp_port) # 连接
            # f.login(username, password) # 登录
            # f.set_pasv(0)
            _sftp = SSHManager(_o.ip, _o.account, _o.password)

            return {"result": True, "data": _sftp}
        except Exception as e:
            print("connect_machine failed\n", str(e))
            return {"result": False, "data": "connect_machine failed\n" + str(e)}

    def move_to_machine(self, dir_list, f):
        try:
            log.info(self.catalog_local_path)
            tool_maintain_path = tool_maintain.objects.get(exptool=self.exp_tool).path # 获取路径 路径为页面配置的基础路径
            catalog_machine_path = os.path.join(tool_maintain_path,
                                                # Constant.NEW_CATALOG_MACHINE_DICT[self.info_tree_tool_id]) + '/'
                                                Constant.CATALOG_MACHINE_DICT[self.info_tree_tool_id]) + '/' # 路径拼接，为准确路径
            log.info(tool_maintain_path+'|||'+catalog_machine_path)
            i = 1
            pass_list = ['.layout.ini', '.level1.mds']
            for dir_path in dir_list:
                close_old_connections()
                log.info("dir_path =" + dir_path)
                if dir_path[dir_path.rfind('/') + 1:] in pass_list:
                    log.info(dir_path[dir_path.rfind('/') + 1:])
                    pass
                # 若路径最后指向为文件夹，则通过ftp创建文件夹
                elif dir_path[0:2] == "M_" or dir_path[0:2] == "D_":
                    log.info('move to machine D or M')
                    ftp_folder_path = dir_path[2:].replace(self.catalog_local_path, tool_maintain_path) # 将本地路径替换为机台上的路径
                    log.info(ftp_folder_path)
                    # file_path_list = [x for x in ftp_folder_path.split('/') if x != '']
                    # cd_path = os.path.join(*file_path_list[:-1])
                    # dir_name = file_path_list[-1]
                    # f.cwd(cd_path)
                    f._mkdir(ftp_folder_path)
                # 创建文件夹结束
                # 若路径最后指向为文件，则ftp上传
                elif dir_path[0:2] == "F_":
                    print('move to machine F')
                    # fp = open(dir_path[2:], 'rb')
                    remote_path = dir_path[2:].replace(self.catalog_local_path, tool_maintain_path)  # 将本地路径替换为机台上的路径
                    log.info(remote_path)
                    # f.storbinary('STOR ' + remote_path, fp, bufsize)
                    f._upload_file(dir_path[2:], remote_path)
                    # fp.close()
                # 上传文件结束

                i += 1

            # f.set_debuglevel(0)
            f.__del__()

            return {"result": True, "data": "success"}
        except Exception as e:
            print("move_to_machine failed\n", str(e))
            traceback.print_exc()
            return {"result": False, "data": "move_to_machine failed\n" + str(e)}
