import logging
import traceback
from datetime import datetime

from django.db import transaction
from django.db.models import Q
from retrying import retry

from Mask_DP.settings import MES_USER
from catalog.models import tool_maintain
from jdv.models import lot_info, lot_op_record, mes_operation_info
from making.models import convert_status
from tooling_form.models import tapeout_info, boolean_info, product_info
from utilslibrary.mes_webservice.mes_base_webservice import MES_TxLotListInq, MES_TxOpeStartReq, MES_OpeStartCancelReq, \
    MES_OpeCompWithDataReq, MES_TxExTIPLayerDataParmUpdateExptool, MES_TxExTIPLayerDataParmSetReq, \
    MES_TxExTIPLayerDataParmInq, TxRouteOperationListInq__160, MES_TxEqpInfoInq, MES_TxExTIPLayerDataParmDeleteLot, \
    MES_TxOpeLocateReq, MES_TxLoadingLotRpt, MES_TxUnloadingLotRpt, MES_TxExTIPLayerDataParmSetReqForInherit, \
    MES_TxExTIPLayerDataParmAddSapOrder, MES_TxExTIPLayerDataParmChangeB_P, MES_TxExTIPLayerDataParmInqForLotID, \
    MES_TxExTIPLayerDataParmInsertB_P, MES_TxExTIPLayerDataParmBackUpInq
from utilslibrary.mes_webservice.mes_demo.MES_TxRunningHoldReq import MES_TxRunningHoldReq
from utilslibrary.mes_webservice.mes_utils import get_tapeout_type, set_lot_state, mes_sign_password
from utilslibrary.system_constant import Constant
from utilslibrary.utils.date_utils import getDateStr, getMESDateStr

log = logging.getLogger('log')

ppt_user = MES_USER
# ppt_user = {'userID': 'DP_SYS', 'password': 'es1xttAQ'}
equipmentID = 'MDCOM01'


def gen_lots(tip_no):
    """调用mes生成lot_id"""
    in_param = {'Action': 'Insert', 'tipNO': tip_no}  # Insert/Update/Delete/ResetCnt
    try:
        tapeout_info_list = tapeout_info.objects.filter(tip_no=tip_no, t_o='Y', is_delete=0)
        print(tapeout_info_list)
        p = product_info.objects.get(tip_no=tip_no)
        t_list = []
        x_num = 1
        for i, t in enumerate(tapeout_info_list):
            if inherit_lots(tip_no, t.mask_name) == 0:
                lot = lot_info.objects.filter(tip_no=tip_no, mask_name=t.mask_name).first()
                t_dict = {}
                t_dict['partName'] = t.mask_name
                # lot_list = lot_info.objects.filter(mask_name=t.mask_name)
                t_dict['seq'] = get_seq(tip_no, t.mask_name) + x_num
                tone = boolean_info.objects.filter(mask_name=t.mask_name).first().tone
                t_dict['tone'] = tone
                t_dict['tipTech'] = p.tech_process
                t_dict['grade'] = t.grade
                t_dict['productType'] = t.mask_type
                t_dict['customerID'] = p.customer
                t_dict['purpose'] = 'Tip'
                t_dict['lotCreatedStatus'] = 'Init'
                t_dict['claimUserID'] = 'DP'
                t_dict['claimTimeStamp'] = getMESDateStr()
                t_dict['orderType'] = get_tapeout_type(p.mask_vendor, p.customer)
                t_dict['paramExpTool'] = lot.exp_tool
                t_dict['paramBlankCode'] = lot.blank_code
                t_dict['paramPellicleCode'] = lot.pellicle_code
                t_dict['paramDesignRule'] = p.design_rule
                t_dict['paramGrade'] = t.grade
                t_dict['paramTone'] = tone
                t_dict['paramProductType'] = t.mask_type
                t_dict['paramDeliveryFab'] = p.delivery_fab
                t_dict['paramWaveLength'] = lot.wavelength
                t_list.append(t_dict)
                x_num += 1
        print("++++++++" + str(len(t_list)))
        if len(t_list) > 0:
            in_param['strExTIPLayerDataInfoSequence'] = t_list
            result = MES_TxExTIPLayerDataParmSetReq(ppt_user, in_param)
            message = result.strResult.messageText
            if result.strResult.returnCode == '0':  # 调用成功
                return True, message
            else:
                return False, message
        else:
            return True, "Inherit Lot Success"
    except Exception as e:
        log.error(traceback.format_exc())
        print(traceback.format_exc())
        return False, str(e)


