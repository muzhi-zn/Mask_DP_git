import logging
import traceback

from suds.client import Client
from suds.transport.http import HttpAuthenticated

from Mask_DP.settings import MES_USER
from utilslibrary.mes_webservice.mes_base_webservice import MES_TxLotListInqForReWork, \
    MES_TxExTIPLayerDataParmAddSapOrder, MES_TxOpeStartReq, MES_OpeCompWithDataReq

log = logging.getLogger('log')

SAP_URL = "http://qys4apqas:8000/sap/bc/srt/wsdl/flv_10002A111AD1/bndg_url/sap/bc/srt/rfc/sap/zpp00101/400/zpp00101/zpp00101?sap-client=400"
SAP_FAB = "2000"
EQP_ID = "MDCOM01"
OP_ID = "MRDODR.1"


def rework_order_job():
    """执行定时任务，查询返修订单"""

    try:
        transport = HttpAuthenticated(username="mask_dp", password="qxic666666")
        client = Client(SAP_URL, transport=transport)
        tr_order = client.factory.create("TableOfZpps001order")

        lot_list_result = MES_TxLotListInqForReWork(MES_USER, OP_ID)
        if lot_list_result.strResult.returnCode == '0':
            # 执行成功
            count = len(lot_list_result.strLotListAttributes.item)
            log.info("rework_order_job获取到" + str(count) + "条lot")
            for lot in lot_list_result.strLotListAttributes.item:
                lotID = lot.lotID.identifier
                tip_no = lot.orderNumber
                productID = lot.productID.identifier
                carrierID = lot.carrierID.identifier
                # cassetteID = lotID[0:8]
                log.info("rework_order_job开始处理...lot_id=" + str(lotID) + "|productID=" + str(productID))
                productID = str(productID)[:12]
                result = client.service.ZPp00101(productID, SAP_FAB, tr_order)
                log.info("rework_order_job请求SAP:" + str(result))
                if result.EReturn.Saprlt == "S":
                    # SAP请求成功
                    sap_order = result.TReorder.item[0]
                    aufnr = sap_order.Aufnr  # 生产订单
                    auart = sap_order.Auart  # 生产订单类型
                    matnr = sap_order.Matnr  # 产品编码
                    if aufnr:
                        # 更新MES中的DP_ORDER_NUM
                        r = MES_TxExTIPLayerDataParmAddSapOrder(MES_USER, tip_no, productID, aufnr, lotID)
                        if r == "0":
                            log.info("rework_order_job更新OrderNum成功,order_number=" + aufnr)
                            # 过order_check站点 MDCOM01
                            if pass_order_check(carrierID):
                                log.info("rework_order_job过站成功")
                            else:
                                log.error("rework_order_job过站失败")
                        else:
                            log.error("rework_order_job更新OrderNum失败,order_number=" + aufnr)
        else:
            log.error("rework_order_job获取list出错，错误信息：" + lot_list_result.strResult.messageText)
    except Exception as e:
        log.error("rework_order_job执行出错：" + str(e))
        log.error(traceback.print_exc())


def pass_order_check(cassetteID):
    """返修订单过站"""
    s_r = MES_TxOpeStartReq(MES_USER, EQP_ID, cassetteID, OP_ID)
    message = s_r.strResult.messageText
    transactionID = s_r.strResult.transactionID
    log.info("返修订单过站op_start请求MES返回：" + message)
    if s_r.strResult.returnCode == '0':  # 执行成功
        controlJobID = s_r.controlJobID.identifier
        log.info("返修订单过站op_start请求MES返回ControlJobID=" + controlJobID)
        # operationID = s_r.strStartCassette.item[0].strLotInCassette.item[0].strStartOperationInfo. \
        #     operationID.identifier
        # operationNumber = s_r.strStartCassette.item[0].strLotInCassette.item[0].strStartOperationInfo. \
        #     operationNumber
        c_r = MES_OpeCompWithDataReq(MES_USER, EQP_ID, controlJobID)
        message = c_r.strResult.messageText
        transactionID = c_r.strResult.transactionID
        log.info("返修订单过站op_start请求MES返回：" + message)
        if c_r.strResult.returnCode == '0':
            return True
        else:
            return False
