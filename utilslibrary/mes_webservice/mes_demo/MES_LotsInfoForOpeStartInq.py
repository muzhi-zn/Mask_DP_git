# from utilslibrary.mes_webservice import mes_utils
#
# client = mes_utils.get_ws_client()
from suds.client import Client

client = Client('file:///C:\\workspace\\DP_Phase1\\utilslibrary\\mes_webservice\\'+
                'MES_FILES/MMS_CS/wsdl/CS_PPTServiceManager.wsdl',
                location="http://10.3.10.30:27111/CS_PPTServiceManager/thePPTServiceManager", cache=None)

def MES_LotsInfoForOpeStartInq():
    # TxLotsInfoForOpeStartInq(pptUser requestUserID, objectIdentifier equipmentID, objectIdentifierSequence cassetteID)
    print(client)
    parmUser = client.factory.create('pptUser')
    parmUser.userID.identifier = "DP_Test"
    parmUser.password = "utfU`QE"

    paramequipmentID = client.factory.create('objectIdentifier')
    paramequipmentID.identifier = 'MDCOM01'

    paramcassetteID = client.factory.create('objectIdentifierSequence')
    cid = client.factory.create('objectIdentifier')
    cid.identifier = 'MA100299'
    paramcassetteID.item.append(cid)

    resultoutput = client.service.TxLotsInfoForOpeStartInq(parmUser,paramequipmentID,paramcassetteID)
    # print(resultoutput)
    return resultoutput

if __name__ == "__main__":
    result = MES_LotsInfoForOpeStartInq()
    print(result)
