from utilslibrary.mes_webservice import mes_utils

ppt_user = {'userID': 'DP_Test', 'password': 'utfU`QE'}
equipmentID = 'MWEB901'

# wsdl_file = get_wsdl_file()
client = mes_utils.get_ws_client()


# TxOpeLocateReq(pptUser requestUserID,
#               xs:boolean locateDirection,
#               objectIdentifier lotID,
#               objectIdentifier currentRouteID,
#               xs:string currentOperationNumber,
#               objectIdentifier routeID,
#               objectIdentifier operationID,
#               xs:string operationNumber,
#               pptProcessRef processRef,
#               xs:int seqno,
#               xs:string claimMemo)
def ope_locate(lot_id):
    """站点切换方法"""
    print(client)
    parmUser = client.factory.create('pptUser')
    parmUser.userID.identifier = "DP_Test"
    parmUser.password = "utfU`QE"
    lotId = client.factory.create('objectIdentifier')
    lotId.identifier = lot_id
    routeID = client.factory.create('objectIdentifier')  # OMOG_01.1
    routeID.identifier = "OMOG_01.1"
    operationID = client.factory.create('objectIdentifier')
    operationID.identifier = "MCDTPC.1"
    processRef = client.factory.create('pptProcessRef')

    result = client.service.TxOpeLocateReq(parmUser, False, lotId, routeID, "100.700", routeID, operationID, "100.100", processRef,
                                           1, "test")
    print(result)


if __name__ == "__main__":
    ope_locate('MA100113.001')
