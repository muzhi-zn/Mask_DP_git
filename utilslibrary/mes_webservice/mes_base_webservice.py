# !/usr/bin/python3
import logging
from urllib.error import URLError

from retrying import retry

from Mask_DP.settings import MES_RETRY_NUM
from utilslibrary.mes_webservice import mes_utils
from utilslibrary.utils.date_utils import getMESDateStr

log = logging.getLogger('log')

client = mes_utils.get_ws_client()


def retry_if_url_error(exception):
    """判断是否是超时错误"""
    return isinstance(exception, URLError)


@retry(stop_max_attempt_number=MES_RETRY_NUM, retry_on_exception=retry_if_url_error, wait_random_min=1000,
       wait_random_max=3000)
def MES_TxLotListInq(pptUser, lot_id, bVirturalOperation):
    """根据查询条件获取lot相关信息"""
    parmUser = client.factory.create('pptUser')
    parmUser.userID.identifier = pptUser['userID']
    parmUser.password = pptUser['password']

    parmObjectIdentifier = client.factory.create('objectIdentifier')

    lotID = client.factory.create('objectIdentifier')
    lotID.identifier = lot_id

    resultOutput = client.service.TxLotListInq__180(parmUser,
                                                    parmObjectIdentifier,  # bankID
                                                    '',  # lotStatus
                                                    '',  # lotType,
                                                    parmObjectIdentifier,  # productID,
                                                    '',  # orderNumber
                                                    '',  # customerCode
                                                    parmObjectIdentifier,  # manufacturingLayerID
                                                    parmObjectIdentifier,  # routeID
                                                    '',  # operationNumber
                                                    False,  # bankInRequiredFlag
                                                    lotID,  # lotID
                                                    '',  # requiredCassetteCategory
                                                    False,  # backupProcessingFlag
                                                    '',  # subLotType
                                                    False,  # deleteLotFlag
                                                    parmObjectIdentifier,  # holdReasonCodeID
                                                    False,  # sorterJobCreationCheckFlag
                                                    '',  # interFabXferState
                                                    False,  # autoDispatchControlLotFlag
                                                    bVirturalOperation,  # virtualOperationFlag
                                                    parmObjectIdentifier  # operationID
                                                    )
    if resultOutput.strResult.returnCode != "0":
        raise Exception(resultOutput.strResult.messageText)
    return resultOutput


def MES_TxLotListInqForReWork(pptUser, OP_ID):
    """获取MRDODR.1下的lotList"""
    parmUser = client.factory.create('pptUser')
    parmUser.userID.identifier = pptUser['userID']
    parmUser.password = pptUser['password']

    parmObjectIdentifier = client.factory.create('objectIdentifier')

    OpID = client.factory.create('objectIdentifier')
    OpID.identifier = OP_ID

    resultOutput = client.service.TxLotListInq__180(parmUser,
                                                    parmObjectIdentifier,  # bankID
                                                    '',  # lotStatus
                                                    '',  # lotType,
                                                    parmObjectIdentifier,  # productID,
                                                    '',  # orderNumber
                                                    '',  # customerCode
                                                    parmObjectIdentifier,  # manufacturingLayerID
                                                    parmObjectIdentifier,  # routeID
                                                    '',  # operationNumber
                                                    False,  # bankInRequiredFlag
                                                    parmObjectIdentifier,  # lotID
                                                    '',  # requiredCassetteCategory
                                                    False,  # backupProcessingFlag
                                                    '',  # subLotType
                                                    False,  # deleteLotFlag
                                                    parmObjectIdentifier,  # holdReasonCodeID
                                                    False,  # sorterJobCreationCheckFlag
                                                    '',  # interFabXferState
                                                    False,  # autoDispatchControlLotFlag
                                                    False,  # virtualOperationFlag
                                                    OpID  # operationID
                                                    )
    if resultOutput.strResult.returnCode != "0":
        raise Exception(resultOutput.strResult.messageText)
    return resultOutput


@retry(stop_max_attempt_number=MES_RETRY_NUM, retry_on_exception=retry_if_url_error, wait_random_min=1000,
       wait_random_max=3000)
