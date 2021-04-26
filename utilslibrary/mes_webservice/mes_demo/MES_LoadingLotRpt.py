from utilslibrary.mes_webservice import mes_utils

client = mes_utils.get_ws_client()


# TxLoadingLotRpt(pptUser requestUserID,
#                 objectIdentifier equipmentID,
#                 objectIdentifier cassetteID,
#                 objectIdentifier portID,
#                 xs:string loadPurposeType,
#                 xs:string claimMemo)
def loading_lot(pptUser, equipmentID, cassetteID):
    paramUser = client.factory.create('pptUser')
    paramUser.userID.identifier = pptUser["userID"]
    paramUser.password = pptUser["password"]

    parmEquipmentID = client.factory.create('objectIdentifier')
    parmEquipmentID.identifier = equipmentID

    parmCassetteID = client.factory.create('objectIdentifier')
    parmCassetteID.identifier = cassetteID

    parmPortID = client.factory.create('objectIdentifier')
    parmPortID.identifier = "PORT1"

    result = client.service.TxLoadingLotRpt(paramUser, parmEquipmentID, parmCassetteID, parmPortID, "Process Lot", "DP test")
    print(result)


if __name__ == "__main__":
    print(client)
    # ppt_user = {'userID': 'DP_SYS', 'password': 'es1xttAQ'}
    # loading_lot(ppt_user, "MWEB901", "MA100011")
