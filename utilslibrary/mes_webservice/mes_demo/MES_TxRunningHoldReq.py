import traceback

from utilslibrary.mes_webservice import mes_utils

client = mes_utils.get_ws_client()

def MES_TxRunningHoldReq(pptUser,
                         equipmentID,
                         holdReasonCodeID,
                         ControlJobID,
                         claimMemo):
    print(client)
    # Parameter 1: pptUser
    paramUser = client.factory.create('pptUser')
    paramUser.userID.identifier = pptUser["userID"]
    paramUser.password = pptUser["password"]

    # Parameter 2: equipmentID
    paramEQPID = client.factory.create('objectIdentifier')
    paramEQPID.identifier = equipmentID

    # Parameter 3: controlJobID
    paramControlJobID = client.factory.create('objectIdentifier')
    paramControlJobID.identifier = ControlJobID

    # Paramrter 4: holdReasonCodeID
    paramholdReasonCodeID = client.factory.create('objectIdentifier')
    paramholdReasonCodeID.identifier = holdReasonCodeID

    # Paramrter 5: claimMemo
    paramclaimMemo = claimMemo or ''

    try:
        resultOutput = client.service.TxRunningHoldReq(paramUser, paramEQPID, paramControlJobID, paramholdReasonCodeID, paramclaimMemo)
        print(resultOutput)
        if resultOutput.strResult.returnCode != 0:
            raise Exception(resultOutput.strResult.messageText)
    except Exception as e:
        traceback.print_exc()


if __name__ == "__main__":
    pptUser = {"userID": "DP_Test", "password": "utfU`QE"}

    MES_TxRunningHoldReq(pptUser,
                         "MDCOM01",
                         'RNHL',
                         'MDCOM01-20200416-0005',
                         '')