def get_seq(tip_no, mask_name):
    """获取lot生成需要的seq"""
    seq = 0
    result = MES_TxExTIPLayerDataParmInq(ppt_user, tip_no, None)
    if result.strResult.returnCode == '0':  # 请求成功
        if result.strExTIPLayerData != '':
            seq = len(result.strExTIPLayerData.item[0].strExTIPLayerDataInfoSequence.item)
            # for layerData in result.strExTIPLayerData.item:
            #     if layerData.tipNO == tip_no:
            #         seq = len(layerData.strExTIPLayerDataInfoSequence.item) + 1
    return seq


def inherit_lots(tip_no, mask_name):
    """继承之前的lot，如果有多条lot存在，都继承，且更新lot相关信息"""
    num = 0
    lot = lot_info.objects.get(tip_no=tip_no, mask_name=mask_name)
    result = MES_TxExTIPLayerDataParmInq(ppt_user, tip_no, mask_name)
    message = result.strResult.messageText
    log.info("tip_no=" + tip_no + ", mask_name=" + mask_name + "继承lot方法查询MES返回信息为：" + message)
    if result.strResult.returnCode == '0':  # 请求成功
        if result.strExTIPLayerData != '':
            for layerData in result.strExTIPLayerData.item:
                for layerDataInfo in layerData.strExTIPLayerDataInfoSequence.item:
                    lot_created_status = layerDataInfo.lotCreatedStatus
                    res = layerDataInfo.result
                    log.info("Inherit Lot 查询lot返回layerDataInfo.result=" + str(res))
                    lot_id = layerDataInfo.lotID
                    if lot_created_status == "Pass":
                        if lot_id:  # 存在lot，保存之前的lot到数据库
                            if lot.lot_id != lot_id and lot.status == 3:
                                lot.id = None
                                lot.lot_id = lot_id
                                lot.status = 3
                                lot.status_dec = "Inherit Lot[2]"
                                lot.save()
                                num += 1
                                log.info("Inherit Lot [2]插入数据库成功lot_id=" + lot_id)
                                convert_status.objects.filter(tip_no=lot.tip_no, mask_name=lot.mask_name). \
                                    update(lot_id=lot_id)
                            else:
                                lot.lot_id = lot_id
                                lot.status = 3
                                lot.status_dec = "Inherit Lot[1]"
                                lot.save()
                                num += 1
                                log.info("Inherit Lot [1]插入数据库成功lot_id=" + lot_id)
                                convert_status.objects.filter(tip_no=lot.tip_no, mask_name=lot.mask_name). \
                                    update(lot_id=lot_id)
        # 更新MES中lot信息
        if num > 0:
            p = product_info.objects.get(tip_no=tip_no)
            t = tapeout_info.objects.get(tip_no=tip_no, mask_name=mask_name, t_o='Y', is_delete=0)
            info = {'tipNO': tip_no, 'partName': mask_name}
            tone = boolean_info.objects.filter(mask_name=mask_name).first().tone
            info['tone'] = tone
            info['tipTech'] = p.tech_process
            info['grade'] = t.grade
            info['productType'] = t.mask_type
            info['customerID'] = p.customer
            info['purpose'] = 'Tip'
            info['claimUserID'] = 'DP'
            info['claimTimeStamp'] = getMESDateStr()
            info['orderType'] = get_tapeout_type(p.mask_vendor, p.customer)
            info['paramExpTool'] = lot.exp_tool
            info['paramBlankCode'] = lot.blank_code
            info['paramPellicleCode'] = lot.pellicle_code
            info['paramDesignRule'] = p.design_rule
            info['paramGrade'] = t.grade
            info['paramTone'] = tone
            info['paramProductType'] = t.mask_type
            info['paramDeliveryFab'] = p.delivery_fab
            info['paramWaveLength'] = lot.wavelength
            result = MES_TxExTIPLayerDataParmSetReqForInherit(ppt_user, info)
            message = result.strResult.messageText
            if result.strResult.returnCode == '0':  # 调用成功
                log.info("Inherit Lot更新mes成功，message=" + message)
            else:
                log.error("Inherit Lot更新mes失败，message=" + message)
    return num