def MES_TxOpeStartReq(pptUser,
                      equipmentID,
                      cassetteID, operationID):
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
                # if lot.strStartRecipe.strDCDef is empty, will come here. We can ignore this exception
                print(ex)
            if "_nil" in lot.recipeParameterChangeType:
                lot.recipeParameterChangeType = ""
            if "_nil" in lot.strStartOperationInfo.routeID.identifier:
                lot.strStartOperationInfo.routeID.identifier = ""
                lot.strStartOperationInfo.routeID.stringifiedObjectReference = ""
            if "_nil" in lot.strStartOperationInfo.operationID.identifier:
                lot.strStartOperationInfo.operationID.identifier = ""
                lot.strStartOperationInfo.operationID.stringifiedObjectReference = ""
            if lot.strStartOperationInfo.operationID.identifier != operationID:
                raise Exception("operationID is not match")
            if "_nil" in lot.strStartOperationInfo.operationNumber:
                lot.strStartOperationInfo.operationNumber = ""
            for wafer in lot.strLotWafer.item:
                if "_nil" in wafer.processJobStatus:
                    wafer.processJobStatus = ""
    resultOpeStartOutput = client.service.TxOpeStartReq(paramUser, parmEquipmentID, parmPortGroupID, parmControlJobID,
                                                        parmStartCassetteSeq, False, "Called by DP Automation")
    if resultOpeStartOutput.strResult.returnCode != "0":
        raise Exception(resultOpeStartOutput.strResult.messageText)

    return resultOpeStartOutput


@retry(stop_max_attempt_number=MES_RETRY_NUM, retry_on_exception=retry_if_url_error, wait_random_min=1000,
       wait_random_max=3000)
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

    resultOpeStartCancelOutput = client.service.TxOpeStartCancelReq(paramUser, paramEquipmentID, paramControlJobID,
                                                                    "Called by DP Automation")
    if resultOpeStartCancelOutput.strResult.returnCode != "0":
        raise Exception(resultOpeStartCancelOutput.strResult.messageText)

    return resultOpeStartCancelOutput


@retry(stop_max_attempt_number=MES_RETRY_NUM, retry_on_exception=retry_if_url_error, wait_random_min=1000,
       wait_random_max=3000)
def MES_OpeCompWithDataReq(pptUser, equipmentID, controlJobID):
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

    resultOutput = client.service.TxOpeCompWithDataReq(paramUser, paramEQPID, paramControlJobID,
                                                       paramSpcResultRequiredFlag, paramClaimMemo)
    if resultOutput.strResult.returnCode != "0":
        raise Exception(resultOutput.strResult.messageText)

    return resultOutput


@retry(stop_max_attempt_number=MES_RETRY_NUM, retry_on_exception=retry_if_url_error, wait_random_min=1000,
       wait_random_max=3000)
def MES_TxExTIPLayerDataParmUpdateExptool(pptUser, tip_no, mask_name, lot_id, exptool):
    """更新lot的EXPTOOL"""
    paramUser = client.factory.create('pptUser')
    paramUser.userID.identifier = pptUser["userID"]
    paramUser.password = pptUser["password"]
    parmTIPLayerDataSetReqIn = client.factory.create('csExTIPLayerDataParmSetReqInParm')
    parmTIPLayerDataSetReqIn.Action = "Update"  # Insert/Update/Delete/ResetCnt
    parmTIPLayerData = client.factory.create('csExTIPLayerData')
    parmTIPLayerData.tipNO = tip_no
    parmTIPLayerDataInfo = client.factory.create('csExTIPLayerDataInfo')
    parmTIPLayerDataInfo.partName = mask_name
    parmTIPLayerDataInfo.lotID = lot_id
    parmTIPLayerData_Param = client.factory.create('csExTIPLayerData_Param')
    parmTIPLayerData_Param.name = "DP_EXPTOOL"
    parmTIPLayerData_Param.type = "String"
    parmTIPLayerData_Param.value = exptool
    parmTIPLayerData_Param.claimUserID.identifier = pptUser['userID']
    parmTIPLayerData_Param.claimTimeStamp = getMESDateStr()
    parmTIPLayerDataInfo.strExTIPLayerData_ParamSequence.item.append(parmTIPLayerData_Param)
    parmTIPLayerData.strExTIPLayerDataInfoSequence.item.append(parmTIPLayerDataInfo)
    parmTIPLayerDataSetReqIn.strExTIPLayerData = parmTIPLayerData
    resultOutput = client.service.CS_TxExTIPLayerDataParmSetReq(paramUser, parmTIPLayerDataSetReqIn)
    if resultOutput.strResult.returnCode != "0":
        raise Exception(resultOutput.strResult.messageText)
    return resultOutput.strResult.returnCode


