from suds.client import Client

# 测试测试
# from utilslibrary.mes_webservice.mes_base_webservice import MES_TxEqpInfoInq
from utilslibrary.mes_webservice import mes_utils
from utilslibrary.mes_webservice.mes_utils import get_wsdl_file

if __name__ == "__main__":
    ppt_user = {'userID': 'DP_Test', 'password': 'utfU`QE'}
    equipmentID = 'MWEB901'

    # wsdl_file = get_wsdl_file()
    client = mes_utils.get_ws_client()
    print(client)
    # parmUser = client.factory.create('pptUser')
    # parmUser.userID.identifier = "DP_Test"
    # parmUser.password = "utfU`QE"
    # #
    # # parmCassetteIDSequence = client.factory.create('objectIdentifierSequence')
    # # lot_id = client.factory.create('objectIdentifier')
    # # lot_id.identifier = 'MA10000B.001'
    # # parmCassetteIDSequence.item.append(lot_id)
    #
    # # route_id = client.factory.create('objectIdentifier')
    # # route_id.identifier = 'OMOG_01.1'
    # # n = client.factory.create('objectIdentifier')
    # # operation_id = client.factory.create('objectIdentifier')
    # # operation_id.identifier = 'MCDTPC.1'
    # # result = client.service.TxRouteOperationListInq__160(parmUser, route_id, n, '', '', 100)
    # #
    # # print(result)
    # # resultLoadingLotOutput = client.service.TxLotInfoInq__160(parmUser, parmCassetteIDSequence, True, True, True, True,
    # #                                                           True, True, True, True, True, True, True, True, True,
    # #                                                           True, True)
    # # paramUser = client.factory.create('pptUser')
    # # paramUser.userID.identifier = ppt_user["userID"]
    # # paramUser.password = ppt_user["password"]
    #
    # # Parameter 2: equipmentID
    # paramEQPID = client.factory.create('objectIdentifier')
    # paramEQPID.identifier = equipmentID
    #
    #
    # # TxEqpInfoInq__160(pptUser requestUserID, objectIdentifier equipmentID,
    # # xs:boolean requestFlagForBRInfo,
    # # xs:boolean requestFlagForStatusInfo,
    # # xs:boolean requestFlagForPMInfo,
    # # xs:boolean requestFlagForPortInfo,
    # # xs:boolean requestFlagForChamberInfo,
    # # xs:boolean requestFlagForStockerInfo,
    # # xs:boolean requestFlagForInprocessingLotInfo,
    # # xs:boolean requestFlagForReservedControlJobInfo,
    # # xs:boolean requestFlagForRSPPortInfo,
    # # xs:boolean requestFlagForEqpContainerInfo)
    # result = client.service.TxEqpInfoInq__160(parmUser, paramEQPID, True, True, True, True, True, True, True, True, True, True)
    # # result = client.service.TxEqpInfoInq__160(parmUser, paramEQPID, False, False, False, False, False, False, False, False,
    # #                                           False, False)
    # if result.strResult.returnCode != "0":
    #     raise Exception(result.strResult.messageText)
    # print(result.equipmentStatusInfo.equipmentStatusCode.identifier)