def get_lots():
    """获取生成的lot_id的task方法"""
    log.info("开始执行lotID查询方法")
    lot_list = lot_info.objects.filter(status=1)  # 获取状态为1的记录
    for lot in lot_list:
        try:
            result = MES_TxExTIPLayerDataParmInq(ppt_user, lot.tip_no, lot.mask_name)
            message = result.strResult.messageText
            if result.strResult.returnCode == '0':  # 请求成功
                for layerData in result.strExTIPLayerData.item:
                    for layerDataInfo in layerData.strExTIPLayerDataInfoSequence.item:
                        lot_created_status = layerDataInfo.lotCreatedStatus
                        res = layerDataInfo.result
                        lot_id = layerDataInfo.lotID
                        if lot_created_status == 'Pass':
                            if lot_id:
                                lot.status = 3
                                lot.lot_id = lot_id
                                lot.status_dec = lot.status_dec + "|" + lot_created_status
                                lot.save()
                                # 更新convert_status数据
                                convert_status.objects.filter(tip_no=lot.tip_no, mask_name=lot.mask_name). \
                                    update(lot_id=lot_id)
                            else:
                                lot.status = 2
                                lot.status_dec = lot.status_dec + "|" + lot_created_status
                                lot.save()
                        elif 'ERR' in lot_created_status:
                            log.info("查询lot_id获取到的lot_created_status为：" + lot_created_status + ":" + res)
                            lot.status = 2
                            lot.status_dec = lot.status_dec + "|" + lot_created_status + ":" + res
                            lot.save()
                        else:  # 其余状态先更新数据库
                            log.info("查询lot_id获取到的lot_created_status为：" + lot_created_status)
                            if lot_id:
                                lot.lot_id = lot_id
                            lot.status_dec = lot_created_status
                            lot.save()

            else:
                log.info("查询lot_id：" + message)
                lot.status = 2
                lot.status_dec = lot.status_dec + "|" + message
                lot.save()
        except Exception as e:
            log.error("执行获取lot_id的请求出错" + str(e))
            lot.status = 2
            lot.status_dec = lot.status_dec + "|" + str(e)
            lot.save()


def monitor_mes_new_lot():
    """监听MES端手工新起的lot"""
    log.info("开始执行监听MES端新起lot的方法")
    try:
        lot_list = lot_info.objects.filter(status=3)
        for lot in lot_list:
            tip_no = lot.tip_no
            mask_name = lot.mask_name
            result = MES_TxExTIPLayerDataParmBackUpInq(ppt_user, tip_no, mask_name)
            message = result.strResult.messageText
            log.info(message)
            if result.strResult.returnCode == '0':  # 请求成功
                if result.strExTIPLayerData != '':
                    for layerData in result.strExTIPLayerData.item:
                        for layerDataInfo in layerData.strExTIPLayerDataInfoSequence.item:
                            # lot_created_status = layerDataInfo.lotCreatedStatus
                            res = layerDataInfo.result
                            lot_id = layerDataInfo.lotID
                            if 'nil' not in str(lot_id):
                                exist_lot = lot_info.objects.filter(lot_id=lot_id)
                                if not exist_lot:  # 如果之前不存在这笔lot，则插入新数据
                                    log.info("lot_id=" + lot_id + "为mes新起的lot，执行插入数据库的操作")
                                    old_lot = lot_info.objects.filter(tip_no=tip_no, mask_name=mask_name).first()
                                    old_lot.pk = None
                                    old_lot.lot_id = lot_id
                                    old_lot.dispatch_flag = 0
                                    old_lot.ready_date = datetime.now()
                                    old_lot.save()
                                    log.info("lot插入完毕")
    except Exception as e:
        log.error("Error:" + str(e))
        log.error(traceback.print_exc())


def mes_op_locate(lot_id, op_id, op_num, remark):
    """将站点往回拉的接口"""
    try:
        lot = lot_info.objects.get(lot_id=lot_id)
        if lot:
            route_id = lot.mes_route_id
            old_op_num = lot.mes_operation_number
            result = MES_TxOpeLocateReq(ppt_user, lot_id, route_id, old_op_num, op_id, op_num, remark)
            if result.strResult.returnCode == '0':  # 执行成功
                message = result.strResult.messageText
                log.info("lot_id=" + lot_id + "执行【op_locate】方法过站到[" + op_id + "]成功")
                op_record = lot_op_record.objects.create(lot_id=lot_id, equipment_id="",
                                                         dp_operation=op_id,
                                                         op_operation_type=4, op_operation='op_locate',
                                                         op_operation_status
                                                         =1, op_operationt_date=getDateStr())
                return True, message
        else:
            log.error("lot_id=" + lot_id + "执行【op_locate】方法未查询到对应的lot_info信息")
            return False, "未查询到对应的lot_info"
    except Exception as e:
        log.error("lot_id=" + lot_id + "执行【op_locate】方法出现错误:" + str(e))
        return False, str(e)


