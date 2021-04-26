import os

# from jdv.models import lot_info
from suds.client import Client

from Mask_DP.settings import MES_URL


def get_wsdl_file():
    return 'file:///' + os.path.dirname(__file__) + \
           '/MES_FILES/MMS_CS/wsdl/CS_PPTServiceManager.wsdl'


def get_ws_client():
    return Client(get_wsdl_file(),
                  location=MES_URL, cache=None)


def get_tapeout_type(mask_vender, customer):
    """根据mask_vender和customer获取tapeout_type"""
    if mask_vender == 'QXIC':
        if customer == 'QXIC':
            return 'A'
        else:
            return 'B'
    else:
        return 'C'


def get_security_type(security_type):
    """根据security_type获取mes需要的参数"""
    if security_type == 'Normal':
        return 'N'
    else:
        return 'Y'


def set_lot_state(lot, lot_state_list):
    """设置 lot的各种状态"""
    for lot_state in lot_state_list:
        state_name = lot_state.stateName
        state_value = lot_state.stateValue
        if state_name == 'Lot State':
            lot.mes_lot_state = state_value
        if state_name == 'Lot Production State':
            lot.mes_lot_production_state = state_value
        if state_name == 'Lot Hold State':
            lot.mes_lot_hold_state = state_value
        if state_name == 'Lot Finished State':
            lot.mes_lot_finished_state = state_value
        if state_name == 'Lot Process State':
            lot.mes_lot_process_state = state_value
        if state_name == 'Lot Inventory State':
            lot.mes_lot_inventory_state = state_value
    return lot


def mes_sign_password(password):
    """密码签名，签名方式为原始密码每个字符ASCII码加一，然后倒序显示"""
    sign = ""
    p_list = list(password)
    p_list.reverse()
    for p in p_list:
        sign += chr(ord(p)+1)
    return sign