def MES_TxExTIPLayerDataParmAddSapOrder(pptUser, tip_no, mask_name, production_order, lot_id=None):
    """更新lot的SAP生成订单号"""
    paramUser = client.factory.create('pptUser')
    paramUser.userID.identifier = pptUser["userID"]
    paramUser.password = pptUser["password"]
    parmTIPLayerDataSetReqIn = client.factory.create('csExTIPLayerDataParmSetReqInParm')
    parmTIPLayerDataSetReqIn.Action = "Update"  # Insert/Update/Delete/ResetCnt
    parmTIPLayerData = client.factory.create('csExTIPLayerData')
    parmTIPLayerData.tipNO = tip_no
    parmTIPLayerDataInfo = client.factory.create('csExTIPLayerDataInfo')
    parmTIPLayerDataInfo.partName = mask_name
    if lot_id:
        parmTIPLayerDataInfo.lotID = lot_id
    parmTIPLayerData_Param = client.factory.create('csExTIPLayerData_Param')
    parmTIPLayerData_Param.name = "DP_ORDER_NUM"
    parmTIPLayerData_Param.type = "String"
    parmTIPLayerData_Param.value = production_order
    parmTIPLayerData_Param.claimUserID.identifier = pptUser['userID']
    parmTIPLayerData_Param.claimTimeStamp = getMESDateStr()
    parmTIPLayerDataInfo.strExTIPLayerData_ParamSequence.item.append(parmTIPLayerData_Param)
    parmTIPLayerData.strExTIPLayerDataInfoSequence.item.append(parmTIPLayerDataInfo)
    parmTIPLayerDataSetReqIn.strExTIPLayerData = parmTIPLayerData
    resultOutput = client.service.CS_TxExTIPLayerDataParmSetReq(paramUser, parmTIPLayerDataSetReqIn)
    if resultOutput.strResult.returnCode != "0":
        raise Exception(resultOutput.strResult.messageText)
    return resultOutput.strResult.returnCode


def MES_TxExTIPLayerDataParmChangeB_P(pptUser, tip_no, mask_name, lot_id, blank_code, pellicle_code):
    """更新lot的Blank和Pellicle"""
    paramUser = client.factory.create('pptUser')
    paramUser.userID.identifier = pptUser["userID"]
    paramUser.password = pptUser["password"]
    parmTIPLayerDataSetReqIn = client.factory.create('csExTIPLayerDataParmSetReqInParm')
    parmTIPLayerDataSetReqIn.Action = "Update"  # Insert/Update/Delete/ResetCnt
    parmTIPLayerData = client.factory.create('csExTIPLayerData')
    parmTIPLayerData.tipNO = tip_no
    parmTIPLayerDataInfo = client.factory.create('csExTIPLayerDataInfo')
    parmTIPLayerDataInfo.partName = mask_name
    parmTIPLayerDataInfo.lotID = lot_id
    if blank_code:
        blank = client.factory.create('csExTIPLayerData_Param')
        blank.name = "DP_BLANK_CODE"
        blank.type = "String"
        blank.value = blank_code
        blank.claimUserID.identifier = pptUser['userID']
        blank.claimTimeStamp = getMESDateStr()
        parmTIPLayerDataInfo.strExTIPLayerData_ParamSequence.item.append(blank)
    if pellicle_code:
        pellicle = client.factory.create('csExTIPLayerData_Param')
        pellicle.name = "DP_PELLICLE_CODE"
        pellicle.type = "String"
        pellicle.value = pellicle_code
        pellicle.claimUserID.identifier = pptUser['userID']
        parmTIPLayerDataInfo.strExTIPLayerData_ParamSequence.item.append(pellicle)
    parmTIPLayerData.strExTIPLayerDataInfoSequence.item.append(parmTIPLayerDataInfo)
    parmTIPLayerDataSetReqIn.strExTIPLayerData = parmTIPLayerData
    resultOutput = client.service.CS_TxExTIPLayerDataParmSetReq(paramUser, parmTIPLayerDataSetReqIn)
    if resultOutput.strResult.returnCode != "0":
        raise Exception(resultOutput.strResult.messageText)
    return resultOutput.strResult.returnCode


def MES_TxExTIPLayerDataParmInsertB_P(pptUser, lot_id, blank_code, pellicle_code):
    """更新lot的Blank和Pellicle"""
    paramUser = client.factory.create('pptUser')
    paramUser.userID.identifier = pptUser["userID"]
    paramUser.password = pptUser["password"]
    parmTIPLayerDataSetReqIn = client.factory.create('csExTIPLayerDataParmSetReqInParm')
    parmTIPLayerDataSetReqIn.Action = "Update"  # Insert/Update/Delete/ResetCnt
    parmTIPLayerData = client.factory.create('csExTIPLayerData')
    # parmTIPLayerData.tipNO = tip_no
    parmTIPLayerDataInfo = client.factory.create('csExTIPLayerDataInfo')
    # parmTIPLayerDataInfo.partName = mask_name
    parmTIPLayerDataInfo.lotID = lot_id
    if blank_code:
        blank = client.factory.create('csExTIPLayerData_Param')
        blank.name = "DP_BLANK_CODE"
        blank.type = "String"
        blank.value = blank_code
        blank.claimUserID.identifier = pptUser['userID']
        blank.claimTimeStamp = getMESDateStr()
        parmTIPLayerDataInfo.strExTIPLayerData_ParamSequence.item.append(blank)
    if pellicle_code:
        pellicle = client.factory.create('csExTIPLayerData_Param')
        pellicle.name = "DP_PELLICLE_CODE"
        pellicle.type = "String"
        pellicle.value = pellicle_code
        pellicle.claimUserID.identifier = pptUser['userID']
        parmTIPLayerDataInfo.strExTIPLayerData_ParamSequence.item.append(pellicle)
    parmTIPLayerData.strExTIPLayerDataInfoSequence.item.append(parmTIPLayerDataInfo)
    parmTIPLayerDataSetReqIn.strExTIPLayerData = parmTIPLayerData
    resultOutput = client.service.CS_TxExTIPLayerDataParmSetReq(paramUser, parmTIPLayerDataSetReqIn)
    if resultOutput.strResult.returnCode != "0":
        raise Exception(resultOutput.strResult.messageText)
    return resultOutput.strResult.returnCode