def mes_real_op_start(mm_user, lot_id, dp_operation):
    """真实站点opstart需要先调用loadingLot"""
    lot = lot_info.objects.get(lot_id=lot_id)
    tool_id = tool_maintain.objects.get(exptool=lot.exp_tool).tool_id
    equipment_id = tool_id
    cassette_id = lot.mes_carrier_id
    result = MES_TxLoadingLotRpt(mm_user, equipment_id, cassette_id, "DP catalog op start")
    message = result.strResult.messageText
    log.info(lot_id + "[op_start]执行loadinglot接口返回" + message)
    if result.strResult.returnCode == '0':  # loading_lot执行成功
        flag = mes_op_start(lot_id, dp_operation)
        if flag:  # op-start执行成功
            return flag, "op_start success"
        else:
            return flag, "op_start false"
    else:
        return False, "LoadingLot false: " + message


def mes_real_op_start_cancel(mm_user, lot_id, dp_operation):
    """真实站点op_start_cancel需要后调用unloadingLot"""
    lot = lot_info.objects.get(lot_id=lot_id)
    tool_id = tool_maintain.objects.get(exptool=lot.exp_tool).tool_id
    equipment_id = tool_id
    cassette_id = lot.mes_carrier_id
    flag = mes_op_start_cancel(lot_id, dp_operation)
    if flag:  # op-start-cancel执行成功
        # 执行UnloadingLot方法
        result = MES_TxUnloadingLotRpt(mm_user, equipment_id, cassette_id, "DP catalog op start cancel")
        message = result.strResult.messageText
        log.info(lot_id + "[op_start_cancel]执行unloadinglot接口返回" + message)
        if result.strResult.returnCode == '0':  # loading_lot执行成功
            return True, "op_start_cancel success"
        else:
            return False, "UnloadingLot false : " + message
    else:
        return flag, "op_start_cancel false"


def mes_real_op_comp(mm_user, lot_id, dp_operation):
    """真实站点op_comp需要后调用unloadingLot"""
    lot = lot_info.objects.get(lot_id=lot_id)
    tool_id = tool_maintain.objects.get(exptool=lot.exp_tool).tool_id
    equipment_id = tool_id
    cassette_id = lot.mes_carrier_id
    flag = mes_op_comp(lot_id, dp_operation)
    if flag:  # op-comp执行成功
        # 执行UnloadingLot方法
        result = MES_TxUnloadingLotRpt(mm_user, equipment_id, cassette_id, "DP catalog op comp")
        message = result.strResult.messageText
        log.info(lot_id + "[op_comp]执行unloadinglot接口返回" + message)
        if result.strResult.returnCode == '0':  # loading_lot执行成功
            return True, "op_comp success"
        else:
            return False, "UnloadingLot false : " + message
    else:
        return flag, "op_comp false"


def mes_op_start(lot_id, dp_operation):
    """op_start方法"""
    lot = lot_info.objects.get(lot_id=lot_id)
    if lot.mes_operation_number >= "200.200":
        tool_id = tool_maintain.objects.get(exptool=lot.exp_tool).tool_id
        equipment_id = tool_id
    else:
        equipment_id = equipmentID
    o_r = lot_op_record.objects.filter(lot_id=lot_id, equipment_id=equipment_id, dp_operation=dp_operation,
                                       op_operation_type=1, op_operation='op_start', op_operation_status=1)
    if o_r:
        return False
    op_record = lot_op_record.objects.create(lot_id=lot_id, equipment_id=equipment_id, dp_operation=dp_operation,
                                             op_operation_type=1, op_operation='op_start', op_operation_status
                                             =0, op_operationt_date=getDateStr())
    if not lot:
        log.error("未查询到lot_id=" + lot_id + "对应的Lot信息")
        message = "未查询到lot_id=" + lot_id + "对应的Lot信息"
        op_record.op_operation_message = message
        op_record.save()
        return False
    # 判断operationID是否一致
    # if lot.mes_operation_id != dp_operation:
    #     log.error("operation_id不一致, lot当前站点为%s,要过站的站点为%s" % (lot.mes_operation_id, dp_operation))
    #     message = "operation_id不一致, lot当前站点为%s,要过站的站点为%s" % (lot.mes_operation_id, dp_operation)
    #     op_record.op_operation_message = message
    #     op_record.save()
    #     return False
    cassette_id = lot.mes_carrier_id
    if not cassette_id:
        log.error("未查询到lot_id=" + lot_id + "对应的cassette_id")
        message = "未查询到lot_id=" + lot_id + "对应的cassette_id"
        op_record.op_operation_message = message
        op_record.save()
        # cassette_id = str(lot_id).split('.')[0]
        return False
    # equipment_id = lot.mes_equipment_id
    try:
        result = MES_TxOpeStartReq(ppt_user, equipment_id, cassette_id, dp_operation)
        message = result.strResult.messageText
        transactionID = result.strResult.transactionID
        if result.strResult.returnCode == '0':  # 执行成功
            controlJobID = result.controlJobID.identifier
            operationID = result.strStartCassette.item[0].strLotInCassette.item[0].strStartOperationInfo. \
                operationID.identifier
            operationNumber = result.strStartCassette.item[0].strLotInCassette.item[0].strStartOperationInfo. \
                operationNumber
            # passCount = result.strStartCassette.item[0].strLotInCassette.item[0].strStartOperationInfo.passCount
            op_record.mes_operation = operationNumber + ':' + operationID
            op_record.control_job_id = controlJobID
            op_record.op_operation_status = 1
            op_record.mes_transaction_id = transactionID
            op_record.op_operation_message = message
            op_record.save()
            return True
        else:
            log.error("执行op_start方法返回" + message)
            op_record.op_operation_message = message
            op_record.save()
            return False
    except Exception as e:
        log.error("执行op_start方法出错" + str(e))
        log.error(traceback.print_exc())
        op_record.op_operation_message = str(e)
        op_record.save()
        return False


