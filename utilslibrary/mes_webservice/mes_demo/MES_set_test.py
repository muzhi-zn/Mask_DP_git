from suds.client import Client

if __name__ == "__main__":
    client = Client('file:///C:\\workspace\\DP_Phase1\\utilslibrary\\mes_webservice\\' +
                    'MES_FILES/MMS_CS/wsdl/CS_PPTServiceManager.wsdl',
                    location="http://10.3.10.30:27111/CS_PPTServiceManager/thePPTServiceManager", cache=None)
    paramUser = client.factory.create('pptUser')
    paramUser.userID.identifier = "DP_Test"
    paramUser.password = "utfU`QE"
    parmTIPLayerDataSetReqIn = client.factory.create('csExTIPLayerDataParmSetReqInParm')
    parmTIPLayerDataSetReqIn.Action = "Update"  # Insert/Update/Delete/ResetCnt
    parmTIPLayerData = client.factory.create('csExTIPLayerData')
    parmTIPLayerData.tipNO = "TP0200019"
    parmTIPLayerDataInfo = client.factory.create('csExTIPLayerDataInfo')
    parmTIPLayerDataInfo.partName = "TES013-12PA1"
    parmTIPLayerDataInfo.lotID = "MA100263.001"
    parmTIPLayerData_Param = client.factory.create('csExTIPLayerData_Param')
    parmTIPLayerData_Param.name = "DP_ORDER_NUM"
    parmTIPLayerData_Param.type = "String"
    parmTIPLayerData_Param.value = "000010000044"
    parmTIPLayerData_Param.claimUserID.identifier = "DP_Test"
    parmTIPLayerData_Param.claimTimeStamp = "2020-12-17-14.20.00.409438"
    parmTIPLayerDataInfo.strExTIPLayerData_ParamSequence.item.append(parmTIPLayerData_Param)
    parmTIPLayerData.strExTIPLayerDataInfoSequence.item.append(parmTIPLayerDataInfo)
    parmTIPLayerDataSetReqIn.strExTIPLayerData = parmTIPLayerData
    print(parmTIPLayerDataSetReqIn)
    resultOutput = client.service.CS_TxExTIPLayerDataParmSetReq(paramUser, parmTIPLayerDataSetReqIn)
    print(resultOutput)