#  删除lot
@retry(stop_max_attempt_number=MES_RETRY_NUM, retry_on_exception=retry_if_url_error, wait_random_min=1000,
       wait_random_max=3000)
def MES_TxExTIPLayerDataParmDeleteLot(pptUser, tip_no, mask_name):
    paramUser = client.factory.create('pptUser')
    paramUser.userID.identifier = pptUser["userID"]
    paramUser.password = pptUser["password"]
    parmTIPLayerDataSetReqIn = client.factory.create('csExTIPLayerDataParmSetReqInParm')
    parmTIPLayerDataSetReqIn.Action = "Delete"  # Insert/Update/Delete/ResetCnt
    parmTIPLayerData = client.factory.create('csExTIPLayerData')
    parmTIPLayerData.tipNO = tip_no
    parmTIPLayerDataInfo = client.factory.create('csExTIPLayerDataInfo')
    parmTIPLayerDataInfo.partName = mask_name
    parmTIPLayerDataInfo.purpose = "TIP"
    # parmTIPLayerDataInfo.lotID = "MA100105.001"
    parmTIPLayerData.strExTIPLayerDataInfoSequence.item.append(parmTIPLayerDataInfo)
    parmTIPLayerDataSetReqIn.strExTIPLayerData = parmTIPLayerData
    resultOutput = client.service.CS_TxExTIPLayerDataParmSetReq(paramUser, parmTIPLayerDataSetReqIn)
    print(resultOutput)
    if resultOutput.strResult.returnCode != "0":
        raise Exception(resultOutput)
    return resultOutput.strResult.returnCode


# 设置参数生成lot_id
@retry(stop_max_attempt_number=MES_RETRY_NUM, retry_on_exception=retry_if_url_error, wait_random_min=1000,
       wait_random_max=3000)