def mes_op_start_cancel(lot_id, dp_operation):
    """opStartCancel取消opStart操作"""
    lot = lot_info.objects.get(lot_id=lot_id)
    if lot.mes_operation_number >= "200.200":
        tool_id = tool_maintain.objects.get(exptool=lot.exp_tool).tool_id
        equipment_id = tool_id
    else:
        equipment_id = equipmentID
    op_record = lot_op_record.objects.create(lot_id=lot_id, equipment_id=equipment_id, dp_operation=dp_operation,
                                             op_operation_type=3, op_operation='op_start_cancel', op_operation_status
                                             =0, op_operationt_date=getDateStr())
    if not lot:
        log.error("未查询到lot_id=" + lot_id + "对应的lot_info信息")
        message = "未查询到lot_id=" + lot_id + "对应的lot_info信息"
        op_record.op_operation_message = message
        op_record.save()
        return False
    # equipment_id = lot.mes_equipment_id
    try:
        op_r = lot_op_record.objects.filter(lot_id=lot_id, dp_operation=dp_operation, op_operation_type=1,
                                            op_operation_status=1).first()
        if not op_r:
            log.error("未查询到lot_id=" + lot_id + "对应的op_record信息")
            message = "未查询到lot_id=" + lot_id + "对应的op_record信息"
            op_record.op_operation_message = message
            op_record.save()
            return False
        control_job_id = op_r.control_job_id
        result = MES_OpeStartCancelReq(ppt_user, equipment_id, control_job_id)  # 访问MES接口
        message = result.strResult.messageText
        transactionID = result.strResult.transactionID
        if result.strResult.returnCode == '0':
            operationID = result.strStartCassette.item[0].strLotInCassette.item[0].strStartOperationInfo. \
                operationID.identifier
            operationNumber = result.strStartCassette.item[0].strLotInCassette.item[0].strStartOperationInfo. \
                operationNumber
            op_record.mes_operation = operationNumber + ':' + operationID
            op_record.control_job_id = control_job_id
            op_record.op_operation_status = 1
            op_record.mes_transaction_id = transactionID
            op_record.op_operation_message = message
            op_record.save()
            op_r.op_operation_status = 3
            op_r.save()
            return True
        else:
            log.error("执行op_start_cancel方法返回" + message)
            op_record.op_operation_message = message
            op_record.save()
            return False
    except Exception as e:
        log.error("执行op_start_cancel方法出错" + str(e))
        log.error(traceback.print_exc())
        op_record.op_operation_message = str(e)
        op_record.save()
        return False


