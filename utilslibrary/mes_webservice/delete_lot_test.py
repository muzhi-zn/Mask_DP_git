from utilslibrary.mes_webservice import mes_utils

# ppt_user = {'userID': 'DP_Test', 'password': 'utfU`QE'}
ppt_user = {'userID': 'DP_SYS', 'password': 'es1xttAQ'}
client = mes_utils.get_ws_client()
parmUser = client.factory.create('pptUser')
parmUser.userID.identifier = "DP_SYS"
parmUser.password = "es1xttAQ"


def query_lot(lot_id):
    parmTIPLayerDataParmInqInParm = client.factory.create('csExTIPLayerDataParmInqInParm')
    parmTIPLayerDataParmInqInParm.purpose = 'Tip'
    parmTIPLayerDataParmInqInParm.tipNO = "TP0200030"
    resultOutput = client.service.CS_TxExTIPLayerDataParmInq(parmUser, parmTIPLayerDataParmInqInParm)
    print("-----" * 8)
    print(resultOutput)


def delete_lot():
    parmTIPLayerDataSetReqIn = client.factory.create('csExTIPLayerDataParmSetReqInParm')
    parmTIPLayerDataSetReqIn.Action = "Delete"  # Insert/Update/Delete/ResetCnt
    parmTIPLayerData = client.factory.create('csExTIPLayerData')
    parmTIPLayerData.tipNO = "TP02001b8"
    parmTIPLayerDataInfo = client.factory.create('csExTIPLayerDataInfo')
    parmTIPLayerDataInfo.partName = "QEA006-12PA1"
    parmTIPLayerDataInfo.purpose = "TIP"
    # parmTIPLayerDataInfo.lotID = "MA100105.001"
    parmTIPLayerData.strExTIPLayerDataInfoSequence.item.append(parmTIPLayerDataInfo)
    parmTIPLayerDataSetReqIn.strExTIPLayerData = parmTIPLayerData
    resultOutput = client.service.CS_TxExTIPLayerDataParmSetReq(parmUser, parmTIPLayerDataSetReqIn)
    print(resultOutput)
    if resultOutput.strResult.returnCode != "0":
        raise Exception(resultOutput)
    return resultOutput.strResult.returnCode


if __name__ == "__main__":
    # query_lot("MA100104.001")
    # delete_lot()
    # print(client)
    query_lot("")
