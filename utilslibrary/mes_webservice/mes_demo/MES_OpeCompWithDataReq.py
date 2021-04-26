#!/usr/bin/python3

from utilslibrary.mes_webservice import mes_utils

client = mes_utils.get_ws_client()

def MES_OpeCompWithDataReq(pptUser,
                           equipmentID,
                           controlJobID):
    # Parameter 1: pptUser
    paramUser = client.factory.create('pptUser')
    paramUser.userID.identifier = pptUser["userID"]
    paramUser.password = pptUser["password"]

    # Parameter 2: equipmentID
    paramEQPID = client.factory.create('objectIdentifier')
    paramEQPID.identifier = equipmentID

    # Parameter 3: controlJobID
    paramControlJobID = client.factory.create('objectIdentifier')
    paramControlJobID.identifier = controlJobID

    # Parameter 4: spcResultRequiredFlag
    paramSpcResultRequiredFlag = False

    # Parameter 5: claimMemo
    paramClaimMemo = ""

    try:
        resultOutput = client.service.TxOpeCompWithDataReq(paramUser, paramEQPID, paramControlJobID, paramSpcResultRequiredFlag, paramClaimMemo)
        print(resultOutput)
        if resultOutput.strResult.returnCode != "0":
            raise Exception(resultOutput.strResult.messageText)


        return resultOutput.strResult.returnCode
    except Exception as ex:
        print(ex)

if __name__ == '__main__':
    pptUser = {"userID":"ADMIN","password":"ojneb"}

    MES_OpeCompWithDataReq(pptUser,
                      "NDUM1",
                      "NDUM1-20200323-0009")