def mes_op_comp(lot_id, dp_operation):
    """op_comp操作"""
    lot = lot_info.objects.get(lot_id=lot_id)
    if lot.mes_operation_number >= "200.200":
        tool_id = tool_maintain.objects.get(exptool=lot.exp_tool).tool_id
        equipment_id = tool_id
    else:
        equipment_id = equipmentID
    op_record = lot_op_record.objects.create(lot_id=lot_id, equipment_id=equipment_id, dp_operation=dp_operation,
                                             op_operation_type=2, op_operation='op_comp', op_operation_status=0,
                                             op_operationt_date=getDateStr())
    if not lot:
        log.error("未查询到lot_id=" + lot_id + "对应的lot_info信息")
        message = "未查询到lot_id=" + lot_id + "对应的lot_info信息"
        op_record.op_operation_message = message
        op_record.save()
        return False
    # equipment_id = lot.mes_equipment_id
    try:
        op_r = lot_op_record.objects.filter(lot_id=lot_id, dp_operation=dp_operation, op_operation_type=1,
                                            op_operation_status=1).first()
        if not op_r:
            log.error("未查询到lot_id=" + lot_id + "对应的op_record信息")
            return False
        control_job_id = op_r.control_job_id
        result = MES_OpeCompWithDataReq(ppt_user, equipment_id, control_job_id)
        message = result.strResult.messageText
        transactionID = result.strResult.transactionID
        if result.strResult.returnCode == '0':
            op_record.control_job_id = control_job_id
            op_record.op_operation_status = 1
            op_record.mes_transaction_id = transactionID
            op_record.op_operation_message = message
            op_record.save()
            op_r.op_operation_status = 3
            op_r.save()
            return True
        else:
            log.error("执行op_comp方法返回" + message)
            op_record.op_operation_message = message
            op_record.save()
            return False
    except Exception as e:
        log.error(traceback.print_exc())
        log.error("执行op_start_cancel方法出错" + str(e))
        log.error(traceback.print_exc())
        op_record.op_operation_message = str(e)
        op_record.save()
        return False


def mes_op_process(lot_id, dp_operation):
    """完整过站流程"""
    if mes_op_start(lot_id, dp_operation):  # 执行opStart成功
        if mes_op_comp(lot_id, dp_operation):  # 执行opComp成功
            return True
        else:
            mes_op_start_cancel(lot_id, dp_operation)
            return False
    else:
        log.error("op_process执行op_start失败")
        return False


def get_wip_for_task():
    """定时获取lot_id对应的最新状态"""
    log.info("执行get_wip任务")
    try:
        lot_list = lot_info.objects.filter(status=3)  # 获取需要更新站点的lot信息
        log.info("get_wip_for_task获取到%d条记录，开始查询" % lot_list.count())
        for lot in lot_list:
            lot_id = lot.lot_id
            result = MES_TxLotListInq(ppt_user, lot_id, False)
            if lot.mes_get_wip_result != result:  # 更新执行结果
                lot.mes_get_wip_result = result
                lot.mes_get_wip_message = result.strResult.messageText
                lot.save()
                if result.strResult.returnCode == '0':  # 执行成功
                    for item in result.strLotListAttributes.item:
                        lot.mes_lot_type = item.lotType
                        lot.mes_lot_status = item.lotStatus
                        lot = set_lot_state(lot, item.strLotStatusList.item)
                        lot.mes_bank_id = item.bankID.identifier
                        lot.mes_order_number = item.orderNumber
                        lot.mes_customer_code = item.customerCode
                        lot.mes_product_id = item.productID.identifier
                        lot.mes_last_claimed_timestamp = item.lastClaimedTimeStamp
                        lot.mes_due_timestamp = item.dueTimeStamp
                        lot.mes_route_id = item.routeID.identifier
                        lot.mes_operation_number = item.operationNumber
                        lot.mes_total_wafer_count = item.totalWaferCount
                        lot.mes_bank_in_required_flag = item.bankInRequiredFlag
                        lot.mes_control_use_state = item.controlUseState
                        lot.mes_used_count = item.usedCount
                        lot.mes_completion_timestamp = item.completionTimeStamp
                        lot.mes_lot_family_id = item.lotFamilyID.identifier
                        lot.mes_product_request_id = item.productRequestID.identifier
                        lot.mes_sub_lot_type = item.subLotType
                        lot.mes_lot_owner_id = item.lotOwnerID.identifier
                        lot.mes_required_cassette_category = item.requiredCassetteCategory
                        lot.mes_backup_processing_flag = item.strLotBackupInfo.backupProcessingFlag
                        lot.mes_current_location_flag = item.strLotBackupInfo.currentLocationFlag
                        lot.mes_transfer_flag = item.strLotBackupInfo.transferFlag
                        lot.mes_carrier_id = item.carrierID.identifier
                        lot.mes_equipment_id = item.equipmentID.identifier
                        lot.mes_hold_reason_code_id = item.holdReasonCodeID.identifier
                        lot.mes_sorter_job_exist_flag = item.sorterJobExistFlag
                        lot.mes_in_post_process_flag_of_cassette = item.inPostProcessFlagOfCassette
                        lot.mes_in_post_process_flag_of_lot = item.inPostProcessFlagOfLot
                        lot.mes_inter_fab_xfer_state = item.interFabXferState
                        lot.mes_bonding_group_id = item.bondingGroupID
                        lot.mes_auto_dispatch_controller_flag = item.autoDispatchControlFlag
                        lot.mes_eqp_monitor_job_id = item.eqpMonitorJobID.identifier
                        lot.mes_operation_id = item.operationID.identifier
                        lot.mes_pd_type = item.pdType
                        lot.mes_schedule_mode = item.scheduleMode
                        lot.mes_plan_start_timestamp = item.planStartTimeStamp
                        lot.mes_priority_class = item.priorityClass
                        lot.mes_lot_info_change_flag = item.lotInfoChangeFlag
                        lot.save()
                        # 自动过站，过TPC跟RFL站点
                        if item.operationID.identifier == Constant.MES_OPERATION_ID_TPC:
                            if mes_op_process(lot_id, Constant.MES_OPERATION_ID_TPC):
                                mes_op_process(lot_id, Constant.MES_OPERATION_ID_RFL)
                        # if item.operationID.identifier == Constant.MES_OPERATION_ID_RFL:
                        #     mes_op_process(lot_id, Constant.MES_OPERATION_ID_RFL)
    except Exception as e:
        traceback.print_exc()
        log.error("get_wip_for_task执行出错" + str(e))


