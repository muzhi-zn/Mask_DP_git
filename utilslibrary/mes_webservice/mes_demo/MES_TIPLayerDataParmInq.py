#!/usr/bin/python3
import os


from suds.client import Client

##自定义

client = Client('file:///C:\\workspace\\DP_Phase1\\utilslibrary\\mes_webservice\\'+
                'MES_FILES/MMS_CS/wsdl/CS_PPTServiceManager.wsdl',
                location="http://10.3.10.30:27111/CS_PPTServiceManager/thePPTServiceManager", cache=None)

# Parameter 1: csExTIPLayerDataParmInqInParm
# typedef struct csExTIPLayerDataParmInqInParm_struct {
#    string                         tipNO;
#    string                         partName;
#    long                           seq;
#    string                         tone;
#    string                         tipTech;
#    string                         grade;
#    string                         orderType;           //REQ-00001-03
#    string                         productType;
#    string                         customerID;
#    string                         purpose;             //TIP,Scrap,Backup
#    string                         lotID;
#    string                         lotCreatedStatus;
#    string                         result;
#    long                           retryCnt;
#    objectIdentifier               claimUserID;
#    string                         claimTimeStamp;
#    string                         claimTimeOperator;
#    any         siInfo;
# } csExTIPLayerDataParmInqInParm;
parmTIPLayerDataParmInqInParm = client.factory.create('csExTIPLayerDataParmInqInParm')
#      Get latest claim time from config file.
# parmTIPLayerDataParmInqInParm.claimUserID.identifier = 'DP_Test'
# parmTIPLayerDataParmInqInParm.claimTimeStamp = '2020-03-05-22.20.10.000000'
# parmTIPLayerDataParmInqInParm.claimTimeOperator = 'DP_Test'
parmTIPLayerDataParmInqInParm.purpose = 'Tip'
# parmTIPLayerDataParmInqInParm.lotID = 'MB200010.001'
# parmTIPLayerDataParmInqInParm.tipNO = 'TP0210129-5'
parmTIPLayerDataParmInqInParm.partName = 'TES998-120A1'


#########################################################################################################
# typedef struct pptRetCode_struct {
#    string transactionID;  //<i>Transaction ID
#    string returnCode;     //<i>Return Code
#    string messageID;      //<i>Message ID
#    string messageText;    //<i>Message Text
#    string reasonText;     //<i>Reason Text
#    any siInfo;            //<i>Reserved for SI customization
# } pptRetCode;
#
# typedef struct csExTIPLayerDataParmInqResult_struct {
#    pptRetCode        strResult;
#    //REQ-00001-04 csExTIPLayerData  strExTIPLayerData;
#    csExTIPLayerDataSequence strExTIPLayerData;       //REQ-00001-04
#    any               siInfo;
# } csExTIPLayerDataParmInqResult;
#
# csExTIPLayerDataParmInqResult CS_TxExTIPLayerDataParmInq
# (
#    in pptUser                        requestUserID,
#    in csExTIPLayerDataParmInqInParm  strExTIPLayerDataParmInqInParm
# )
def MES_TxExTIPLayerDataParmInq(strExTIPLayerDataParmInqInParm):
    # Parameter 1: pptUser
    parmUser = client.factory.create('pptUser')
    parmUser.userID.identifier = "DP_Test"
    parmUser.password = "utfU`QE"
    print("-----" * 8)
    print(strExTIPLayerDataParmInqInParm)
    resultOutput = client.service.CS_TxExTIPLayerDataParmInq(parmUser, strExTIPLayerDataParmInqInParm)
    print("-----" * 8)
    print(resultOutput)
    print("-----" * 8)
    # print(resultOutput.strExTIPLayerData.item[0])
    print("-----" * 8)
    print(len(resultOutput.strExTIPLayerData.item[0].strExTIPLayerDataInfoSequence.item))
    if resultOutput.strResult.returnCode != "0":
        raise Exception(resultOutput.strResult.messageText)
    return resultOutput.strExTIPLayerData


