#!/usr/bin/python3
from suds.client import Client

# from utilslibrary.mes_webservice import mes_utils

# client = mes_utils.get_ws_client()
client = Client('file:///C:\\workspace\\DP_Phase1\\utilslibrary\\mes_webservice\\'+
                'MES_FILES/MMS_CS/wsdl/CS_PPTServiceManager.wsdl',
                location="http://10.3.16.30:17101/CS_PPTServiceManager/thePPTServiceManager", cache=None)

# Parameter 1: csExTIPLayerDataParmSetReqInParm
#   typedef struct csExTIPLayerDataParmSetReqInParm_struct {
#      csExTIPLayerData  strExTIPLayerData;
#      string            Action;
#      any               siInfo;
#   } csExTIPLayerDataParmSetReqInParm;
parmTIPLayerDataSetReqIn = client.factory.create('csExTIPLayerDataParmSetReqInParm')
parmTIPLayerDataSetReqIn.Action = "Update"  #  Insert/Update/Delete/ResetCnt

#     Parameter 1.1: csExTIPLayerData
#       typedef struct csExTIPLayerData_struct {
#          string                         tipNO;
#          csExTIPLayerDataInfoSequence   strExTIPLayerDataInfoSequence;
#          any                            siInfo;
#       } csExTIPLayerData;
parmTIPLayerData = client.factory.create('csExTIPLayerData')
parmTIPLayerData.tipNO = "TP0210129-5"

#         Parameter 1.1.2: csExTIPLayerDataInfo
#           typedef struct csExTIPLayerDataInfo_struct {
#              string                         partName;
#              long                           seq;
#              string                         tone;
#              string                         tipTech;
#              string                         grade;
#              string                         productType;
#              string                         customerID;
#              string                         purpose;             //TIP,Scrap,Backup
#              string                         lotID;
#              string                         lotCreatedStatus;
#              string                         result;
#              long                           retryCnt;
#              objectIdentifier               claimUserID;
#              string                         claimTimeStamp;
#              csExTIPLayerData_ParamSequence strExTIPLayerData_ParamSequence;
#              string                         orderType;//added by chenyang for compile error
#              any                            siInfo;
#           } csExTIPLayerDataInfo;
#    start loop layers
parmTIPLayerDataInfo = client.factory.create('csExTIPLayerDataInfo')
parmTIPLayerDataInfo.partName = "Y0131-156A-1NK4"
# parmTIPLayerDataInfo.seq = 1
# parmTIPLayerDataInfo.tone = "Tone"
# parmTIPLayerDataInfo.tipTech = "TipTech"
# parmTIPLayerDataInfo.grade = "Grade"
# parmTIPLayerDataInfo.productType = "ProductType"
# parmTIPLayerDataInfo.customerID = "Customer"
# parmTIPLayerDataInfo.purpose = "TIP"
parmTIPLayerDataInfo.lotID = "MB100007.001"
# parmTIPLayerDataInfo.claimUserID.identifier = "User"
# parmTIPLayerDataInfo.claimTimeStamp = "2020-03-05-22.20.00.000000"
# parmTIPLayerDataInfo.orderType = "OrderType"  # ask IBM

#             Parameter 1.1.2.15: csExTIPLayerDataInfo
#               typedef struct csExTIPLayerData_Param_struct {
#                  string                 name;
#                  string                 type;
#                  string                 value;
#                  objectIdentifier       claimUserID;
#                  string                 claimTimeStamp;
#                  any                    siInfo;
#               } csExTIPLayerData_Param;
#         start loop parameters
# parmTIPLayerData_Param = client.factory.create('csExTIPLayerData_Param')
# parmTIPLayerData_Param.name = "DP_EXPTOOL"
# parmTIPLayerData_Param.type = "String"  # ask IBM
# parmTIPLayerData_Param.value = "1A-0.0005"
# parmTIPLayerData_Param.claimUserID.identifier = "RichardGao"
# parmTIPLayerData_Param.claimTimeStamp = "2021-01-21-15.52.00.000000"
#
# parmTIPLayerDataInfo.strExTIPLayerData_ParamSequence.item.append(parmTIPLayerData_Param)
#
# parmTIPLayerData_Param1 = client.factory.create('csExTIPLayerData_Param')
# parmTIPLayerData_Param1.name = "DP_BLANK_CODE"
# parmTIPLayerData_Param1.type = "String"  # ask IBM
# parmTIPLayerData_Param1.value = "BK03"
# parmTIPLayerData_Param1.claimUserID.identifier = "RichardGao"
# parmTIPLayerData_Param1.claimTimeStamp = "2021-01-21-15.52.00.000000"
#
# parmTIPLayerDataInfo.strExTIPLayerData_ParamSequence.item.append(parmTIPLayerData_Param1)
#
# parmTIPLayerData_Param2 = client.factory.create('csExTIPLayerData_Param')
# parmTIPLayerData_Param2.name = "DP_PELLICLE_CODE"
# parmTIPLayerData_Param2.type = "String"  # ask IBM
# parmTIPLayerData_Param2.value = "P01"
# parmTIPLayerData_Param2.claimUserID.identifier = "RichardGao"
# parmTIPLayerData_Param2.claimTimeStamp = "2021-01-21-15.52.00.000000"
#
# parmTIPLayerDataInfo.strExTIPLayerData_ParamSequence.item.append(parmTIPLayerData_Param2)