def MES_TxExTIPLayerDataParmSetReq(pptUser, inParam):
    # Parameter 1: pptUser
    parmUser = client.factory.create('pptUser')
    parmUser.userID.identifier = pptUser['userID']
    parmUser.password = pptUser['password']
    parmTIPLayerDataSetReqIn = client.factory.create('csExTIPLayerDataParmSetReqInParm')
    parmTIPLayerDataSetReqIn.Action = inParam['Action']  # Insert/Update/Delete/ResetCnt
    parmTIPLayerData = client.factory.create('csExTIPLayerData')
    parmTIPLayerData.tipNO = inParam['tipNO']
    for info in inParam['strExTIPLayerDataInfoSequence']:
        layerDataInfo = client.factory.create('csExTIPLayerDataInfo')
        layerDataInfo.partName = info['partName']
        layerDataInfo.seq = info['seq']
        layerDataInfo.tone = info['tone']
        layerDataInfo.tipTech = info['tipTech']
        layerDataInfo.grade = info['grade']
        layerDataInfo.productType = info['productType']
        layerDataInfo.customerID = info['customerID']
        layerDataInfo.purpose = info['purpose']
        layerDataInfo.lotCreatedStatus = info['lotCreatedStatus']
        layerDataInfo.claimUserID.identifier = info['claimUserID']
        layerDataInfo.claimTimeStamp = info['claimTimeStamp']
        layerDataInfo.orderType = info['orderType']
        # exptool
        parm_exp_tool = client.factory.create('csExTIPLayerData_Param')
        parm_exp_tool.name = "DP_EXPTOOL"
        parm_exp_tool.type = "String"
        parm_exp_tool.value = info['paramExpTool']
        parm_exp_tool.claimUserID.identifier = info['customerID']
        parm_exp_tool.claimTimeStamp = info['claimTimeStamp']
        layerDataInfo.strExTIPLayerData_ParamSequence.item.append(parm_exp_tool)
        # blank_code
        parm_blank_code = client.factory.create('csExTIPLayerData_Param')
        parm_blank_code.name = "DP_BLANK_CODE"
        parm_blank_code.type = "String"
        parm_blank_code.value = info['paramBlankCode']
        parm_blank_code.claimUserID.identifier = info['customerID']
        parm_blank_code.claimTimeStamp = info['claimTimeStamp']
        layerDataInfo.strExTIPLayerData_ParamSequence.item.append(parm_blank_code)
        # pellicle_code
        parm_pellicle_code = client.factory.create('csExTIPLayerData_Param')
        parm_pellicle_code.name = "DP_PELLICLE_CODE"
        parm_pellicle_code.type = "String"
        parm_pellicle_code.value = info['paramPellicleCode']
        parm_pellicle_code.claimUserID.identifier = info['customerID']
        parm_pellicle_code.claimTimeStamp = info['claimTimeStamp']
        layerDataInfo.strExTIPLayerData_ParamSequence.item.append(parm_pellicle_code)
        # Design_Rule
        parm_design_rule = client.factory.create('csExTIPLayerData_Param')
        parm_design_rule.name = "DP_DESIGN_RULE"
        parm_design_rule.type = "String"
        parm_design_rule.value = info['paramDesignRule']
        parm_design_rule.claimUserID.identifier = info['customerID']
        parm_design_rule.claimTimeStamp = info['claimTimeStamp']
        layerDataInfo.strExTIPLayerData_ParamSequence.item.append(parm_design_rule)
        # Grade
        parm_grade = client.factory.create('csExTIPLayerData_Param')
        parm_grade.name = "DP_GRADE"
        parm_grade.type = "String"
        parm_grade.value = info['paramGrade']
        parm_grade.claimUserID.identifier = info['customerID']
        parm_grade.claimTimeStamp = info['claimTimeStamp']
        layerDataInfo.strExTIPLayerData_ParamSequence.item.append(parm_grade)
        # Tone
        parm_tone = client.factory.create('csExTIPLayerData_Param')
        parm_tone.name = "DP_TONE"
        parm_tone.type = "String"
        parm_tone.value = info['paramTone']
        parm_tone.claimUserID.identifier = info['customerID']
        parm_tone.claimTimeStamp = info['claimTimeStamp']
        layerDataInfo.strExTIPLayerData_ParamSequence.item.append(parm_tone)
        # Product_Type
        parm_product_type = client.factory.create('csExTIPLayerData_Param')
        parm_product_type.name = "DP_PRODUCT_TYPE"
        parm_product_type.type = "String"
        parm_product_type.value = info['paramProductType']
        parm_product_type.claimUserID.identifier = info['customerID']
        parm_product_type.claimTimeStamp = info['claimTimeStamp']
        layerDataInfo.strExTIPLayerData_ParamSequence.item.append(parm_product_type)
        # Delivery_Fab
        parm_delivery_fab = client.factory.create('csExTIPLayerData_Param')
        parm_delivery_fab.name = "DP_DELIVERY_FAB"
        parm_delivery_fab.type = "String"
        parm_delivery_fab.value = info['paramDeliveryFab']
        parm_delivery_fab.claimUserID.identifier = info['customerID']
        parm_delivery_fab.claimTimeStamp = info['claimTimeStamp']
        layerDataInfo.strExTIPLayerData_ParamSequence.item.append(parm_delivery_fab)
        # WaveLength
        parm_wavelength = client.factory.create('csExTIPLayerData_Param')
        parm_wavelength.name = "DP_WAVELENGTH"
        parm_wavelength.type = "String"
        parm_wavelength.value = info['paramWaveLength']
        parm_wavelength.claimUserID.identifier = info['customerID']
        parm_wavelength.claimTimeStamp = info['claimTimeStamp']
        layerDataInfo.strExTIPLayerData_ParamSequence.item.append(parm_wavelength)

        parmTIPLayerData.strExTIPLayerDataInfoSequence.item.append(layerDataInfo)
    parmTIPLayerDataSetReqIn.strExTIPLayerData = parmTIPLayerData
    # print("-----"*5)
    # print(parmTIPLayerDataSetReqIn)
    resultOutput = client.service.CS_TxExTIPLayerDataParmSetReq(parmUser, parmTIPLayerDataSetReqIn)
    # print("-----" * 5)
    # print(resultOutput)
    if resultOutput.strResult.returnCode != "0":
        raise Exception(resultOutput.strResult.messageText)
    return resultOutput