# typedef struct csExTIPLayerData_Param_struct {
#    string                 name;
#    string                 type;
#    string                 value;
#    objectIdentifier       claimUserID;
#    string                 claimTimeStamp;
#    any                    siInfo;
# } csExTIPLayerData_Param;
#
# typedef sequence <csExTIPLayerData_Param> csExTIPLayerData_ParamSequence;
#
# typedef struct csExTIPLayerDataInfo_struct {
#    string                         partName;
#    long                           seq;
#    string                         tone;
#    string                         tipTech;
#    string                         grade;
#    string                         productType;
#    string                         customerID;
#    string                         purpose;             //TIP,Scrap,Backup
#    string                         lotID;
#    string                         lotCreatedStatus;
#    string                         result;
#    long                           retryCnt;
#    objectIdentifier               claimUserID;
#    string                         claimTimeStamp;
#    csExTIPLayerData_ParamSequence strExTIPLayerData_ParamSequence;
#    string                         orderType;//added by chenyang for compile error
#    any                            siInfo;
# } csExTIPLayerDataInfo;
#
# typedef sequence <csExTIPLayerDataInfo> csExTIPLayerDataInfoSequence;
#
# typedef struct csExTIPLayerData_struct {
#    string                         tipNO;
#    csExTIPLayerDataInfoSequence   strExTIPLayerDataInfoSequence;
#    any                            siInfo;
# } csExTIPLayerData;
#
# typedef sequence <csExTIPLayerData> csExTIPLayerDataSequence;

# try:
#     tipLayerDataSeq = MES_TxExTIPLayerDataParmInq(parmTIPLayerDataParmInqInParm)

# # Sort ClaimTime & remove the same ClaimTime
# lstSortClaimTime = []
# for tipLayerData in tipLayerDataSeq.item:
#     for tipLayerInfo in tipLayerData.strExTIPLayerDataInfoSequence.item:
#         if tipLayerInfo.claimTimeStamp not in lstSortClaimTime:
#             lstSortClaimTime.append(tipLayerInfo.claimTimeStamp)
# lstSortClaimTime.sort()
#
# # Sort orginal TipLayerData by lstSortClaimTime
# sortedTipLayerDataSeq = client.factory.create('csExTIPLayerDataSequence')
# for claimTime in lstSortClaimTime:
#     for tipLayerData in tipLayerDataSeq.item:
#         for tipLayerInfo in tipLayerData.strExTIPLayerDataInfoSequence.item:
#             if claimTime == tipLayerInfo.claimTimeStamp:
#                 sortedTipLayerDataSeq.append(tipLayerData)
#
# for tipLayerData in sortedTipLayerDataSeq.item:
#     tipNO = tipLayerData.tipNO
#     for tipInfo in tipLayerData.strExTIPLayerDataInfoSequence.item:
#         partName = tipInfo.partName
#         seq = tipInfo.seq
#         tone = tipInfo.tone
#         tipTech = tipInfo.tipTech
#         grade = tipInfo.grade
#         productType = tipInfo.productType
#         customerID = tipInfo.customerID
#         purpose = tipInfo.purpose
#         lotID = tipInfo.lotID
#         lotCreatedStatus = tipInfo.lotCreatedStatus
#         result = tipInfo.result
#         retryCnt = tipInfo.retryCnt
#         claimUserID = tipInfo.claimUserID
#         claimTimeStamp = tipInfo.claimTimeStamp
#         orderType = tipInfo.orderType

# Update lotID back to DP Automation Database
# 1. If lotID field is empty in Database for target record, then update this lotID back to record
# 2. Else If lotID field is not empty in Database for target record, then copy this record and put this lotID to new record
# coding here ....

# qxconfig.cf.set("AGENT", "last_claimtime", claimTimeStamp)
# qxconfig.cf.write(open("config.ini", "w"))

# except Exception as ex:
#     print(ex)
#
# print("OK!!")

def test_xxx():
    tipLayerDataSeq = MES_TxExTIPLayerDataParmInq(parmTIPLayerDataParmInqInParm)


