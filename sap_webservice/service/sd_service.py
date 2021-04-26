import os

from suds.client import Client

from Mask_DP.settings import MES_URL
from Mask_DP.settings import MES_USER

BANK_ID = "FINISH"


class SDService:

    def get_client(self):
        """获取webservice的clent"""
        return Client('file:///' + os.path.dirname(__file__) + '/MES_wsdl/wsdl/CS_PPTServiceManager.wsdl',
                      location=MES_URL, cache=None)

    def ship(self, lot_ids, remark):
        client = self.get_client()
        parmUser = client.factory.create('pptUser')
        parmUser.userID.identifier = MES_USER['userID']
        parmUser.password = MES_USER['password']
        lot_list = client.factory.create('objectIdentifierSequence')
        for _lot_id in lot_ids:
            lot_id = client.factory.create('objectIdentifier')
            lot_id.identifier = _lot_id
            lot_list.item.append(lot_id)
        bank_id = client.factory.create('objectIdentifier')
        bank_id.identifier = BANK_ID
        result = client.service.TxShipReq(parmUser, lot_list, bank_id, remark)
        return result

    def unShip(self, lot_ids, remark):
        client = self.get_client()
        parmUser = client.factory.create('pptUser')
        parmUser.userID.identifier = MES_USER['userID']
        parmUser.password = MES_USER['password']
        lot_list = client.factory.create('objectIdentifierSequence')
        for _lot_id in lot_ids:
            lot_id = client.factory.create('objectIdentifier')
            lot_id.identifier = _lot_id
            lot_list.item.append(lot_id)
        bank_id = client.factory.create('objectIdentifier')
        bank_id.identifier = BANK_ID
        result = client.service.TxShipCancelReq(parmUser, lot_list, bank_id, remark)
        return result

