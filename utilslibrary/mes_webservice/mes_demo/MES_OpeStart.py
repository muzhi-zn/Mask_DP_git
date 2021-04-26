#!/usr/bin/python3

from utilslibrary.mes_webservice import mes_utils

client = mes_utils.get_ws_client()

def MES_TxOpeStartReq(pptUser,
                      equipmentID,
                      cassetteID):
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

    # Parameter :equipmentID
    parmEquipmentID = client.factory.create('objectIdentifier')
    parmEquipmentID.identifier = equipmentID

    # 2. Get StartCassette data from TxLotsInfoForOpeStartInq
    # pptLotsInfoForOpeStartInqResult TxLotsInfoForOpeStartInq
    # (
    #    in pptUser requestUserID,
    #    in objectIdentifier equipmentID,
    #    in objectIdentifierSequence cassetteID
    # )
    #
    #     Parameter 2.3: cassetteID
    parmCassetteIDSequence = client.factory.create('objectIdentifierSequence')
    parmCassetteID = client.factory.create('objectIdentifier')
    parmCassetteID.identifier = cassetteID
    parmCassetteIDSequence.item.append(parmCassetteID)
    resultLotsInfoOutput = client.service.TxLotsInfoForOpeStartInq(paramUser, parmEquipmentID, parmCassetteIDSequence)
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

            try:
                for dcDef in lot.strStartRecipe.strDCDef.item:
                    for dcItem in dcDef.strDCItem.item:
                        if "_nil" in dcItem.dataCollectionUnit:
                            dcItem.dataCollectionUnit = ""
                        if "_nil" in dcItem.waferID.stringifiedObjectReference:
                            dcItem.waferID.stringifiedObjectReference = ""
                        if "_nil" in dcItem.waferPosition:
                            dcItem.waferPosition = ""
                        if "_nil" in dcItem.sitePosition:
                            dcItem.sitePosition = ""
                        if "_nil" in dcItem.calculationExpression:
                            dcItem.calculationExpression = ""
                    if "_nil" in dcDef.dcSpecDescription:
                        dcDef.dcSpecDescription = ""
                    if "_nil" in dcDef.previousDataCollectionDefinitionID.identifier:
                        dcDef.previousDataCollectionDefinitionID.identifier = ""
                        dcDef.previousDataCollectionDefinitionID.stringifiedObjectReference = ""
                    if "_nil" in dcDef.previousOperationID.identifier:
                        dcDef.previousOperationID.identifier = ""
                        dcDef.previousOperationID.stringifiedObjectReference = ""
                    if "_nil" in dcDef.previousOperationNumber:
                        dcDef.previousOperationNumber = ""
            except Exception as ex:
                #if lot.strStartRecipe.strDCDef is empty, will come here. We can ignore this exception
                print(ex)

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
    resultOpeStartOutput = client.service.TxOpeStartReq(paramUser, parmEquipmentID, parmPortGroupID, parmControlJobID, parmStartCassetteSeq, False, "Called by DP Automation")

    if resultOpeStartOutput.strResult.returnCode != "0":
        raise Exception(resultOpeStartOutput.strResult.messageText)

    return resultOpeStartOutput




if __name__ == '__main__':
    pptUser = {'userID': 'DP_Test', 'password': 'utfU`QE'}

    result = MES_TxOpeStartReq(pptUser,
                      "MDCOM01",
                      "MA100011")
    print(result)
    message = result.strResult.messageText
    print(message)
    transactionID = result.strResult.transactionID
    print(transactionID)
    contorlJobID = result.controlJobID.identifier
    print(contorlJobID)
    operationNumber = result.strStartCassette.item[0].strLotInCassette.item[0].strStartOperationInfo.operationNumber
    print(operationNumber)
    passCount = result.strStartCassette.item[0].strLotInCassette.item[0].strStartOperationInfo.passCount
    print(passCount)