def cross_operations():
    """自动过站操作"""
    log.info("开始执行自动过站操作")
    lot_list = lot_info.objects.filter(status=3, mes_operation_id__isnull=False)
    for lot in lot_list:
        tip_no = lot.tip_no
        mask_name = lot.mask_name
        lot_id = lot.lot_id
        result = MES_TxLotListInq(ppt_user, lot_id, False)
        if result.strResult.returnCode == '0':  # 执行成功
            for item in result.strLotListAttributes.item:
                operation_id = item.operationID.identifier
                # DEV站点 在lotID的fracture执行完进行过站
                if operation_id == Constant.MES_OPERATION_ID_DVC:
                    c_s_list = convert_status.objects.filter(~Q(status=Constant.CONVERT_STATUS_DONE), tip_no=tip_no,
                                                             mask_name=mask_name, stage="Fracture")
                    if c_s_list.count() == 0:  # Fracture全都done
                        log.info("【DVC】tip_no=%s,mask_name=%s,lot_id=%s开始执行【%s】过站" % (tip_no, mask_name, lot_id,
                                                                                      Constant.MES_OPERATION_ID_DVC))
                        dvc_flag = mes_op_process(lot_id, Constant.MES_OPERATION_ID_DVC)
                        log.info("【DVC】过站:" + str(dvc_flag))
                # jvw过站
                if operation_id == Constant.MES_OPERATION_ID_JVW:
                    if lot.release_status:  # 点击jdv release按钮
                        log.info("【JVW】tip_no=%s,mask_name=%s,lot_id=%s开始执行【%s】过站" % (tip_no, mask_name, lot_id,
                                                                                      Constant.MES_OPERATION_ID_JVW))
                        jvw_flag = mes_op_process(lot_id, Constant.MES_OPERATION_ID_JVW)
                        log.info("【JVW】过站:" + str(jvw_flag))
                # odr站点过站
                if operation_id == Constant.MES_OPERATION_ID_ODR:
                    if lot.payment_status:  # 点击payment check按钮
                        log.info("【ODR】tip_no=%s,mask_name=%s,lot_id=%s开始执行【%s】过站" % (tip_no, mask_name, lot_id,
                                                                                      Constant.MES_OPERATION_ID_ODR))
                        odr_flag = mes_op_process(lot_id, Constant.MES_OPERATION_ID_ODR)
                        log.info("【ODR】过站" + str(odr_flag))

                # DIS站点过站
                if operation_id == Constant.MES_OPERATION_ID_DIS:
                    if lot.dispatch_flag:  # 点击dispatch按钮
                        log.info("【DIS】tip_no=%s,mask_name=%s,lot_id=%s开始执行【%s】过站" % (tip_no, mask_name, lot_id,
                                                                                      Constant.MES_OPERATION_ID_DIS))
                        dis_flag = mes_op_process(lot_id, Constant.MES_OPERATION_ID_DIS)
                        log.info("【DIS】过站" + str(dis_flag))


def update_exptool(mm_user, tip_no, mask_name, lot_id, exptool):
    """通知mes更新exptool参数"""
    try:
        result = MES_TxExTIPLayerDataParmUpdateExptool(mm_user, tip_no, mask_name, lot_id, exptool)
        if result == '0':
            return True
        else:
            return False
    except Exception as e:
        log.error("update_exptool执行出错" + str(e))
        log.error(traceback.print_exc())
        return False


