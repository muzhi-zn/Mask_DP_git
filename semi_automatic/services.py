from Mask_DP.settings import MES_USER
from semi_automatic.models import lot_record
from utilslibrary.base.base import BaseService
from utilslibrary.mes_webservice.mes_base_webservice import MES_TxExTIPLayerDataParmInq


class LotRecordListService(BaseService):
    """查询lot记录的service类"""

    def get_lot_record_list(self, request):
        """获取记录列表"""
        pass


def query_mes_lot(l_r: lot_record):
    """通过接口获取mes的lotID"""
    l_r_list = []
    query_flag = False
    result = MES_TxExTIPLayerDataParmInq(MES_USER, l_r.tip_no, l_r.mask_name)
    print(result)
    if result.strResult.returnCode == '0':  # 请求成功
        for layerData in result.strExTIPLayerData.item:
            for layerDataInfo in layerData.strExTIPLayerDataInfoSequence.item:
                lot_created_status = layerDataInfo.lotCreatedStatus
                res = layerDataInfo.result
                print(res)
                lot_id = layerDataInfo.lotID
                if lot_created_status == 'Pass':  # 生成成功
                    if lot_id:
                        l_r.lot_id = lot_id
                        l_r.lot_result = res
                        query_flag = True
                        l_r_list.append(l_r)
                    else:
                        l_r.lot_result = res
                elif 'ERR' in lot_created_status:  # 生成失败
                    l_r.lot_result = res
                else:  # 其余状态先更新数据库
                    l_r.lot_result = res
    else:  # 接口请求失败
        l_r.lot_result = "接口请求失败"
    lot_record.objects.bulk_create(l_r_list)
    return query_flag
