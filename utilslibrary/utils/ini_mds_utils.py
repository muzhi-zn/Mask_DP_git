import os
import logging
from jdv.models import lot_info
from system.models import template
from tooling_form.models import layout_info
from utilslibrary.system_constant import Constant
from system.models import dict

log = logging.getLogger('log')


def ini(tip_no):
    lot_IDs = lot_info.objects.filter(tip_no=tip_no)
    log.info('ini文件lotID获取成功')
    layout_ini = template.objects. get(template_type=Constant.LAY_OUT_INI_FILE_NAME).template_text
    log.info('ini文本获取成功')
    dict_file = dict.objects.get(is_delete=0, type=Constant.LAY_OUT_INI_FILE_NAME)
    dict_list = dict.objects.filter(is_delete=0, parent_id=dict_file.id)
    info_list = layout_info.objects.filter(tip_no=tip_no)
    code_list, device_list = [], []
    if lot_IDs:
        for lot_ID in lot_IDs:
            lotID = lot_ID.lot_id
            mask_name = lot_ID.mask_name
            product = lot_IDs[0].product_name
            code = mask_name.split('-')[-1]
            code_list.append(code)
            if info_list:
                for info in info_list:
                    device = info.device_name
                    device_list.append(device)
                for it in dict_list:
                    temp = "".join(['{{', it.label, '}}'])
                    if temp in layout_ini:
                        if temp == Constant.LAY_OUT_MASK_NAME:
                            layout_ini = layout_ini.replace(temp, mask_name)
                        elif temp == Constant.LAY_OUT_LOT_ID:
                            layout_ini = layout_ini.replace(temp, lotID)
                    for device_name in device_list:
                        for code_num in code_list:
                            path = Constant.TEMPLATE_FILE_GENERATE_PATH + Constant.LAY_OUT_FILE_PATH.format(product,device_name,code_num)
                            if not os.path.exists(path):
                                log.info('不存在ini路径文件夹，创建文件')
                                os.makedirs(path)
                                log.info('已创建ini路径文件夹')
                                os.chmod(path, 0o777)
                            with open(path+'/layout.ini', 'w', encoding='utf-8') as f:
                                f.write(layout_ini)

            else:
                log.info('ini无对应的layout')
                return False
    else:
        log.info('ini无对应的lotID')
        return False


def mds(tip_no):
    lot_IDs = lot_info.objects.filter(tip_no=tip_no)
    log.info('mds文件lotID获取成功')
    layout_mds = template.objects.get(template_type=Constant.LAY_OUT_MDS_FILE_NAME).template_text
    log.info('mds文本获取成功')
    dict_file = dict.objects.get(is_delete=0, type=Constant.LAY_OUT_MDS_FILE_NAME)
    dict_list = dict.objects.filter(is_delete=0, parent_id=dict_file.id)
    code_list,device_list = [],[]
    # path_list = []
    info_list = layout_info.objects.filter(tip_no=tip_no)
    if lot_IDs:
        for lot_ID in lot_IDs:
            lotID = lot_ID.lot_id
            mask_name = lot_ID.mask_name
            product = lot_IDs[0].product_name
            code = mask_name.split('-')[-1]
            code_list.append(code)
            x_y_list = []
            if info_list:
                for info in info_list:
                    device = info.device_name
                    x1 = info.x1
                    y1 = info.y1
                    #mds中x,y取值算法
                    x = round(float(x1) * 4 - 76200)
                    y = round(float(y1) * 4 - 76200)
                    x_y_list.append('put {} {} 1 0 ${};'.format(x, y, device))
                    x_y_str = '\n        '.join(x_y_list)
                    device_list.append(device)
                for it in dict_list:
                    temp = "".join(['{{', it.label, '}}'])
                    if temp in layout_mds:
                        if temp == Constant.LAY_OUT_MASK_NAME:
                            layout_mds = layout_mds.replace(temp, mask_name)
                        elif temp == Constant.LAY_OUT_LOT_ID:
                            layout_mds = layout_mds.replace(temp, lotID)
                        elif temp == Constant.LAY_OUT_X_Y_NUM:
                            layout_mds = layout_mds.replace(temp, x_y_str)
                    # mask_name,lotID,x_y_str
                    for device_name in device_list:
                         for code_num in code_list:
                            path = Constant.TEMPLATE_FILE_GENERATE_PATH + Constant.LAY_OUT_FILE_PATH.format(product,device_name,code_num)
                            if not os.path.exists(path):
                                log.info('不存在mds路径文件夹，创建文件')
                                os.makedirs(path)
                                log.info('已创建mds路径文件夹')
                                os.chmod(path, 0o777)
                            with open(path+'/layout.mds', 'w', encoding='utf-8') as f:
                                f.write(layout_mds)
            else:
                log.info('mds无对应的layout')
                return False
    else:
        log.info('mds无对应的lotID')
        return False