def MES_TxExTIPLayerDataParmSetReqForInherit(pptUser, info):
    parmUser = client.factory.create('pptUser')
    parmUser.userID.identifier = pptUser['userID']
    parmUser.password = pptUser['password']
    parmTIPLayerDataSetReqIn = client.factory.create('csExTIPLayerDataParmSetReqInParm')
    parmTIPLayerDataSetReqIn.Action = "Update"  # Insert/Update/Delete/ResetCnt
    parmTIPLayerData = client.factory.create('csExTIPLayerData')
    parmTIPLayerData.tipNO = info['tipNO']
    layerDataInfo = client.factory.create('csExTIPLayerDataInfo')
    layerDataInfo.partName = info['partName']
    # layerDataInfo.seq = info['seq']
    layerDataInfo.tone = info['tone']
    layerDataInfo.tipTech = info['tipTech']
    layerDataInfo.grade = info['grade']
    layerDataInfo.productType = info['productType']
    layerDataInfo.customerID = info['customerID']
    layerDataInfo.purpose = info['purpose']
    # layerDataInfo.lotCreatedStatus = info['lotCreatedStatus']
    layerDataInfo.claimUserID.identifier = info['claimUserID']
    layerDataInfo.claimTimeStamp = info['claimTimeStamp']
    layerDataInfo.orderType = info['orderType']
    # exptool
    parm_exp_tool = client.factory.create('csExTIPLayerData_Param')
    parm_exp_tool.name = "DP_EXPTOOL"
    parm_exp_tool.type = "String"
    parm_exp_tool.value = info['paramExpTool']
    parm_exp_tool.claimUserID.identifier = info['customerID']
    parm_exp_tool.claimTimeStamp = info['claimTimeStamp']
    layerDataInfo.strExTIPLayerData_ParamSequence.item.append(parm_exp_tool)
    # blank_code
    parm_blank_code = client.factory.create('csExTIPLayerData_Param')
    parm_blank_code.name = "DP_BLANK_CODE"
    parm_blank_code.type = "String"
    parm_blank_code.value = info['paramBlankCode']
    parm_blank_code.claimUserID.identifier = info['customerID']
    parm_blank_code.claimTimeStamp = info['claimTimeStamp']
    layerDataInfo.strExTIPLayerData_ParamSequence.item.append(parm_blank_code)
    # pellicle_code
    parm_pellicle_code = client.factory.create('csExTIPLayerData_Param')
    parm_pellicle_code.name = "DP_PELLICLE_CODE"
    parm_pellicle_code.type = "String"
    parm_pellicle_code.value = info['paramPellicleCode']
    parm_pellicle_code.claimUserID.identifier = info['customerID']
    parm_pellicle_code.claimTimeStamp = info['claimTimeStamp']
    layerDataInfo.strExTIPLayerData_ParamSequence.item.append(parm_pellicle_code)
    # Design_Rule
    parm_design_rule = client.factory.create('csExTIPLayerData_Param')
    parm_design_rule.name = "DP_DESIGN_RULE"
    parm_design_rule.type = "String"
    parm_design_rule.value = info['paramDesignRule']
    parm_design_rule.claimUserID.identifier = info['customerID']
    parm_design_rule.claimTimeStamp = info['claimTimeStamp']
    layerDataInfo.strExTIPLayerData_ParamSequence.item.append(parm_design_rule)
    # Grade
    parm_grade = client.factory.create('csExTIPLayerData_Param')
    parm_grade.name = "DP_GRADE"
    parm_grade.type = "String"
    parm_grade.value = info['paramGrade']
    parm_grade.claimUserID.identifier = info['customerID']
    parm_grade.claimTimeStamp = info['claimTimeStamp']
    layerDataInfo.strExTIPLayerData_ParamSequence.item.append(parm_grade)
    # Tone
    parm_tone = client.factory.create('csExTIPLayerData_Param')
    parm_tone.name = "DP_TONE"
    parm_tone.type = "String"
    parm_tone.value = info['paramTone']
    parm_tone.claimUserID.identifier = info['customerID']
    parm_tone.claimTimeStamp = info['claimTimeStamp']
    layerDataInfo.strExTIPLayerData_ParamSequence.item.append(parm_tone)
    # Product_Type
    parm_product_type = client.factory.create('csExTIPLayerData_Param')
    parm_product_type.name = "DP_PRODUCT_TYPE"
    parm_product_type.type = "String"
    parm_product_type.value = info['paramProductType']
    parm_product_type.claimUserID.identifier = info['customerID']
    parm_product_type.claimTimeStamp = info['claimTimeStamp']
    layerDataInfo.strExTIPLayerData_ParamSequence.item.append(parm_product_type)
    # Delivery_Fab
    parm_delivery_fab = client.factory.create('csExTIPLayerData_Param')
    parm_delivery_fab.name = "DP_DELIVERY_FAB"
    parm_delivery_fab.type = "String"
    parm_delivery_fab.value = info['paramDeliveryFab']
    parm_delivery_fab.claimUserID.identifier = info['customerID']
    parm_delivery_fab.claimTimeStamp = info['claimTimeStamp']
    layerDataInfo.strExTIPLayerData_ParamSequence.item.append(parm_delivery_fab)
    # WaveLength
    parm_wavelength = client.factory.create('csExTIPLayerData_Param')
    parm_wavelength.name = "DP_WAVELENGTH"
    parm_wavelength.type = "String"
    parm_wavelength.value = info['paramWaveLength']
    parm_wavelength.claimUserID.identifier = info['customerID']
    parm_wavelength.claimTimeStamp = info['claimTimeStamp']
    layerDataInfo.strExTIPLayerData_ParamSequence.item.append(parm_wavelength)

    parmTIPLayerData.strExTIPLayerDataInfoSequence.item.append(layerDataInfo)
    parmTIPLayerDataSetReqIn.strExTIPLayerData = parmTIPLayerData
    # print("-----"*5)
    # print(parmTIPLayerDataSetReqIn)
    resultOutput = client.service.CS_TxExTIPLayerDataParmSetReq(parmUser, parmTIPLayerDataSetReqIn)
    # print("-----" * 5)
    # print(resultOutput)
    if resultOutput.strResult.returnCode != "0":
        raise Exception(resultOutput.strResult.messageText)
    return resultOutput


