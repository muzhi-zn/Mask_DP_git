# coding:utf-8
"""
lot_trail model
"""


class LotInfoModel(object):
    Id = ''
    Tip_No = ''
    Lot_Id = ''
    Status = ''
    Status_Desc = ''
    Convert_Status = ''
    Convert_Status_Desc = ''

    def conver_to_dict(self, obj):
        d = {}
        d.update(obj.__dict__)
        return d
