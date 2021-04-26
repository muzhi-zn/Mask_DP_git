#!/usr/bin/python3
import os
import traceback

from suds.client import Client

# from utilslibrary.mes_webservice import mes_utils

client = Client('file:///C:\\workspace\\DP_Phase1\\utilslibrary\\mes_webservice\\'+
                'MES_FILES/MMS_CS/wsdl/CS_PPTServiceManager.wsdl',
                location="http://10.3.10.30:27111/CS_PPTServiceManager/thePPTServiceManager", cache=None)


#######################################################################
# pptLotListInqResult__180 TxLotListInq__180
# (
#    in pptUser          requestUserID,
#    in objectIdentifier bankID,
#    in string           lotStatus,
#    in string           lotType,
#    in objectIdentifier productID,
#    in string           orderNumber,
#    in string           customerCode,
#    in objectIdentifier manufacturingLayerID,
#    in objectIdentifier routeID,
#    in string           operationNumber,
#    in boolean          bankInRequiredFlag,
#    in objectIdentifier lotID,
#    in string           requiredCassetteCategory,
#    in boolean          backupProcessingFlag,
#    in string           subLotType,
#    in boolean          deleteLotFlag,
#    in objectIdentifier holdReasonCodeID,
#    in boolean          sorterJobCreationCheckFlag,
#    in string           interFabXferState,
#    in boolean          autoDispatchControlLotFlag,
#    in boolean          virtualOperationFlag,
#    in objectIdentifier operationID
# )
def MES_TxLotListInq(operationNumber, bVirturalOperation):
    # Parameter 1: pptUser
    parmUser = client.factory.create('pptUser')
    parmUser.userID.identifier = "DP_Test"
    parmUser.password = "utfU`QE"

    parmObjectIdentifier = client.factory.create('objectIdentifier')

    lotID = client.factory.create('objectIdentifier')
    lotID.identifier = 'MA100264.001'  # QA000257.001
    # lotID.identifier = 'QA000257.001'
    opNumberIdentifier = client.factory.create('objectIdentifier')
    opNumberIdentifier.identifier = operationNumber
    print(client)
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
    print(resultOutput)
    if resultOutput.strResult.returnCode != "0":
        raise Exception(resultOutput.strResult.messageText)
    return resultOutput.strLotListAttributes


###############################################################################################################
# typedef struct pptLotListAttributes__180_struct {
#    objectIdentifier         lotID;                                 //<i>Lot ID
#    string                   lotType;                               //<i>Lot Type
#    string                   lotStatus;                             //<i>Lot Status
#    pptLotStatusListSequence strLotStatusList;                      //<i>Sequence of Lot Status List
#    objectIdentifier         bankID;                                //<i>Bank ID
#    string                   orderNumber;                           //<i>Order Number
#    string                   customerCode;                          //<i>Customer Code
#    objectIdentifier         productID;                             //<i>Product ID
#    string                   lastClaimedTimeStamp;                  //<i>Last Claimed Time Stamp
#    string                   dueTimeStamp;                          //<i>Due Time Stamp
#    objectIdentifier         routeID;                               //<i>Route ID
#    string                   operationNumber;                       //<i>Operation Number
#    long                     totalWaferCount;                       //<i>Total Wafer Count
#    boolean                  bankInRequiredFlag;                    //<i>Bank In Required Flag
#    string                   controlUseState;                       //<i>Control Use State
#    long                     usedCount;                             //<i>Used Count
#    string                   completionTimeStamp;                   //<i>Completion Time Stamp
#    objectIdentifier         lotFamilyID;                           //<i>Lot Family ID
#    objectIdentifier         productRequestID;                      //<i>Product Request ID
#    string                   subLotType;                            //<i>Sub Lot Type
#    objectIdentifier         lotOwnerID;                            //<i>Lot Owner ID
#    string                   requiredCassetteCategory;              //<i>Required Carrier Category
#    pptLotBackupInfo         strLotBackupInfo;                      //<i>Lot Backup Info
#    objectIdentifier         carrierID;                             //<i>Carrier ID
#    objectIdentifier         equipmentID;                           //<i>Equipment ID
#    objectIdentifier         holdReasonCodeID;                      //<i>Hold Reason Code ID
#    boolean                  sorterJobExistFlag;                    //<i>Sorter Job Existence Flag
#    boolean                  inPostProcessFlagOfCassette;           //<i>InPostProcessFlag of Cassette
#    boolean                  inPostProcessFlagOfLot;                //<i>InPostProcessFlag of Lot
#    string                   interFabXferState;                     //<i>interFab Xfer State
#    string                   bondingGroupID;                        //<i>Bonding Group ID
#    boolean                  autoDispatchControlFlag;               //<i>Auto Dispatch Control Flag
#    objectIdentifier         eqpMonitorJobID;                       //<i>Equipment Monitor Job ID
#    objectIdentifier         operationID;                           //<i>Operation ID
#    string                   pdType;                                //<i>Process Definition Type
#    string                   scheduleMode;                          //<i>PD Type
#    string                   planStartTimeStamp;                    //<i>Plan Start Time
#    long                     priorityClass;                         //<i>Priority Class
#    boolean                  lotInfoChangeFlag;                     //<i>Lot Info Change Flag
#    any                      siInfo;                                //<i>Reserved for SI customization
# } pptLotListAttributes__180;
#
# typedef sequence <pptLotListAttributes__180> pptLotListAttributesSequence__180;
#
# typedef struct pptLotListInqResult__180_struct {
#    pptRetCode                        strResult;                    //<i>Transaction Execution Result Information
#    pptLotListAttributesSequence__180 strLotListAttributes;         //<i>Sequence of Lot List Attributes
#    any                               siInfo;                       //<i>Reserved for SI customization
# } pptLotListInqResult__180;
try:
    lots = MES_TxLotListInq('MRDODR.1', False)
    for lot in lots.item:
        print(lot.lotID.identifier)
        print(lot.carrierID.identifier)
        print(lot.lotStatus)
except Exception as ex:
    traceback.print_exc()

print("OK!!")
