# SLICE EDIT,17,    $TED/ATMA0024XA4A.JB
# *  JOBDECK WRITTEN BY CATS: ACER AT SUN DEC 22 14:09:38 2019
# *!
# *! GROUP COMMANDS
# *!
# SCALE 0.25,1
# *!
# *! ALPHA, RETICLE, REPEAT AND SIZING COMMANDS
# *!
# *! OPTION COMMANDS
# OPTION  AA=0.25,DA=1,	MA,	PA
# *!
# *! TITLE AND ORIENT COMMANDS
# *!
# ORIENT A,MTITLE,  TITLEROT=90,MIRROR=NO,CHARROT=0,LOC=140000,24000,JUST=L
# ITITLE A,TCE-LOT
# ORIENT A,ITITLE,  TITLEROT=90,MIRROR=NO,CHARROT=0,LOC=145000,24000,JUST=L
# MTITLE 1,TMA002-780A1
# *!
# *!
# *! CHIP AND ROWS COMMANDS
# *!
# CHIP FRAME_00,
# $   (1, frame_1219_dummy_EO_opc_ok.oas,TC=ENG_v191113_mfg,SF=4,AG=0,BX=-51560,BY=-66000,UX=51560,UY=66000,LY={51;0,2,3}, AD=0.000125)
# ROWS 76200/76200
# *!
# CHIP FRAME_01,
# $   (1, ENG_v191223_mfg.gds,TC=frame,SF=4,AG=0,BX=-51560,BY=-66000,UX=51560,UY=66000,LY={0;102}, AD=0.000125)
# ROWS 76200/76200
# *!
# CHIP MP001_00,
# $   (1, ADD_1215_addChipPRbound_v1_dummy_EO_DP_opc.oas,TC=ADD,SF=4,AG=0,BX=-51560,BY=-66000,UX=51560,UY=66000,LY={51;0,2,3}, AD=0.000125)
# ROWS 76200/76200
# *!
# CHIP MP002_00,
# $   (1, MEOL_1215_addChipPRbound_v1_dummy_EO_DP_opc.oas,TC=MEOL,SF=4,AG=0,BX=-51560,BY=-66000,UX=51560,UY=66000,LY={51;0,2,3}, AD=0.000125)
# ROWS 76200/76200
# *!
# CHIP MP003_00,
# $   (1, HR_1215_addChipPRbound_v1_dummy_EO_DP_opc.oas,TC=HR,SF=4,AG=0,BX=-51560,BY=-66000,UX=51560,UY=66000,LY={51;0,2,3}, AD=0.000125)
# ROWS 76200/76200
# *!
# CHIP MP004_00,
# $   (1, VIA0_1215_addChipPRbound_v1_dummy_EO_DP_opc.oas,TC=VIA0,SF=4,AG=0,BX=-51560,BY=-66000,UX=51560,UY=66000,LY={51;0,2,3}, AD=0.000125)
# ROWS 76200/76200
# *!
# CHIP MP005_00,
# $   (1, VIA_1_1215_addChipPRbound_v1_dummy_EO_DP_opc.oas,TC=VIA_1,SF=4,AG=0,BX=-51560,BY=-66000,UX=51560,UY=66000,LY={51;0,2,3}, AD=0.000125)
# ROWS 76200/76200
# *!
# CHIP MP006_00,
# $   (1, DEF_1215_addChipPRbound_v1_dummy_EO_DP_opc.oas,TC=DEF,SF=4,AG=0,BX=-51560,BY=-66000,UX=51560,UY=66000,LY={51;0,2,3}, AD=0.000125)
# ROWS 76200/76200
# *!
# CHIP MP007_00,
# $   (1, CAP_merge_20191221.oas,TC=CAP_20190828_C_3,SF=4,AG=0,BX=-51560,BY=-66000,UX=51560,UY=66000,LY={51;0,2,3}, AD=0.000125)
# ROWS 76200/76200
# *!
# CHIP MP008_00,
# $   (1, REL_1216_addChipPRbound_changeR5_v1_dummy_EO_DP_opc.oas,TC=REL,SF=4,AG=0,BX=-51560,BY=-66000,UX=51560,UY=66000,LY={51;0,2,3}, AD=0.000125)
# ROWS 76200/76200
# *!
# CHIP MP009_00,
# $   (1, REL_1216_addChipPRbound_changeR5_v1_dummy_EO_DP_opc.oas,TC=REL,SF=4,AG=0,BX=-51560,BY=-66000,UX=51560,UY=66000,LY={51;0,2,3}, AD=0.000125)
# ROWS 76200/76200
# *!
# END
import re

from tooling_form.models import product_info, tapeout_info, device_info, boolean_info


def create_extend_jb(tip_no):
    """创建Extend_jb文件"""
    # 产品信息
    product = product_info.objects.filter(tip_no=tip_no, is_delete=0)
    # mask信息
    tapeout_list = tapeout_info.objects.filter(tip_no=tip_no, is_delete=0, t_o='Y')
    for tapeout in tapeout_list:
        pass
    content = ""


def get_chip_content(tip_no, mask_name):
    """获取chip内容"""
    chip_content = ""
    tapeout = tapeout_info.objects.get(tip_no=tip_no, mask_name=mask_name, is_delete=0)
    device_list = device_info.objects.filter(tip_no=tip_no, mask_name=mask_name, is_delete=0)
    for device in device_list:
        chip_content += "*!\nCHIP " + device.device_name + "_00,\n" + "$   (1, " + device.file_name + "," + "TC=" \
                        + device.top_structure + ",SF=" + tapeout.mask_mag + ",AG=" + tapeout.rotation + \
                        ",BX=" + str(float(device.lb_x) * float(tapeout.mask_mag)) + \
                        ",BY=" + str(float(device.lb_y) * float(tapeout.mask_mag)) + \
                        ",UX=" + str(float(device.rt_x) * float(tapeout.mask_mag)) + \
                        ",UY=" + str(float(device.rt_y) * float(tapeout.mask_mag)) + \
                        ",LY="
        pass
    return chip_content


def get_ly(tip_no, mask_name):
    """获取device的layer"""
    ly_list = []
    boolean = boolean_info.objects.filter(tip_no=tip_no, mask_name=mask_name, is_delete=0)
    layer = boolean.operation
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
    """获取boolean_info中带DB的layer数据"""
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


def get_device_content():
    """获取device的job view的内容"""
    pass