# 根据最近的时间查询lot_id
@retry(stop_max_attempt_number=MES_RETRY_NUM, retry_on_exception=retry_if_url_error, wait_random_min=1000,
       wait_random_max=3000)
def MES_TxExTIPLayerDataParmInq(ppt_User, tip_no, part_name):
    parmUser = client.factory.create('pptUser')
    parmUser.userID.identifier = ppt_User['userID']
    parmUser.password = ppt_User['password']
    parmTIPLayerDataParmInqInParm = client.factory.create('csExTIPLayerDataParmInqInParm')
    parmTIPLayerDataParmInqInParm.purpose = 'Tip'
    if tip_no:
        parmTIPLayerDataParmInqInParm.tipNO = tip_no
    if part_name:
        parmTIPLayerDataParmInqInParm.partName = part_name
    resultOutput = client.service.CS_TxExTIPLayerDataParmInq(parmUser, parmTIPLayerDataParmInqInParm)
    if resultOutput.strResult.returnCode != "0":
        raise Exception(resultOutput.strResult.messageText)
    return resultOutput


def MES_TxExTIPLayerDataParmBackUpInq(ppt_User, tip_no, part_name):
    parmUser = client.factory.create('pptUser')
    parmUser.userID.identifier = ppt_User['userID']
    parmUser.password = ppt_User['password']
    parmTIPLayerDataParmInqInParm = client.factory.create('csExTIPLayerDataParmInqInParm')
    parmTIPLayerDataParmInqInParm.purpose = 'Backup'
    if tip_no:
        parmTIPLayerDataParmInqInParm.tipNO = tip_no
    if part_name:
        parmTIPLayerDataParmInqInParm.partName = part_name
    resultOutput = client.service.CS_TxExTIPLayerDataParmInq(parmUser, parmTIPLayerDataParmInqInParm)
    if resultOutput.strResult.returnCode != "0":
        raise Exception(resultOutput.strResult.messageText)
    return resultOutput


def MES_TxExTIPLayerDataParmInqForLotID(ppt_User, lot_id):
    parmUser = client.factory.create('pptUser')
    parmUser.userID.identifier = ppt_User['userID']
    parmUser.password = ppt_User['password']
    parmTIPLayerDataParmInqInParm = client.factory.create('csExTIPLayerDataParmInqInParm')
    parmTIPLayerDataParmInqInParm.purpose = 'Tip'
    parmTIPLayerDataParmInqInParm.lotID = lot_id
    resultOutput = client.service.CS_TxExTIPLayerDataParmInq(parmUser, parmTIPLayerDataParmInqInParm)
    if resultOutput.strResult.returnCode != "0":
        raise Exception(resultOutput.strResult.messageText)
    return resultOutput



# RunningHoldReq
@retry(stop_max_attempt_number=MES_RETRY_NUM, retry_on_exception=retry_if_url_error, wait_random_min=1000,
       wait_random_max=3000)
def MES_TxRunningHoldReq(pptUser,
                         equipmentID,
                         holdReasonCodeID,
                         controlJobID,
                         claimMemo):
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

    # Paramrter 4: holdReasonCodeID
    paramholdReasonCodeID = client.factory.create('objectIdentifier')
    paramholdReasonCodeID.identifier = holdReasonCodeID

    # Paramrter 5: claimMemo
    paramclaimMemo = claimMemo or ''

    resultOutput = client.service.TxOpeCompWithDataReq(paramUser, paramEQPID, paramControlJobID,
                                                       paramholdReasonCodeID, paramclaimMemo)
    if resultOutput.strResult.returnCode != "0":
        raise Exception(resultOutput.strResult.messageText)
    return resultOutput


@retry(stop_max_attempt_number=MES_RETRY_NUM, retry_on_exception=retry_if_url_error, wait_random_min=1000,
       wait_random_max=3000)
