import re

from suds.client import Client

pptUser = {'userID': 'DP_Test', 'password': 'utfU`QE'}


def get_ws_client():
    return Client("file:///C:/workspace/DP_Phase1/sap_webservice/service/MES_wsdl/wsdl/CS_PPTServiceManager.wsdl",
                  location="http://10.3.10.30:27111/CS_PPTServiceManager/thePPTServiceManager", cache=None)


if __name__ == "__main__":
    # p = "TES667-860A1.00"
    # print(p[:12])
    # client = get_ws_client()
    # print(client)
    # parmUser = client.factory.create('pptUser')
    # parmUser.userID.identifier = pptUser['userID']
    # parmUser.password = pptUser['password']
    # lot_id = client.factory.create('objectIdentifier')
    # lot_id.identifier = "MA10002D.001"
    # lot_list = client.factory.create('objectIdentifierSequence')
    # lot_list.item.append(lot_id)
    # bank_id = client.factory.create('objectIdentifier')
    # bank_id.identifier = "FINISH"
    # result = client.service.TxShipReq(parmUser, lot_list, bank_id, "测试")
    # print(result)
    # print(result.strResult.returnCode)
    s = "COMPARE:      99      234830"

    print(re.findall(r"COMPARE:      99 *(\d+)", s))
