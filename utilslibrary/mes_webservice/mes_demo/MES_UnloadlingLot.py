from utilslibrary.mes_webservice import mes_utils

client = mes_utils.get_ws_client()


# TxUnloadingLotRpt(pptUser requestUserID,
#                   objectIdentifier equipmentID,
#                   objectIdentifier cassetteID,
#                   objectIdentifier portID,
#                   xs:string claimMemo)
def unloading_lot(pptUser, equipmentID, cassetteID):
    paramUser = client.factory.create('pptUser')
    paramUser.userID.identifier = pptUser["userID"]
    paramUser.password = pptUser["password"]

    parmEquipmentID = client.factory.create('objectIdentifier')
    parmEquipmentID.identifier = equipmentID

    parmCassetteID = client.factory.create('objectIdentifier')
    parmCassetteID.identifier = cassetteID

    parmPortID = client.factory.create('objectIdentifier')
    parmPortID.identifier = "PORT1"

    result = client.service.TxUnloadingLotRpt(paramUser, parmEquipmentID, parmCassetteID, parmPortID, "DP test")
    print(result)


if __name__ == "__main__":
    ppt_user = {'userID': 'DP_SYS', 'password': 'es1xttAQ'}
    unloading_lot(ppt_user, "MWEB901", "MA100011")