def add_order_num(tip_no, mask_name, production_order):
    """通知mes更新DP_ORDER_NUM参数"""
    flag = 0
    try:
        q_result = MES_TxExTIPLayerDataParmInq(ppt_user, tip_no, mask_name)
        message = q_result.strResult.messageText
        if q_result.strResult.returnCode == '0':  # 请求成功
            for layerData in q_result.strExTIPLayerData.item:
                for layerDataInfo in layerData.strExTIPLayerDataInfoSequence.item:
                    # lot_created_status = layerDataInfo.lotCreatedStatus
                    # res = layerDataInfo.result
                    lot_id = layerDataInfo.lotID
                    result = MES_TxExTIPLayerDataParmAddSapOrder(ppt_user, tip_no, mask_name, production_order, lot_id)
                    if result != '0':
                        flag = flag + 1
        if flag > 0:
            return False
        else:
            return True
    except Exception as e:
        log.error("更新mes_order_num执行出错" + str(e))
        log.error(traceback.print_exc())
        return False


def change_blank_pellicle(mm_user, tip_no, mask_name, lot_id, blank_code=None, pellicle_code=None):
    """通知mes更新blank和pellicle"""
    try:
        result = MES_TxExTIPLayerDataParmChangeB_P(mm_user, tip_no, mask_name, lot_id, blank_code, pellicle_code)
        if result == '0':
            return True
        else:
            return False
    except Exception as e:
        log.error("更新mes_blank_pellicle执行出错" + str(e))
        log.error(traceback.print_exc())
        return False


def insert_blank_pellicle(mm_user, lot_type, lot_id, blank_code=None, pellicle_code=None):
    """插入blank_code和pellicle_code"""
    try:
        if lot_type == "p":
            # 根据LotID获取tip_no和mask_name
            result = MES_TxExTIPLayerDataParmInqForLotID(mm_user, lot_id)
            tip_no = result.strExTIPLayerData.item[0].tipNO
            mask_name = result.strExTIPLayerData.item[0].strExTIPLayerDataInfoSequence.item[0].partName
            if tip_no:
                r = MES_TxExTIPLayerDataParmChangeB_P(mm_user, tip_no, mask_name, lot_id, blank_code, pellicle_code)
                if r == '0':
                    return True
                else:
                    return False
            else:
                log.error("insert_blank_pellicle执行出错, tip_no未获取到" + tip_no)
                return False
        elif lot_type == "e":
            r = MES_TxExTIPLayerDataParmInsertB_P(mm_user, lot_id, blank_code, pellicle_code)
            if r == '0':
                return True
            else:
                return False
    except Exception as e:
        log.error("insert_blank_pellicle执行出错" + str(e))
        log.error(traceback.print_exc())
        return False



# def delete_lot(tip_no, mask_name):
#     """通知mes删除LOT"""
#     try:
#         result = MES_TxExTIPLayerDataParmDeleteLot(ppt_user, tip_no, mask_name)
#         if result == '0':
#             return True
#         else:
#             return False
#     except Exception as e:
#         log.error("delete_lot执行出错" + str(e))
#         log.error(traceback.print_exc())
#         return False


def mes_run_hold(lot_id, claimMemo):
    try:
        lot_info_list = lot_info.objects.filter(lot_id=lot_id).first()
        lot_op_list = lot_op_record.objects.filter(lot_id=lot_id).first()
        equipmentID = lot_op_list.equipment_id
        hold_reason_code_id = lot_info_list.mes_hold_reason_code_id
        controlJobID = lot_op_list.control_job_id
        MES_TxRunningHoldReq(ppt_user, equipmentID, hold_reason_code_id, controlJobID, claimMemo)
        log.info('mes_run_hold ok')
        return True
    except Exception as e:
        log.error(str(e))
        return False


def get_operation_info_list():
    log.info("执行查询operation_info的方法")
    route_id_list = ['BIN_01.1', 'PSM_01.1', 'OMOG_01.1']
    try:
        with transaction.atomic():
            mes_operation_info.objects.all().delete()
            for route_id in route_id_list:
                result = TxRouteOperationListInq__160(ppt_user, route_id)
                for op in result.strOperationNameAttributes.item:
                    o_i = mes_operation_info()
                    o_i.seq_no = op.seqno
                    o_i.route_id = op.routeID.identifier
                    o_i.operation_id = op.operationID.identifier
                    o_i.operation_number = op.operationNumber
                    o_i.stage_id = op.stageID.identifier
                    o_i.stage_group_id = op.stageGroupID.identifier
                    o_i.machines = op.machines
                    o_i.pdType = op.pdType
                    o_i.save()
            log.info("[operation_info update success]")
    except Exception as e:
        log.error("get_operation_info_list出错" + str(e))
