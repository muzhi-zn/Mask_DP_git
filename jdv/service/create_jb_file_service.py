# code: utf-8
import logging
import os
import re
from collections import Counter

from making.models import convert_status
from system.models import template,dict
from tooling_form.models import product_info, tapeout_info, layout_info, boolean_info, device_info
from utilslibrary.decorators.catch_exception_decorators import catch_exception
from utilslibrary.system_constant import Constant
from utilslibrary.utils.file_utils import get_work_path, join_path

log = logging.getLogger('log')

@catch_exception
def create_jb_file(tip_no):
    """生成jb文件"""
    product_name = product_info.objects.get(tip_no=tip_no, is_delete=0).product
    jdv_folder = join_path(get_work_path(product=product_name), 'JDV')
    jb_file_name = get_jb_file_name(jdv_folder, product_name)
    jb_path = join_path(jdv_folder, jb_file_name)
    jb = open(jb_path, 'w')
    temp = template.objects.filter(template_type=Constant.JDV_JB_TEMPLATE_TYPE, template_name='JB_FILE').first()
    mask_list = tapeout_info.objects.filter(tip_no=tip_no, t_o='Y', is_delete=0)
    mtitle_str = ''
    for mtitle, mask in enumerate(mask_list):
        mtitle_str += 'MTITLE ' + str(mtitle + 1) + ',' + mask.mask_name + '\n'
    chips_str = ''
    for num, mask in enumerate(mask_list):
        num = num + 1
        if num == 1:
            for chips in get_chips(num, tip_no, jdv_folder, mask):
                chips_str += chips
        else:
            for chips in get_chips(num, tip_no, jdv_folder, mask):
                chips_str += chips
    dict_parent_id = dict.objects.filter(type=Constant.JDV_JB_TEMPLATE_TYPE).first().id
    d_mtitles = dict.objects.filter(parent_id=dict_parent_id, label='MTITLES').first().value
    d_chips = dict.objects.filter(parent_id=dict_parent_id, label='CHIPS').first().value
    jb_str = str(temp.template_text).replace("{{%s}}" % d_mtitles, mtitle_str).replace("{{%s}}" % d_chips, chips_str)
    jb.write(jb_str)
    jb.close()
    # 更新convert_status中jdv的文件名及路径
    convert_status.objects.filter(tip_no=tip_no, device_name="Frame", stage_id=6).update(file_name=jb_file_name,
                                                                                         location=jdv_folder)
    log.info("jb文件更新convert_status路径成功")
    log.info("jb文件生成成功")


def get_jb_file_name(jdv_folder, product_name):
    """获取jb_file_name"""
    file_name = ''
    for item in os.listdir(jdv_folder):
        if re.match(product_name + '_\d+.jb', item):
            file_name = item
            os.remove(os.path.join(jdv_folder, item))
    if file_name != '':
        num = file_name.split('_')[1].split('.')[0]
        file_name = product_name + '_' + ('%04d' % (int(num) + 1)) + '.jb'
    else:
        file_name = product_name + '_0001.jb'
    return file_name


def get_chips(num, tip_no, jdv_folder, mask):
    """获取chips"""
    chips = []
    layout_list = layout_info.objects.filter(tip_no=tip_no)
    layout_l = []
    for layout in layout_list:
        layout_l.append(layout.device_name)
    s = Counter(layout_l)
    c = Counter(layout_l)
    for device_name in layout_l:
        chip_str = "CHIP %s, \n" % (device_name + ("_%02d" % (s[device_name] - c[device_name])))
        chip_str = chip_str + get_chip_rows(num, tip_no, jdv_folder, mask, device_name)
        chips.append(chip_str)
        c[device_name] = c[device_name] - 1
    return chips


def get_chip_rows(num, tip_no, jdv_folder, mask, device_name):
    """获取chips_rows"""
    rows_list = []
    rows = ''
    boolean = boolean_info.objects.filter(tip_no=tip_no, mask_name=mask.mask_name).first()
    layout = layout_info.objects.filter(tip_no=tip_no, device_name=device_name).first()
    layers = boolean.operation  # layers
    db_list = [boolean.source_db]  # 保存所有db
    db_group = re.findall(r'\[(\w+)?\]', layers)
    for db in db_group:
        db_list.append(db)  # 将DB插入列表
    if len(db_list) == 1:  # layers中不存在其他DB
        device = device_info.objects.filter(tip_no=tip_no, mask_name=mask.mask_name, device_name=device_name,
                                            source_db=boolean.source_db).first()
        for ly in get_ly(boolean.operation):
            row = "$   (" + str(num) + ", " + os.path.join(jdv_folder, device.file_name) + \
                  ",TC=" + device.top_structure + \
                  ",SF=" + mask.mask_mag + \
                  ",AG=" + str(mask.rotation) + \
                  ",BX=" + str(float(device.lb_x) * 4) + \
                  ",BY=" + str(float(device.lb_y) * 4) + \
                  ",UX=" + str(float(device.rt_x) * 4) + \
                  ",UY=" + str(float(device.rt_x) * 4) + \
                  ",LY=" + ly + \
                  ",AD=" + boolean.grid + ")\n"
            rows_list.append(row)
    else:
        for db in list(set(db_list)):
            l = []
            if db == boolean.source_db:
                l = re.findall(r'[^\]][A-Z]+(\d+;\d+)', layers)  # 匹配出不包含[DB]的数据
            else:
                l = re.findall(r'\[' + db + '\]\w(\d+;\d+)', layers)  # 匹配当前DB的数据
            device = device_info.objects.filter(tip_no=tip_no, mask_name=mask.mask_name,
                                                device_name=device_name, source_db=db).first()
            for ly in get_db_ly(l):
                row = "$   (" + str(num) + ", " + os.path.join(jdv_folder, device.file_name) + \
                      ",TC=" + device.top_structure + \
                      ",SF=" + mask.mask_mag + \
                      ",AG=" + str(int(float(mask.rotation))) + \
                      ",BX=" + str(float(device.lb_x) * 4) + \
                      ",BY=" + str(float(device.lb_y) * 4) + \
                      ",UX=" + str(float(device.rt_x) * 4) + \
                      ",UY=" + str(float(device.rt_x) * 4) + \
                      ",LY=" + ly + \
                      ",AD=" + boolean.grid + ")\n"
                rows_list.append(row)
    for row in rows_list:
        rows += row
    return rows + "ROWS " + str(float(layout.x1) * 4 + 76200) + "/" + str(float(layout.y1) * 4 + 76200) + "\n*! \n"


def get_ly(layer):
    """格式化layer数据"""
    ly_list = []
    l_s = re.findall(r'\d+;\d+', layer)
    d = {}
    for l in l_s:
        f = l.split(';')[0]
        e = l.split(';')[1]
        if f in d.keys():
            d[f] = d[f] + ", " + e
        else:
            d[f] = l
    for v in d.values():
        # ly = ly + "{%s}" % v
        ly_list.append("{%s}" % v)
    return ly_list


def get_db_ly(l_list):
    """获取带[DB]的数据"""
    ly_list = []
    d = {}
    for l in l_list:
        f = l.split(';')[0]
        e = l.split(';')[1]
        if f in d.keys():
            d[f] = d[f] + ", " + e
        else:
            d[f] = l
    for v in d.values():
        ly_list.append("{%s}" % v)
    return ly_list