def TxLotOperationListInq__160(ppt_user, _lot_id):
    parmUser = client.factory.create('pptUser')
    parmUser.userID.identifier = ppt_user['userID']
    parmUser.password = ppt_user['password']
    searchDirection = True
    posSearchFlag = True
    searchCount = 100
    currentFlag = True
    lot_id = client.factory.create('objectIdentifier')
    lot_id.identifier = _lot_id
    result = client.service.TxLotOperationListInq__160(parmUser, searchDirection, posSearchFlag, searchCount,
                                                       currentFlag, lot_id)
    if result.strResult.returnCode != "0":
        raise Exception(result.strResult.messageText)
    return result


@retry(stop_max_attempt_number=MES_RETRY_NUM, retry_on_exception=retry_if_url_error, wait_random_min=1000,
       wait_random_max=3000)
def TxRouteOperationListInq__160(ppt_user, route_id):
    """查询route下的所有operation"""
    parmUser = client.factory.create('pptUser')
    parmUser.userID.identifier = ppt_user['userID']
    parmUser.password = ppt_user['password']
    routeID = client.factory.create('objectIdentifier')
    routeID.identifier = route_id
    nil = client.factory.create('objectIdentifier')
    result = client.service.TxRouteOperationListInq__160(parmUser, routeID, nil, '', '', 100)
    if result.strResult.returnCode != "0":
        raise Exception(result.strResult.messageText)
    return result


@retry(stop_max_attempt_number=MES_RETRY_NUM, retry_on_exception=retry_if_url_error, wait_random_min=1000,
       wait_random_max=3000)
def MES_TxEqpInfoInq(pptUser, equipmentID):
    # Parameter 1: pptUser
    paramUser = client.factory.create('pptUser')
    paramUser.userID.identifier = pptUser["userID"]
    paramUser.password = pptUser["password"]

    # Parameter 2: equipmentID
    paramEQPID = client.factory.create('objectIdentifier')
    paramEQPID.identifier = equipmentID

    result = client.service.TxEqpInfoInq__160(paramUser, paramEQPID, True, True, True, True, True, True, True
                                                         , True, True, True)
    if result.strResult.returnCode != "0":
        raise Exception(result.strResult.messageText)
    return result.equipmentStatusInfo.equipmentStatusCode.identifier


@retry(stop_max_attempt_number=MES_RETRY_NUM, retry_on_exception=retry_if_url_error, wait_random_min=1000,
       wait_random_max=3000)
def MES_TxOpeLocateReq(pptUser, lot_id, route_id, old_op_num, op_id, op_num, remark):
    # Parameter 1: pptUser
    paramUser = client.factory.create('pptUser')
    paramUser.userID.identifier = pptUser["userID"]
    paramUser.password = pptUser["password"]
    # Parameter 2: lotID
    lotID = client.factory.create('objectIdentifier')
    lotID.identifier = lot_id
    # routeID
    routeID = client.factory.create('objectIdentifier')
    routeID.identifier = route_id
    # operationID
    operationID = client.factory.create('objectIdentifier')
    operationID.identifier = op_id
    # pptProcessRef
    processRef = client.factory.create('pptProcessRef')
    result = client.service.TxOpeLocateReq(paramUser, False, lotID, routeID, old_op_num, routeID, operationID, op_num,
                                           processRef, 1, remark)
    if result.strResult.returnCode != "0":
        raise Exception(result.strResult.messageText)
    return result


def MES_TxLoadingLotRpt(pptUser, equipmentID, cassetteID, remark):
    paramUser = client.factory.create('pptUser')
    paramUser.userID.identifier = pptUser["userID"]
    paramUser.password = pptUser["password"]

    parmEquipmentID = client.factory.create('objectIdentifier')
    parmEquipmentID.identifier = equipmentID

    parmCassetteID = client.factory.create('objectIdentifier')
    parmCassetteID.identifier = cassetteID

    parmPortID = client.factory.create('objectIdentifier')
    parmPortID.identifier = "PORT1"

    result = client.service.TxLoadingLotRpt(paramUser, parmEquipmentID, parmCassetteID, parmPortID, "Process Lot",
                                            remark)
    return result


def MES_TxUnloadingLotRpt(pptUser, equipmentID, cassetteID, remark):
    paramUser = client.factory.create('pptUser')
    paramUser.userID.identifier = pptUser["userID"]
    paramUser.password = pptUser["password"]

    parmEquipmentID = client.factory.create('objectIdentifier')
    parmEquipmentID.identifier = equipmentID

    parmCassetteID = client.factory.create('objectIdentifier')
    parmCassetteID.identifier = cassetteID

    parmPortID = client.factory.create('objectIdentifier')
    parmPortID.identifier = "PORT1"

    result = client.service.TxUnloadingLotRpt(paramUser, parmEquipmentID, parmCassetteID, parmPortID, remark)
    return result
