#!/usr/bin/python3

from utilslibrary.mes_webservice import mes_utils

client = mes_utils.get_ws_client()


# Parameter 2: lotID
parmLot = client.factory.create('objectIdentifier')
parmLot.identifier = "MA000000.001"

# Parameter 3: releaseReasonCodeID
parmRelReasonCode = client.factory.create('objectIdentifier')
parmRelReasonCode.identifier = "RNHR"


# typedef struct pptHoldReq_struct {
#    string           holdType;                  //<i>Hold Type
#                                                    //<c>SP_HoldType_LotHold                    "LotHold"
#                                                    //<c>SP_HoldType_BankHold                   "BankHold"
#                                                    //<c>SP_HoldType_FutureHold                 "FutureHold"
#                                                    //<c>SP_HoldType_MergeHold                  "MergeHold"
#                                                    //<c>SP_HoldType_MonitorSPCHold             "MonitorSPCHold"
#                                                    //<c>SP_HoldType_MonitorSpecHold            "MonitorSpecHold"
#                                                    //<c>SP_HoldType_ReworkHold                 "ReworkHold"
#                                                    //<c>SP_HoldType_SPCOutOfRangeHold          "SPCOutOfRangeHold"
#                                                    //<c>SP_HoldType_SpecOverHold               "SpecOverHold"
#                                                    //<c>SP_HoldType_WaitingMonitorResultHold   "WaitingMonitorHold"
#                                                    //<c>SP_HoldType_ProcessHold                "ProcessHold"
#                                                    //<c>SP_HoldType_RecipeHold                 "RecipeHold"
#                                                    //<c>SP_HoldType_RunningHold                "RunningHold"
#                                                    //<c>SP_HoldType_ForceCompHold              "ForceCompHold"
#    objectIdentifier holdReasonCodeID;          //<i>Hold Reason Code ID
#    objectIdentifier holdUserID;                //<i>Hold User ID
#    string           responsibleOperationMark;  //<i>Responsible Opration Mark.
#                                                    //<c>SP_ResponsibleOperation_Current        "C"
#                                                    //<c>SP_ResponsibleOperation_Previous       "P"
#    objectIdentifier routeID;                   //<i>Route ID
#    string           operationNumber;           //<i>Operation Number
#    objectIdentifier relatedLotID;              //<i>Related Lot ID
#    string           claimMemo;                 //<i>Claim Comment
#    any siInfo;                                 //<i>Reserved for SI customization
# }pptHoldList;
#
# typedef sequence<pptHoldList> pptHoldListSequence ;
#
# Parameter 4: pptHoldListSequence
parmHoldListSeq = client.factory.create('pptHoldListSequence')
#    Parameter 4.1: pptHoldList
parmHoldList = client.factory.create('pptHoldList')
parmHoldList.holdType = "LotHold"
#       Parameter 4.1.1: holdReasonCodeID
parmHoldList.holdReasonCodeID = client.factory.create('objectIdentifier')
parmHoldList.holdReasonCodeID.identifier = "RNHL"
#       Parameter 4.1.2: holdUserID
parmHoldList.holdUserID = client.factory.create('objectIdentifier')
parmHoldList.holdUserID.identifier = "DP_Test"
#       Parameter 4.1.3: responsibleOperationMark
parmHoldList.responsibleOperationMark = "P"
#       Parameter 4.1.4: routeID
parmHoldList.routeID = client.factory.create('objectIdentifier')
parmHoldList.routeID.identifier = "dctest03.1"
#       Parameter 4.1.5: operationNumber
parmHoldList.operationNumber = "51.20"

parmHoldListSeq.item.append(parmHoldList)


#########################################################################
# pptHoldLotReleaseReqResult TxHoldLotReleaseReq
# (
#    in pptUser requestUserID,
#    in objectIdentifier lotID,
#    in objectIdentifier releaseReasonCodeID,
#    in pptHoldListSequence strLotHoldReleaseReqList
# )
def MES_TxHoldLotReleaseReq(parmLot, parmRelReasonCode, parmHoldListSeq):
    # Parameter 1: pptUser
    parmUser = client.factory.create('pptUser')
    parmUser.userID.identifier = "DP_Test"
    parmUser.password = "utfU`QE"

    resultOutput = client.service.TxHoldLotReleaseReq(parmUser, parmLot, parmRelReasonCode, parmHoldListSeq)
    if resultOutput.strResult.returnCode != "0":
        raise Exception(resultOutput.strResult.messageText)
    return resultOutput.strResult.returnCode


try:
    MES_TxHoldLotReleaseReq(parmLot, parmRelReasonCode, parmHoldListSeq)
except Exception as ex:
    print(ex)

print("OK!!")

