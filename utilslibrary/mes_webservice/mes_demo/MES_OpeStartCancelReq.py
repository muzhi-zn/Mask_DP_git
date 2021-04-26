#!/usr/bin/python3
from suds.client import Client

# from utilslibrary.mes_webservice import mes_utils

client = Client('file:///C:\\workspace\\DP_Phase1\\utilslibrary\\mes_webservice\\'+
                'MES_FILES/MMS_CS/wsdl/CS_PPTServiceManager.wsdl',
                location="http://10.3.16.30:17101/CS_PPTServiceManager/thePPTServiceManager", cache=None)


def MES_OpeStartCancelReq(pptUser, equipmentID, controlJobID):
    """    pptOpeStartReqResult TxOpeStartReq
        (
        in pptUser requestUserID,
        in objectIdentifier equipmentID,
        in string portGroupID,
        in objectIdentifier controlJobID,
        in pptStartCassetteSequence strStartCassette,
        in boolean processJobPauseFlag,
        in string claimMemo
        ); """
    # Parameter 1: pptUser
    paramUser = client.factory.create('pptUser')
    paramUser.userID.identifier = pptUser["userID"]
    paramUser.password = pptUser["password"]

    # Parameter 2: equipmentID
    paramEquipmentID = client.factory.create('objectIdentifier')
    paramEquipmentID.identifier = equipmentID

    # Parameter 3: controlJobID
    paramControlJobID = client.factory.create('objectIdentifier')
    paramControlJobID.identifier = controlJobID


    resultOpeStartCancelOutput = client.service.TxOpeStartCancelReq(paramUser, paramEquipmentID, paramControlJobID, "Called by DP Automation")
    print(resultOpeStartCancelOutput)
    if resultOpeStartCancelOutput.strResult.returnCode != "0":
        raise Exception(resultOpeStartCancelOutput.strResult.messageText)

    return resultOpeStartCancelOutput.strResult.returnCode




if __name__ == '__main__':
    pptUser = {'userID': 'DP_SYS', 'password': 'es1xttAQ'}

    MES_OpeStartCancelReq(pptUser, "MDCOM01", "MDCOM01-20210119-0013")

