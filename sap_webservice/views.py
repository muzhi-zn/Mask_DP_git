# import json
# import logging
# from datetime import datetime
#
# from django.views.decorators.csrf import csrf_exempt
# from spyne import ServiceBase, rpc, Unicode, Application, Iterable, ComplexModel, Integer, Array
# from spyne.protocol.soap import Soap11
# from spyne.server.django import DjangoApplication
#
# from jdv.models import lot_info
# from sap_webservice.service.sd_service import SDService
# from utilslibrary.mes_webservice.mes_webservice import add_order_num
#
# log = logging.getLogger("log")
#
#
# class DpResponse(ComplexModel):
#     __namespace__ = 'dpResponse'
#     request_code = Unicode
#     request_message = Unicode
#     result_code = Unicode
#     result_message = Unicode
#
#
# class SDResponse(ComplexModel):
#     __namespace__ = 'sdResponse'
#     returnCode = Unicode
#     messageID = Unicode
#     messageText = Unicode
#     reasonText = Unicode
#     lotResult = Unicode
#
#
# class NoticeProductionOrder(ServiceBase):
#
#     @rpc(Unicode, Unicode, Unicode, Unicode, Unicode, Unicode, Unicode, Unicode,  _returns=DpResponse)
#     def notice_production_order(self, DWERK, CHARG, PRODID, AUFNR, AUART, KDAUF, KDPOS, MATNR):
#         dpResponse = DpResponse()
#         try:
#             dpResponse.request_code = "S"
#             dpResponse.request_message = "Request Successful"
#             log.info("SAP_Webservice接收到的参数为[DWERK]=%s, [CHARG]=%s, [PRODID]=%s, [AUFNR]=%s, "
#                      "[AUART]=%s, [KDAUF]=%s, [KDPOS]=%s, [MATNR]=%s" %
#                      (DWERK, CHARG, PRODID, AUFNR, AUART, KDAUF, KDPOS, MATNR))
#             mask_name = PRODID
#             production_order = AUFNR
#             # 查询已经生成lot_id的lot信息
#             tip_no_list = lot_info.objects.values("tip_no").filter(mask_name=mask_name,
#                                                                    status=3, is_delete=0).distinct()
#             if len(tip_no_list) > 0:
#                 for tip_no_dict in tip_no_list:
#                     tip_no = tip_no_dict['tip_no']
#                     # payment_check按钮未点击过，自动release
#                     lot_info.objects.filter(mask_name=mask_name,
#                                             status=3, is_delete=0).update(payment_check_date=datetime.now(),
#                                                                           sap_dwerk=DWERK, sap_charg=CHARG,
#                                                                           sap_aufnr=AUFNR, sap_auart=AUART,
#                                                                           sap_kdauf=KDAUF, sap_kdpos=KDPOS,
#                                                                           sap_matnr=MATNR, sap_notice_status=1)
#                     lot_info.objects.filter(mask_name=mask_name,
#                                             status=3, payment_status=0,
#                                             is_delete=0).update(payment_status=1)
#                     flag = add_order_num(tip_no, mask_name, production_order)  # 更新MES的SAP生产订单号
#                     if flag:
#                         dpResponse.result_code = "S"
#                         dpResponse.result_message = "Normal end"
#                     else:
#                         dpResponse.result_code = "F"
#                         dpResponse.result_message = "Update MES Fail"
#             else:  # 不存在对应的lot
#                 dpResponse.result_code = "F"
#                 dpResponse.result_message = "No corresponding ProductID was found"
#         except Exception as e:
#             dpResponse.request_code = "F"
#             dpResponse.request_message = "Request Fail"
#             dpResponse.result_code = "F"
#             dpResponse.result_message = "Error:" + str(e)
#             log.error("SAP_Webservice中notice_production_order方法出现异常：" + str(e))
#         return dpResponse
#
#
# class ShipOrUnshipProduction(ServiceBase):
#     """下线产品"""
#
#     @rpc(Array(Unicode), Unicode, Unicode, _returns=SDResponse)
#     def ship_or_unship(self, LOTID, CHNAME, ACTION):
#         print("-----------SHIP------------")
#         log.info("ship_or_unship参数为" + str(LOTID) + "|" + str(CHNAME) + "|" + str(ACTION))
#         sdResponse = SDResponse()
#         if ACTION == "SHIP":
#             try:
#                 result = SDService().ship(LOTID, str(CHNAME))
#                 print(result)
#                 l = list()
#                 if result.strShipLotResult:
#                     for lotResult in result.strShipLotResult.item:
#                         dic = {"lotID": None if "nil" in str(lotResult.lotID.identifier) else lotResult.lotID.identifier,
#                                "returnCode": None if "true" in str(lotResult.returnCode) else lotResult.returnCode}
#                         l.append(dic)
#                 sdResponse.returnCode = result.strResult.returnCode
#                 sdResponse.messageID = result.strResult.messageID
#                 sdResponse.messageText = result.strResult.messageText
#                 sdResponse.reasonText = None if 'nil' in str(result.strResult.reasonText) else str(result.strResult.reasonText)
#                 sdResponse.lotResult = json.dumps(l)
#                 print(sdResponse)
#             except Exception as e:
#                 sdResponse.returnCode = "F"
#                 sdResponse.messageID = "F"
#                 sdResponse.messageText = "Request Fail"
#                 sdResponse.reasonText = "Error:" + str(e)
#                 sdResponse.lotResult = None
#                 log.error("SAP_Webservice中ship方法出现异常：" + str(e))
#             return sdResponse
#         elif ACTION == "UNSHIP":
#             try:
#                 result = SDService().unShip(LOTID, str(CHNAME))
#                 print(result)
#                 l = list()
#                 if result.strShipCancelLotResult:
#                     for lotResult in result.strShipCancelLotResult.item:
#                         dic = {
#                             "lotID": None if "nil" in str(lotResult.lotID.identifier) else lotResult.lotID.identifier,
#                             "returnCode": None if "true" in str(lotResult.returnCode) else lotResult.returnCode}
#                         l.append(dic)
#                 sdResponse.returnCode = result.strResult.returnCode
#                 sdResponse.messageID = result.strResult.messageID
#                 sdResponse.messageText = result.strResult.messageText
#                 sdResponse.reasonText = None if 'nil' in str(result.strResult.reasonText) else str(result.strResult.reasonText)
#                 sdResponse.lotResult = json.dumps(l)
#                 print(sdResponse)
#             except Exception as e:
#                 sdResponse.returnCode = "F"
#                 sdResponse.messageID = "F"
#                 sdResponse.messageText = "Request Fail"
#                 sdResponse.reasonText = "Error:" + str(e)
#                 sdResponse.lotResult = None
#                 log.error("SAP_Webservice中unship方法出现异常：" + str(e))
#             return sdResponse
#
#
# npo_application = Application([NoticeProductionOrder],
#                               tns="DP.SAP.NoticeProductionOrder",
#                               in_protocol=Soap11(validator='lxml'),
#                               out_protocol=Soap11())
#
# notice_production_order_app = csrf_exempt(DjangoApplication(npo_application))
#
#
# ship_or_unship_application = Application([ShipOrUnshipProduction],
#                                          tns="DP.SAP.ShipOrUnshipProduction",
#                                          in_protocol=Soap11(validator='lxml'),
#                                          out_protocol=Soap11())
#
# ship_or_unship_app = csrf_exempt(DjangoApplication(ship_or_unship_application))
