#!/usr/bin/python3

from utilslibrary.mes_webservice import mes_utils

client = mes_utils.get_ws_client()


# typedef struct csUniversalHoldLotReqInParm_struct
# {
#    objectIdentifierSequence                lotIDSeq;
#    objectIdentifier                        reasonCode;
#    string                                  holdClaimMemo;
#    any                                     siInfo;
# } csUniversalHoldLotReqInParm;
#
# Parameter 2.1: csUniversalHoldLotReqInParm
parmUniversalHold = client.factory.create('csUniversalHoldLotReqInParm')
parmLot = client.factory.create('objectIdentifier')
parmLot.identifier = "QA000255.001"
parmUniversalHold.lotIDSeq.item.append(parmLot)

# Parameter 2.2: reasonCode
parmUniversalHold.reasonCode.identifier = "0CS1"

# Parameter 2.3: holdClaimMemo
parmUniversalHold.holdClaimMemo = "Hold by DP Automation"



#########################################################################
# csUniversalHoldLotReqResult CS_TxUniversalHoldLotReq
# (
#    in pptUser                                  requestUserID,
#    in csUniversalHoldLotReqInParm              strUniversalHoldLotReqInParm,
#    in string                                   claimMemo
# )
def MES_TxUniversalHoldLotReq(parmUniversalHoldLot, parmClaimMemo):
    # Parameter 1: pptUser
    parmUser = client.factory.create('pptUser')
    parmUser.userID.identifier = "ADMIN"
    parmUser.password = "ojneb"

    resultOutput = client.service.CS_TxUniversalHoldLotReq(parmUser, parmUniversalHoldLot, parmClaimMemo)
    if resultOutput.strResult.returnCode != "0":
        raise Exception(resultOutput.strResult.messageText)
    return resultOutput.strResult.returnCode


try:
    MES_TxUniversalHoldLotReq(parmUniversalHold, "Called by DP Automation")
except Exception as ex:
    print(ex)

print("OK!!")