def test_x():
    print(client)
    parmUser = client.factory.create('pptUser')
    parmUser.userID.identifier = "DP_Test"
    parmUser.password = "utfU`QE"
    n = client.factory.create('objectIdentifier')
    parmLot = client.factory.create('objectIdentifier')
    parmLot.identifier = "QA000133.001"
    eid = client.factory.create('objectIdentifier')
    eid.identifier = 'MDCOM01'
    cid = client.factory.create('objectIdentifier')
    cid.identifier = 'MDCOM01-20200415-0012'
    hid = client.factory.create('objectIdentifier')
    hid.identifier = 'RNHL'

    result = client.service.TxRunningHoldReq(parmUser, n, cid, hid, '')
    print(result)


def test_VirtualOperationLotList():
    parmUser = client.factory.create('pptUser')
    parmUser.userID.identifier = "DP_Test"
    parmUser.password = "utfU`QE"
    p = client.factory.create("pptVirtualOperationLotListInqInParam")
    routeID = client.factory.create('objectIdentifier')
    routeID.identifier = 'RR_OMOG.1'
    p.routeID = routeID
    p.operationNumber = '100.500'
    operationID = client.factory.create('objectIdentifier')
    operationID.identifier = 'MRDODR.1'
    p.operationID = operationID
    p.selectCriteria = 'SALL'
    # SP_DP_SelectCriteria_All = 'SALL'
    # SP_DP_SelectCriteria_CanBeProcessed = 'SAVL'
    # SP_DP_SelectCriteria_Hold = 'SHLD'
    result = client.service.TxVirtualOperationLotListInq(parmUser, p)
    print(result)


def test_OperationList():
    # TxLotOperationListInq__160(pptUser requestUserID, xs:boolean searchDirection, xs:boolean posSearchFlag, xs:int searchCount, xs:boolean currentFlag, objectIdentifier lotID)
    parmUser = client.factory.create('pptUser')
    parmUser.userID.identifier = "DP_Test"
    parmUser.password = "utfU`QE"
    searchDirection = True
    posSearchFlag = True
    searchCount = 100
    currentFlag = True
    lot_id = client.factory.create('objectIdentifier')
    lot_id.identifier = 'MA100039.001'
    result = client.service.TxLotOperationListInq__160(parmUser, searchDirection, posSearchFlag, searchCount,
                                                       currentFlag, lot_id)
    print(result)


# OMOG_01.1
def test_RouteOperationList():
    parmUser = client.factory.create('pptUser')
    parmUser.userID.identifier = "DP_Test"
    parmUser.password = "utfU`QE"
    route_id = client.factory.create('objectIdentifier')
    route_id.identifier = 'RR_OMOG.1'
    n = client.factory.create('objectIdentifier')
    operation_id = client.factory.create('objectIdentifier')
    operation_id.identifier = 'MCDTPC.1'
    result = client.service.TxRouteOperationListInq__160(parmUser, route_id, n, '', '', 100)
    print(result)


def test_TxLotsInfoForOpeStartInq():
    parmUser = client.factory.create('pptUser')
    parmUser.userID.identifier = "DP_Test"
    parmUser.password = "utfU`QE"
    equipmentID = client.factory.create('objectIdentifier')
    equipmentID.identifier = 'MDCOM01'
    parmCassetteIDSequence = client.factory.create('objectIdentifierSequence')
    parmCassetteID = client.factory.create('objectIdentifier')
    parmCassetteID.identifier = "MA10003A"
    parmCassetteIDSequence.item.append(parmCassetteID)
    resultLotsInfoOutput = client.service.TxLotsInfoForOpeStartInq(parmUser, equipmentID, parmCassetteIDSequence)
    print(resultLotsInfoOutput)


if __name__ == '__main__':
    test_xxx()
    # test_VirtualOperationLotList()
    # print(client)
    # test_RouteOperationList()
    # test_xxx()
    # test_TxLotsInfoForOpeStartInq()
    # test_OperationList()