parmTIPLayerData_Param3 = client.factory.create('csExTIPLayerData_Param')
parmTIPLayerData_Param3.name = "DP_DESIGN_RULE"
parmTIPLayerData_Param3.type = "String"  # ask IBM
parmTIPLayerData_Param3.value = "0.13"
parmTIPLayerData_Param3.claimUserID.identifier = "RichardGao"
parmTIPLayerData_Param3.claimTimeStamp = "2021-02-02-10.45.00.000000"

parmTIPLayerDataInfo.strExTIPLayerData_ParamSequence.item.append(parmTIPLayerData_Param3)
#
# parmTIPLayerData_Param4 = client.factory.create('csExTIPLayerData_Param')
# parmTIPLayerData_Param4.name = "DP_GRADE"
# parmTIPLayerData_Param4.type = "String"  # ask IBM
# parmTIPLayerData_Param4.value = "L"
# parmTIPLayerData_Param4.claimUserID.identifier = "RichardGao"
# parmTIPLayerData_Param4.claimTimeStamp = "2021-01-21-15.52.00.000000"
#
# parmTIPLayerDataInfo.strExTIPLayerData_ParamSequence.item.append(parmTIPLayerData_Param4)
#
# parmTIPLayerData_Param5 = client.factory.create('csExTIPLayerData_Param')
# parmTIPLayerData_Param5.name = "DP_TONE"
# parmTIPLayerData_Param5.type = "String"  # ask IBM
# parmTIPLayerData_Param5.value = "C"
# parmTIPLayerData_Param5.claimUserID.identifier = "RichardGao"
# parmTIPLayerData_Param5.claimTimeStamp = "2021-01-21-15.52.00.000000"
#
# parmTIPLayerDataInfo.strExTIPLayerData_ParamSequence.item.append(parmTIPLayerData_Param5)
#
# parmTIPLayerData_Param6 = client.factory.create('csExTIPLayerData_Param')
# parmTIPLayerData_Param6.name = "DP_PRODUCT_TYPE"
# parmTIPLayerData_Param6.type = "String"  # ask IBM
# parmTIPLayerData_Param6.value = "BIN"
# parmTIPLayerData_Param6.claimUserID.identifier = "RichardGao"
# parmTIPLayerData_Param6.claimTimeStamp = "2021-01-21-15.52.00.000000"
#
# parmTIPLayerDataInfo.strExTIPLayerData_ParamSequence.item.append(parmTIPLayerData_Param6)
#
# parmTIPLayerData_Param7 = client.factory.create('csExTIPLayerData_Param')
# parmTIPLayerData_Param7.name = "DP_DELIVERY_FAB"
# parmTIPLayerData_Param7.type = "String"  # ask IBM
# parmTIPLayerData_Param7.value = "QXIC"
# parmTIPLayerData_Param7.claimUserID.identifier = "RichardGao"
# parmTIPLayerData_Param7.claimTimeStamp = "2021-01-21-15.52.00.000000"
#
# parmTIPLayerDataInfo.strExTIPLayerData_ParamSequence.item.append(parmTIPLayerData_Param7)
#
# parmTIPLayerData_Param8 = client.factory.create('csExTIPLayerData_Param')
# parmTIPLayerData_Param8.name = "DP_WAVELENGTH"
# parmTIPLayerData_Param8.type = "String"  # ask IBM
# parmTIPLayerData_Param8.value = "248"
# parmTIPLayerData_Param8.claimUserID.identifier = "RichardGao"
# parmTIPLayerData_Param8.claimTimeStamp = "2021-01-21-15.52.00.000000"
#
# parmTIPLayerDataInfo.strExTIPLayerData_ParamSequence.item.append(parmTIPLayerData_Param8)
#
# parmTIPLayerData_Param9 = client.factory.create('csExTIPLayerData_Param')
# parmTIPLayerData_Param9.name = "DP_INSP_TYPE"
# parmTIPLayerData_Param9.type = "String"  # ask IBM
# parmTIPLayerData_Param9.value = "DB"
# parmTIPLayerData_Param9.claimUserID.identifier = "RichardGao"
# parmTIPLayerData_Param9.claimTimeStamp = "2021-01-21-15.52.00.000000"
#
# parmTIPLayerDataInfo.strExTIPLayerData_ParamSequence.item.append(parmTIPLayerData_Param9)
#         end loop parameters

parmTIPLayerData.strExTIPLayerDataInfoSequence.item.append(parmTIPLayerDataInfo)
#    end loop layers

parmTIPLayerDataSetReqIn.strExTIPLayerData = parmTIPLayerData


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
# typedef struct pptBaseResult_struct {
#    pptRetCode            strResult;
#    any siInfo;
# } pptBaseResult;
#
# csExTIPLayerDataParmSetReqResult CS_TxExTIPLayerDataParmSetReq
# (
#    in pptUser                           requestUserID,
#    in csExTIPLayerDataParmSetReqInParm  strExTIPLayerDataParmSetReqInParm
# )
def MES_TxExTIPLayerDataParmSetReq(strExTIPLayerDataParmSetReqInParm):
    # Parameter 1: pptUser
    parmUser = client.factory.create('pptUser')
    parmUser.userID.identifier = "DP_SYS"
    parmUser.password = "es1xttAQ"
    print(strExTIPLayerDataParmSetReqInParm)
    resultOutput = client.service.CS_TxExTIPLayerDataParmSetReq(parmUser, strExTIPLayerDataParmSetReqInParm)
    print(resultOutput)
    if resultOutput.strResult.returnCode != "0":
        raise Exception(resultOutput)
    return resultOutput.strResult.returnCode


if __name__ == '__main__':
    print(client)
    try:
        MES_TxExTIPLayerDataParmSetReq(parmTIPLayerDataSetReqIn)
    except Exception as ex:
        print(ex)

    print("OK!!")
