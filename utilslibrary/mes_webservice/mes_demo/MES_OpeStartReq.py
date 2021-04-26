#!/usr/bin/python3
import traceback

from utilslibrary.mes_webservice import mes_utils

client = mes_utils.get_ws_client()


#######################################################################
# pptOpeStartReqResult TxOpeStartReq
# (
#    in pptUser requestUserID,
#    in objectIdentifier equipmentID,
#    in string portGroupID,
#    in objectIdentifier controlJobID,
#    in pptStartCassetteSequence strStartCassette,
#    in boolean processJobPauseFlag,
#    in string claimMemo
# )
def MES_TxOpeStartReq(cassetteID, equipmentID, loadPortID, bVirturalOperation):
    # Parameter 1: pptUser
    parmUser = client.factory.create('pptUser')
    parmUser.userID.identifier = "DP_Test"
    parmUser.password = "utfU`QE"

    # 1. if Operation is not virtual, need to do TxLoadingLotRpt first
    if bVirturalOperation is False:
        # pptLoadingLotRptResult TxLoadingLotRpt
        # (
        #    in pptUser requestUserID,
        #    in objectIdentifier equipmentID,
        #    in objectIdentifier cassetteID,
        #    in objectIdentifier portID,
        #    in string loadPurposeType,
        #    in string claimMemo
        # )
        print("TxLoadingLotRpt")
        resultLoadingLotOutput = client.service.TxLoadingLotRpt(parmUser, equipmentID, cassetteID, loadPortID, "Process Lot", "Called by DP Automation")
        if resultLoadingLotOutput.strResult.returnCode != "0":
            raise Exception(resultLoadingLotOutput.strResult.messageText)

    # 2. Get StartCassette data from TxLotsInfoForOpeStartInq
    # pptLotsInfoForOpeStartInqResult TxLotsInfoForOpeStartInq
    # (
    #    in pptUser requestUserID,
    #    in objectIdentifier equipmentID,
    #    in objectIdentifierSequence cassetteID
    # )
    #
    #     Parameter 2.3: cassetteID
    print("TxLotsInfoForOpeStartInq")
    parmCassetteIDSequence = client.factory.create('objectIdentifierSequence')
    parmCassetteIDSequence.item.append(cassetteID)
    resultLotsInfoOutput = client.service.TxLotsInfoForOpeStartInq(parmUser, equipmentID, parmCassetteIDSequence)
    if resultLotsInfoOutput.strResult.returnCode != "0":
        raise Exception(resultLotsInfoOutput.strResult.messageText)

    # 3. Operation Start
    #     Parameter 3.3: portGroupID
    #                    if value is _nil, it will cause fail, so need to change value to empty string
    parmPortGroupID = resultLotsInfoOutput.portGroupID
    if "_nil" in parmPortGroupID:
        parmPortGroupID = ""
    print(parmPortGroupID)
    #     Parameter 3.4: controlJobID
    parmControlJobID = client.factory.create('objectIdentifier')
    parmControlJobID.identifier = ""
    #     Parameter 3.5: strStartCassette
    #                    Some column's value are _nil, it will cause fail, so need to change value to empty string
    parmStartCassetteSeq = resultLotsInfoOutput.strStartCassette
    for startCast in parmStartCassetteSeq.item:
        if "_nil" in startCast.cassetteID.stringifiedObjectReference:
            startCast.cassetteID.stringifiedObjectReference = ""
        if "_nil" in startCast.loadPortID.identifier:
            startCast.loadPortID.identifier = ""
            startCast.loadPortID.stringifiedObjectReference = ""
        if "_nil" in startCast.unloadPortID.identifier:
            startCast.unloadPortID.identifier = ""
            startCast.unloadPortID.stringifiedObjectReference = ""
        for lot in startCast.strLotInCassette.item:
            if "_nil" in lot.strStartRecipe.logicalRecipeID.identifier:
                lot.strStartRecipe.logicalRecipeID.identifier = ""
                lot.strStartRecipe.logicalRecipeID.stringifiedObjectReference = ""
            if "_nil" in lot.strStartRecipe.machineRecipeID.identifier:
                lot.strStartRecipe.machineRecipeID.identifier = ""
                lot.strStartRecipe.machineRecipeID.stringifiedObjectReference = ""
            if "_nil" in lot.strStartRecipe.physicalRecipeID:
                lot.strStartRecipe.physicalRecipeID = ""
            # for dcDef in lot.strStartRecipe.strDCDef.item:
            #     for dcItem in dcDef.strDCItem.item:
            #         if "_nil" in dcItem.dataCollectionUnit:
            #             dcItem.dataCollectionUnit = ""
            #         if "_nil" in dcItem.waferID.stringifiedObjectReference:
            #             dcItem.waferID.stringifiedObjectReference = ""
            #         if "_nil" in dcItem.waferPosition:
            #             dcItem.waferPosition = ""
            #         if "_nil" in dcItem.sitePosition:
            #             dcItem.sitePosition = ""
            #         if "_nil" in dcItem.calculationExpression:
            #             dcItem.calculationExpression = ""
            #     if "_nil" in dcDef.dcSpecDescription:
            #         dcDef.dcSpecDescription = ""
            #     if "_nil" in dcDef.previousDataCollectionDefinitionID.identifier:
            #         dcDef.previousDataCollectionDefinitionID.identifier = ""
            #         dcDef.previousDataCollectionDefinitionID.stringifiedObjectReference = ""
            #     if "_nil" in dcDef.previousOperationID.identifier:
            #         dcDef.previousOperationID.identifier = ""
            #         dcDef.previousOperationID.stringifiedObjectReference = ""
            #     if "_nil" in dcDef.previousOperationNumber:
            #         dcDef.previousOperationNumber = ""
            if "_nil" in lot.recipeParameterChangeType:
                lot.recipeParameterChangeType = ""
            if "_nil" in lot.strStartOperationInfo.routeID.identifier:
                lot.strStartOperationInfo.routeID.identifier = ""
                lot.strStartOperationInfo.routeID.stringifiedObjectReference = ""
            if "_nil" in lot.strStartOperationInfo.operationID.identifier:
                lot.strStartOperationInfo.operationID.identifier = ""
                lot.strStartOperationInfo.operationID.stringifiedObjectReference = ""
            if "_nil" in lot.strStartOperationInfo.operationNumber:
                lot.strStartOperationInfo.operationNumber = ""
            for wafer in lot.strLotWafer.item:
                if "_nil" in wafer.processJobStatus:
                    wafer.processJobStatus = ""
    print(parmStartCassetteSeq)
    resultOpeStartOutput = client.service.TxOpeStartReq(parmUser, equipmentID, parmPortGroupID, parmControlJobID, parmStartCassetteSeq, False, "Called by DP Automation")
    print(resultOpeStartOutput.strResult.returnCode)
    if resultOpeStartOutput.strResult.returnCode != "0":
        raise Exception(resultOpeStartOutput.strResult.messageText)

    return resultOpeStartOutput.controlJobID.identifier


# Parameter 1: cassetteID
#parmLotID = client.factory.create('objectIdentifier')
#parmLotID.identifier = "QA000347.001"
#lots = MES_GetWIP.MES_TxLotListInq('', parmLotID, True)
#parmCassetteID = lots.item[0].carrierID
#print(parmCassetteID)
parmCassetteID = client.factory.create('objectIdentifier')
#parmCassetteID.identifier = "XTCarrier67"
parmCassetteID.identifier = "MA100099"

# Parameter 2: equipmentID
parmEquipmentID = client.factory.create('objectIdentifier')
parmEquipmentID.identifier = "MDCOM01"
# parmEquipmentID.identifier = "NDUM1"

# Parameter 2: loadPortID
parmLoadPortID = client.factory.create('objectIdentifier')
parmLoadPortID.identifier = ""

try:
    controlJobID = MES_TxOpeStartReq(parmCassetteID, parmEquipmentID, parmLoadPortID, True)
    print(controlJobID)
except Exception as ex:
    traceback.print_exc()
    print('error')


print("OK!!")