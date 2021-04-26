# coding:utf-8
"""jdv/generate file/ process method

"""
import os
import re
import logging
import copy
import traceback
import time

from catalog.models import tool_name_route
from infotree.models import released_info_alta, released_info, released_mdt
from utilslibrary.base.base import BaseService
from system.models import template, dict
from machine.models import machine_basic
from django.conf import settings
from shutil import rmtree
from django.db import transaction
from django.db.models import Q
from utilslibrary.utils.common_utils import getCurrentSessionID, getCurrentSessionName
from utilslibrary.utils.file_utils import create_file
from utilslibrary.system_constant import Constant
# from tooling.models import import_data, device_info
from django.http.response import HttpResponseRedirect, JsonResponse
from utilslibrary.utils.file_utils import *
from making.models import deck_para, fracture_deck, alta_naming_table, convert_status
from jdv.models import lot_info, lot_trail, mes_blank_code
from jdv.service.lot_trail_service import LotTrailService
from shutil import copyfile
from datetime import datetime
from tooling_form.models import product_info as tooling_product_info, tapeout_info as tooling_tapeout_info, \
    device_info as tooling_device_info, boolean_info as tooling_boolean_info
from machine.models import writer_mapping
from catalog.models import tool_maintain

log = logging.getLogger('LOGGING')


def catch_value(val, device_name, mask_name, tip_no, boolean_index, _db_path):
    val = val.split(",")
    tmp_str = ''
    return tmp_str


class GenerateFileService(BaseService):

    def fracture_deck(self, user_id, user_name, lot_id, tip_no, mask_name, device_name, stage_name, tool_id):

        # validate data
        data, mdt, _mdt, fra_file, fra_path = self.validate_Fracture_mdt_table(lot_id, tip_no, mask_name, tool_id,
                                                                               device_name, 'fracture')
        if data['success'] != True:
            return data
        else:
            LotTrailService().insert_trail(user_id=user_id, user_name=user_name, lot_id=lot_id, tip_no=tip_no,
                                           stage='Generate File',
                                           stage_desc=data['msg'], remark='', is_error=Constant.LOT_STAGE_IS_ERROR_YES)
            # return data

        return self.fracture_template_generate(user_id=user_id, user_name=user_name, lot_id=lot_id,
                                               device_name=device_name,
                                               mask_name=mask_name, tip_no=tip_no,
                                               product="", mdt=mdt, stage_name=stage_name, tool_id=tool_id,
                                               design_rule=_mdt.node, mask_tone=_mdt.tone, mask_grade=_mdt.grade,
                                               blank=_mdt.blank,
                                               fra_file=fra_file, fra_path=fra_path)

    # template file generate
    # mask_name:
    # tip_no:
    # product:
    # host_file_content:
    # mrcexe_lsf_content:
    # mdt:Y：vsb12i,need generate .attr file N:vsb12.donnot generate .attr file
    def fracture_template_generate(self, user_id, user_name, lot_id, device_name, mask_name, tip_no, product, mdt,
                                   stage_name, tool_id, design_rule, mask_tone, mask_grade, blank, fra_file, fra_path):
        # get layer name:120A1 in TIM001-120A1
        data = {}
        try:
            _layer = mask_name[-5:]
            product = mask_name.split("-")[0]
            # response data
            # generated file list
            _list_file = ''
            # make dirs
            base_path = get_work_path(product, mak=1)

            # query device list by tip_no
            _device_list = []
            if device_name:
                _device_list.append({'import_data': device_name})
            else:
                _device_list = list()
            # while device,mkdir
            for _device in _device_list:
                _device_name = _device['import_data']
                # package device_path start
                _device_path = get_device_path(join_path(base_path, Constant.FILE_PATH_DEVICE), _device_name, mak=1)
                # package  device/db path
                _db_path = get_db_path(_device_path, mak=1)
                # package device/layer path
                _layer_path = join_path(_device_path, Constant.FILE_PATH_LAYER, mak=1)
                _mask_name_path = get_layer_path(_layer_path, _layer, mak=1)
                _fracture_path = join_path(_mask_name_path, Constant.FILE_PATH_FRACTURE, mak=1)
                # package device_path end
                # delete all file
                #                del_file(_fracture_path)

                _deck = product + '_' + _layer + '_' + device_name + '_' + stage_name.lower().replace(" ", "_",
                                                                                                      1) + '.' + \
                        fra_file.split(".")[1]
                #                if check_file_exists(join_path(_fracture_path, _deck, mak=0)):
                #                    os.remove(join_path(_fracture_path, _deck, mak=0))
                copyfile(join_path(fra_path, fra_file, mak=0), join_path(_fracture_path, _deck, mak=0))
                os.chmod(join_path(_fracture_path, _deck, mak=0), 0o775)
                _file = join_path(_fracture_path, _deck, mak=0)
                self.convert_deck(lot_id=lot_id, tip_no=tip_no, mask_name=mask_name, device_name=device_name,
                                  _stage=Constant.STAGE_FRACTURE, _prestage='', _pre_stage_path='', _file=_file,
                                  deck_type='deck',
                                  customer='out', input_path='', input_path2='', output_path='', input_name='',
                                  out_gds_path='', recipe_id='')

                _list_file = _list_file + _file + '<br>'
                # package host_file content
                host_file_content = self.package_host_file()
                # generate host_file
                path = join_path(_fracture_path, Constant.FRACTURE_VSB12I_HOST_FILE_NAME)
                create_file(path, host_file_content)
                _list_file = _list_file + path + '<br>'
                # generate attr
                if mdt == 'Y':
                    _attr_content = self.get_vsb12i_attr_content_from_mdt_table(tip_no, mask_name, tool_id,
                                                                                design_rule, mask_tone,
                                                                                mask_grade, blank, _layer[0:3])
                    _attr_file_name = product + '_' + mask_name[-5:] + '.attr'
                    path = join_path(_fracture_path, _attr_file_name)
                    create_file(path, _attr_content)
                    _list_file = _list_file + path + '<br>'
                # generate vsb12i fracture xor

            # modify lot_info convert_status
            _o = lot_info.objects.get(lot_id=lot_id)
            _o.convert_status = Constant.LOT_STAGE_GEN_FILE_SUCCESS
            _o.save()
            # insert into lot_trail

            LotTrailService().insert_trail(user_id=user_id, user_name=user_name, lot_id=_o.id, tip_no=tip_no,
                                           stage='Generate File',
                                           stage_desc=_list_file, remark='')

            data["success"] = True
            data["msg"] = "success"
            return data
        except Exception as e:
            traceback.print_exc()
            data["success"] = False
            data["msg"] = str(e)
            return data

    def fracture_xor_deck(self, user_id, user_name, lot_id, device_name):
        print(lot_id)
        _o = lot_info.objects.get(lot_id=lot_id)

        mask_name = _o.mask_name
        tip_no = _o.tip_no
        # query data from db
        # product
        _product = mask_name.split("-")[0]

        # if vsb12i
        return self.fracture_xor_template_generate(user_id=user_id, user_name=user_name, lot_id=lot_id,
                                                   mask_name=mask_name, tip_no=tip_no,
                                                   product=_product, device_name=device_name)

        # template file generate
        # mask_name:
        # tip_no:
        # product:

    def fracture_xor_template_generate(self, user_id, user_name, lot_id, mask_name, tip_no, product, device_name):
        tool_id = lot_info.objects.get(lot_id=lot_id).info_tree_tool_id
        data, mdt, _mdt, fra_file, fra_path = self.validate_Fracture_mdt_table(lot_id, tip_no, mask_name, tool_id,
                                                                               device_name, 'fractureXOR')
        # get layer name:120A1 in TIM001-120A1
        _layer = mask_name[-5:]
        # response data
        data = {}
        # generated file list
        _list_file = ''
        # make dirs
        base_path = get_work_path(product, mak=1)

        # query device list by tip_no
        _device_list = list()
        # while device,mkdir

        # package device_path start
        _device_path = get_device_path(join_path(base_path, Constant.FILE_PATH_DEVICE), device_name, mak=1)
        # package  device/db path
        _db_path = get_db_path(_device_path, mak=1)
        # package device/layer path
        _layer_path = join_path(_device_path, Constant.FILE_PATH_LAYER, mak=1)
        _mask_name_path = get_layer_path(_layer_path, _layer, mak=1)

        _fracture_path = join_path(_mask_name_path, Constant.FILE_PATH_FRACTURE, mak=1)
        # generate  xor file start
        _fracture_xor_path = get_fracture_XOR_path(_fracture_path, mak=1)
        # package device_path end

        # get boolean_index

        # _boolean_index = self.get_device_boolean(tip_no, _device_name)
        # get source_db
        print(tip_no)
        print(device_name)
        # print(_boolean_index)
        # _source_db1, _source_db2 = self.check_source_db(tip_no, _device_name, _boolean_index)
        stage_name = Constant.STAGE_FRACTURE_XOR
        stage_name = "fracture XOR"
        _deck = product + '_' + _layer + '_' + device_name + '_' + stage_name.replace(" ", "_", 1) + '.' + \
                fra_file.split(".")[1]
        #        if check_file_exists(join_path(_fracture_xor_path, _deck, mak=0)):
        #            os.remove(join_path(_fracture_xor_path, _deck, mak=0))
        copyfile(join_path(fra_path, fra_file, mak=0), join_path(_fracture_xor_path, _deck, mak=0))
        os.chmod(join_path(_fracture_xor_path, _deck, mak=0), 0o775)
        _file = join_path(_fracture_xor_path, _deck, mak=0)
        self.convert_deck(lot_id=lot_id, tip_no=tip_no, mask_name=mask_name, device_name=device_name,
                          _stage=Constant.STAGE_FRACTURE_XOR, _prestage='', _pre_stage_path='', _file=_file,
                          deck_type='deck',
                          customer='out', input_path='', input_path2='', output_path='', input_name='',
                          out_gds_path='', recipe_id='')

        # _file_name = _fracture_xor_path + '/' + mask_name.replace('-','_',1) +'_' + _device_name + '_fracture_XOR.prj'
        # copyfile('/qxic/qxic/MaskData/MDP_Page/fractureXOR_deck/fractureXOR_vsb12i.prj',_file_name)
        # _fracture_out_file = join_path(_fracture_path,  mask_name.replace('-','_',1) +'_' + _device_name + '/chip.cnf', mak=1)

        _list_file = _list_file + _file + '<br>'
        # generate  xor file end

        # generate mrcexe_lsf.sh start
        path = join_path(_fracture_xor_path, Constant.FRACTURE_VSB12I_XOR_MRCEXE_LSF_SH_FILE_NAME)
        mrcexe_lsf_content = self.package_mrcexe_lsf_sh()
        create_file(path, mrcexe_lsf_content)
        _list_file = _list_file + path + '<br>'
        # generate mrcexe_lsf.sh end

        # modify lot_info convert_status
        _o = lot_info.objects.get(lot_id=lot_id)
        _o.convert_status = Constant.LOT_STAGE_GEN_FILE_SUCCESS
        _o.save()
        # insert into lot_trail

        LotTrailService().insert_trail(user_id=user_id, user_name=user_name, lot_id=_o.id, tip_no=tip_no,
                                       stage='Generate File',
                                       stage_desc=_list_file, remark='')

        data["success"] = True
        data["msg"] = "success"
        return data

    # package fracture vsb12i template content
    def package_fracture_file_content(self, lot_id, _fracture_path, tip_no, _device_name, mask_name, boolean_index,
                                      _layer, _db_path, template_file_name, template_text):
        makdirs(_fracture_path)
        # generate fracture script
        # get template
        _o_dict = dict.objects.get(is_delete=0, type=Constant.FRACTURE_VSB12I_DICT_TYPE_NAME)
        _dict_list = dict.objects.filter(is_delete=0, parent_id=_o_dict.id)
        # get mask type
        _mask_type = self.get_mask_type(tip_no, mask_name)

        file_name = template_file_name
        # replace key value
        # replace info tree key value
        for it in _dict_list:
            # get db value by sheet&column
            temp = "".join(["{{", it.label, "}}"])
            if temp in template_text:
                value = self.sheet_column_to_db_value(tip_no=tip_no, device_name=_device_name, mask_name=mask_name,
                                                      boolean_index=boolean_index,
                                                      sheet_column=it.value, _db_path=_db_path, fracture_path='',
                                                      fracture_type=1)
                template_text = template_text.replace(temp, str(value))
            if temp in file_name:
                value = self.sheet_column_to_db_value(tip_no=tip_no, device_name=_device_name, mask_name=mask_name,
                                                      boolean_index=boolean_index,
                                                      sheet_column=it.value, _db_path=_db_path, fracture_path='',
                                                      fracture_type=1)

                file_name = file_name.replace(temp, str(value))
        template_text = template_text.encode('utf-8').decode('utf-8')
        file_name = file_name.encode('utf-8').decode('utf-8')
        return file_name, template_text

    # return:
    # code,msg,filename,template_text
    def get_fracture_template(self, lot_id, tip_no, device_name, boolean_index, mdt):
        # get source_db
        _source_db1, _source_db2 = self.check_source_db(tip_no, device_name, boolean_index)

        # query writer type by lot_id  from lot_info
        _lot_info = lot_info.objects.get(lot_id=lot_id)
        _machine = tool_name_route.objects.get(id=_lot_info.machine_id)
        if _machine.machine_type == Constant.WRITER_TYPE_MODE5:
            if _source_db1 != '' and _source_db2 == '':
                # get template1
                _template_file_name, _template_text = self.get_mode5_db1_template_content()
            elif _source_db1 != '' and _source_db2 != '':
                # get template2
                _template_file_name, _template_text = self.get_mode5_db1_db2_template_content()
            else:
                # raise Exception('source db error!')
                return Constant.COMMON_METHOD_RETURN_FLAG_ERROR, Constant.FRACTURE_SOURCE_DB_ERROR, '', ''
        elif _machine.machine_type == Constant.WRITER_TYPE_VSB:
            if mdt == 'Y' and _source_db1 != '' and _source_db2 == '':
                # get template1
                _template_file_name, _template_text = self.get_vsb12i_db1_template_content()
            elif mdt == 'Y' and _source_db1 != '' and _source_db2 != '':
                # get template2
                _template_file_name, _template_text = self.get_vsb12i_db1_db2_template_content()
            elif mdt == 'N' and _source_db1 != '' and _source_db2 == '':
                # get template1
                _template_file_name, _template_text = self.get_vsb12_db1_template_content()
            elif mdt == 'N' and _source_db1 != '' and _source_db2 != '':
                # get template2
                _template_file_name, _template_text = self.get_vsb12_db1_db2_template_content()
            else:
                # raise Exception('source db error!')
                return Constant.COMMON_METHOD_RETURN_FLAG_ERROR, Constant.FRACTURE_SOURCE_DB_ERROR, '', ''
        else:
            return Constant.COMMON_METHOD_RETURN_FLAG_ERROR, Constant.FRACTURE_WRITER_ERROR, '', ''
        return Constant.COMMON_METHOD_RETURN_FLAG_SUCCESS, '', _template_file_name, _template_text

    # generate fracture xor file
    def package_fracture_xor_file(self, _fracture_path, tip_no, mask_name, boolean_index, source_db, _device_name,
                                  _layer,
                                  _db_path):
        makdirs(_fracture_path)
        # get mask type
        _mask_type = self.get_mask_type(tip_no, mask_name)

        # generate fracture script
        # get template
        _template_list = template.objects.filter(is_delete=0, template_type=Constant.FRACTURE_VSB12I_XOR_DICT_TYPE_NAME)
        _o_dict = dict.objects.get(is_delete=0, type=Constant.FRACTURE_VSB12I_XOR_DICT_TYPE_NAME)
        _dict_list = dict.objects.filter(is_delete=0, parent_id=_o_dict.id)
        for _o in _template_list:
            file_name = _o.file_name
            text = _o.template_text
            # replace key value
            # replace info tree key value
            for it in _dict_list:
                # get db value by sheet&column
                temp = "".join(["{{", it.label, "}}"])
                if temp in text:
                    value = self.sheet_column_to_db_value(tip_no=tip_no, device_name=_device_name, mask_name=mask_name,
                                                          boolean_index=boolean_index,
                                                          sheet_column=it.value, _db_path=_db_path,
                                                          fracture_path=_fracture_path, fracture_type=2)

                    text = text.replace(temp, str(value))
                if temp in file_name:
                    value = self.sheet_column_to_db_value(tip_no=tip_no, device_name=_device_name, mask_name=mask_name,
                                                          boolean_index=boolean_index,
                                                          sheet_column=it.value, _db_path=_db_path,
                                                          fracture_path=_fracture_path, fracture_type=2)

                    file_name = file_name.replace(temp, str(value))
            # 判断device_file_type
            device_file_name = ""
            if ".gds" in device_file_name:
                text = text.replace("{{device_file_type}}", "GDS2")
            elif ".oas" in device_file_name:
                text = text.replace("{{device_file_type}}", "OASIS")
            text = text.encode('utf-8').decode('utf-8')
            file_name = file_name.encode('utf-8').decode('utf-8')
            return file_name, text

    def package_fracture_xor_file2(self, _file, _fracture_path, tip_no, mask_name, boolean_index, source_db,
                                   _device_name, _layer, _db_path, _file_name, _fracture_out_file):
        makdirs(_fracture_path)
        # get mask type
        _mask_type = self.get_mask_type(tip_no, mask_name)
        # generate fracture script

        self.convert_deck(lot_id='', tip_no=tip_no, mask_name=mask_name, device_name=_device_name,
                          _stage=Constant.STAGE_FRACTURE_XOR, _prestage=Constant.STAGE_FRACTURE, _file=_file,
                          deck_type='deck', customer='out', input_path=_fracture_path, input_path2=_fracture_out_file,
                          output_path='', input_name='', out_gds_path='', recipe_id='')

        return

    # get db value,by sheet:column
    # fracture_type=1: fracture
    # fracture_type=2:xor fracture
    def sheet_column_to_db_value(self, tip_no, device_name, mask_name, boolean_index, sheet_column,
                                 _db_path, fracture_path, fracture_type=1):
        _list = sheet_column.split(':')
        if _list[0] == 'TF':
            if _list[1] == Constant.TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO and (
                    _list[2] == Constant.TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO_LB_X \
                    or _list[2] == Constant.TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO_LB_Y \
                    or _list[2] == Constant.TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO_RT_X \
                    or _list[2] == Constant.TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO_RT_Y):
                if fracture_type == 1:
                    # _data_key =mask_type+'_'+device_name+'_'+boolean_index+'_'+db
                    _data_key = device_name + '_' + boolean_index + '_' + _list[3]

                    return self.get_value_from_db_by_data_key(tip_no, _list[1], _list[2], _data_key)
                if fracture_type == 2:
                    # _data_key = mask_type + '_' + device_name + '_' + boolean_index + '_' + db
                    # _data_key = device_name + '_' + boolean_index
                    _data_key = device_name + '_' + boolean_index + '_' + _list[3]
                return float(self.get_value_from_db_by_data_key(tip_no, _list[1], _list[2], _data_key)) * 1000
            elif _list[1] == Constant.TOOLING_FORM_EXCEL_SHEET_TAPEOUT_INFO and (
                    _list[2] == Constant.TOOLING_FORM_EXCEL_SHEET_TAPEOUT_INFO_MASK_MAG):
                return self.get_value_from_db_by_data_key(tip_no, _list[1], _list[2], mask_name)
            elif _list[1] == Constant.TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO and (
                    _list[2] == Constant.TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO_ROTATE):
                _data_key = device_name + '_' + boolean_index + '_' + _list[3]
                return self.get_value_from_db_by_data_key(tip_no, _list[1], _list[2], _data_key)
            elif _list[1] == Constant.TOOLING_FORM_EXCEL_SHEET_PRODUCT_INFO and (
                    _list[2] == Constant.TOOLING_FORM_EXCEL_SHEET_PRODUCT_INFO_PRODUCT):
                return self.get_value_from_db(tip_no, _list[1], _list[2])
            elif _list[1] == Constant.TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO and (
                    _list[2] == Constant.TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO_DEVICE_NAME):
                return device_name
            elif _list[1] == Constant.TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO and (
                    _list[2] == Constant.TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO_TOP_STRUCTURE):
                # data_key = mask_type+'_'+device_name+'_'+boolean_index+'_'+db
                if fracture_type == 1:
                    data_key = device_name + '_' + boolean_index + '_' + _list[3]
                elif fracture_type == 2:
                    # data_key = device_name + '_' + boolean_index
                    data_key = device_name + '_' + boolean_index + '_' + _list[3]
                return self.get_value_from_db_by_data_key(tip_no, _list[1], _list[2], data_key)
            elif _list[1] == Constant.TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO and (
                    _list[2] == Constant.TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO_SOURCE_MAG):
                if fracture_type == 1:
                    data_key = device_name + '_' + boolean_index + '_' + _list[3]
                elif fracture_type == 2:
                    # data_key = device_name + '_' + boolean_index
                    data_key = device_name + '_' + boolean_index + '_' + _list[3]
                return self.get_value_from_db_by_data_key(tip_no, _list[1], _list[2], data_key)

            elif _list[1] == Constant.TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO and (
                    _list[2] == Constant.TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO_FILE_NAME):
                # data_key = mask_type+'_'+device_name + '_' + boolean_index + '_' + db
                if fracture_type == 1:
                    data_key = device_name + '_' + boolean_index + '_' + _list[3]
                elif fracture_type == 2:
                    # data_key = device_name + '_' + boolean_index
                    data_key = device_name + '_' + boolean_index + '_' + _list[3]
                _file_name = self.get_value_from_db_by_data_key(tip_no, _list[1], _list[2], data_key)
                return join_path(_db_path, _file_name)

            elif _list[1] == Constant.TOOLING_FORM_EXCEL_SHEET_BOOLEAN_INFO and (
                    _list[2] == Constant.TOOLING_FORM_EXCEL_SHEET_BOOLEAN_INFO_GRID):
                data_key = mask_name + '_' + boolean_index + '_' + _list[3]
                return float(self.get_value_from_db_by_data_key(tip_no, _list[1], _list[2], data_key)) * 4
                # return self.get_grid(tip_no,mask_name,boolean_index,_list[3])
            elif _list[1] == Constant.TOOLING_FORM_EXCEL_SHEET_BOOLEAN_INFO and (
                    _list[2] == Constant.TOOLING_FORM_EXCEL_SHEET_BOOLEAN_INFO_OPERATION):
                if fracture_type == 1:
                    data_key = mask_name + '_' + boolean_index + '_' + _list[3]
                elif fracture_type == 2:
                    # data_key = mask_name + '_' + boolean_index
                    data_key = mask_name + '_' + boolean_index + '_' + _list[3]
                _operation = self.get_value_from_db_by_data_key(tip_no, _list[1], _list[2], data_key)
                e_layers_list = re.findall(r'\d+;\d+', _operation)

                if fracture_type == 1:
                    if _list[3] == Constant.TOOLING_FORM_DEVICE_INFO_SOURCE_DB1:
                        str = ' '.join(e_layers_list)
                    elif _list[3] == Constant.TOOLING_FORM_DEVICE_INFO_SOURCE_DB2:
                        db_list = re.findall(r'\[' + Constant.TOOLING_FORM_DEVICE_INFO_SOURCE_DB2 + '\]\w\d+;\d+',
                                             _operation)
                        str = ' '.join(db_list)
                        db_list = re.findall(r'\d+;\d+', str)
                        str = ' '.join(db_list)
                    elif _list[3] == Constant.TOOLING_FORM_DEVICE_INFO_SOURCE_DB3:
                        db_list = re.findall(r'\[' + Constant.TOOLING_FORM_DEVICE_INFO_SOURCE_DB3 + '\]\w\d+;\d+',
                                             _operation)
                        str = ' '.join(db_list)
                        db_list = re.findall(r'\d+;\d+', str)
                        str = ' '.join(db_list)

                elif fracture_type == 2:
                    str = '  INPUT1.'.join(e_layers_list)
                    str = 'INPUT1.' + str
                    str = str.replace(';', ':')
                return str

            elif _list[1] == Constant.TOOLING_FORM_EXCEL_SHEET_BOOLEAN_INFO and (
                    _list[2] == Constant.TOOLING_FORM_EXCEL_SHEET_BOOLEAN_INFO_TOTAL_BIAS):
                if fracture_type == 1:
                    data_key = mask_name + '_' + boolean_index + '_' + _list[3]
                elif fracture_type == 2:
                    data_key = mask_name + '_' + boolean_index
                return self.get_value_from_db_by_data_key(tip_no, _list[1], _list[2], data_key)

            elif _list[1] == Constant.TOOLING_FORM_EXCEL_SHEET_TAPEOUT_INFO and (
                    _list[2] == Constant.TOOLING_FORM_EXCEL_SHEET_TAPEOUT_INFO_MASK_NAME):
                return mask_name[-5:]
            elif _list[1] == 'Fracture_Path':
                return fracture_path

        elif _list[0] == 'CO':
            if _list[1] == 'HOST_FILE':
                return Constant.FRACTURE_VSB12I_HOST_FILE_NAME

    # package host_file content from db
    def package_host_file(self):
        # query dictionary where type= FRACTURE_HOST_FILE
        _o = dict.objects.get(is_delete=0, type=Constant.FRACTURE_HOST_FILE_DICT_TYPE_NAME)
        _dict_list = dict.objects.filter(is_delete=0, parent_id=_o.id)
        text = ""
        for _dict in _dict_list:
            text = text + _dict.value + "\n"
        return text

    # package mrcexe_lsf.sh content from db
    def package_mrcexe_lsf_sh(self):
        # query dictionary where type= FRACTURE_mrcexe_lsf
        _o = dict.objects.get(is_delete=0, type=Constant.FRACTURE_MRCEXE_LSF_SH_DICT_TYPE_NAME)
        _dict_list = dict.objects.filter(is_delete=0, parent_id=_o.id).order_by('sort')
        text = ""
        for _dict in _dict_list:
            text = text + _dict.value + "\n"
        return text

    # query data from db
    def get_value_from_db_by_data_key(self, tip_no, sheet_name, column_name, data_key):
        print('tip_no=%s,sheet_name=%s,column_name=%s,data_key=%s' % (tip_no, sheet_name, column_name, data_key))
        log.info('get_value_from_db_by_data_key():tip_no=%s,sheet_name=%s,column_name=%s,data_key=%s' % (
            tip_no, sheet_name, column_name, data_key))
        _o = ""
        return _o.import_data

    # query list from db
    def get_list_from_db_by_data_key(self, tip_no, sheet_name, column_name, data_key):
        _list = ""
        return _list

    # query data from db
    def get_value_from_db(self, tip_no, sheet_name, column_name):
        _o = ""
        return _o.import_data

    # get total_bias
    def get_mask_tone(self, tip_no, mask_name):
        _list = list()
        if _list.count() > 0:
            _o = _list[0]
            return _o.import_data
        return ''

    # get boolean by device
    def get_device_boolean(self, tip_no, device_name):
        _o_list = list()
        if _o_list.count() > 0:
            return _o_list[0].import_data

    # get db
    def get_source_db(self, tip_no, device_name, boolean_index):
        _data_key = device_name + '_' + boolean_index
        _list_db = list()
        _list = []
        for item in _list_db:
            _list.append(item.import_data)
        return _list

    # get mask_type
    def get_mask_type(self, tip_no, mask_name):
        _mask_type = self.get_value_from_db_by_data_key(tip_no, Constant.TOOLING_FORM_EXCEL_SHEET_TAPEOUT_INFO,
                                                        Constant.TOOLING_FORM_EXCEL_SHEET_TAPEOUT_INFO_MASK_TYPE,
                                                        mask_name)
        if _mask_type == Constant.TOOLING_FORM_EXCEL_SHEET_TAPEOUT_INFO_MASK_TYPE_PSM:
            _mask_type = 'Y'
        else:
            _mask_type = 'N'
        return _mask_type

    # get vsb12i_db1 template text
    def get_vsb12i_db1_template_content(self):
        _o = _template_list = template.objects.get(is_delete=0,
                                                   template_type=Constant.SCRIPT_TEMPLATE_VSB12i_DB1_FILE_TYPE)
        return _o.file_name, _o.template_text

    # get vsb12_db1 template text
    def get_vsb12_db1_template_content(self):
        _o = _template_list = template.objects.get(is_delete=0,
                                                   template_type=Constant.SCRIPT_TEMPLATE_VSB12_DB1_FILE_TYPE)
        return _o.file_name, _o.template_text

    # get vsb12i_db1_db2 template text
    def get_vsb12i_db1_db2_template_content(self):
        _o = _template_list = template.objects.get(is_delete=0,
                                                   template_type=Constant.SCRIPT_TEMPLATE_VSB12i_DB1_DB2_FILE_TYPE)
        return _o.file_name, _o.template_text

    # get vsb12_db1_db2 template text
    def get_vsb12_db1_db2_template_content(self):
        _o = _template_list = template.objects.get(is_delete=0,
                                                   template_type=Constant.SCRIPT_TEMPLATE_VSB12_DB1_DB2_FILE_TYPE)
        return _o.file_name, _o.template_text

    # get mode5_db1 template text
    def get_mode5_db1_template_content(self):
        _o = _template_list = template.objects.get(is_delete=0,
                                                   template_type=Constant.SCRIPT_TEMPLATE_MODE5_DB1_FILE_TYPE)
        return _o.file_name, _o.template_text

    # get mode5_db2 template text
    def get_mode5_db1_db2_template_content(self):
        _o = _template_list = template.objects.get(is_delete=0,
                                                   template_type=Constant.SCRIPT_TEMPLATE_MODE5_DB1_DB2_FILE_TYPE)
        return _o.file_name, _o.template_text

    # get vsb12i attr file content from mdt table
    def get_vsb12i_attr_content_from_mdt_table(self, tip_no, mask_name, tool_id, _tf_design_rule, _tf_mask_tone,
                                               _tf_mask_grade, blank, _tf_layer_name):

        if tool_id != 'MS03':
            mdt_type = 1
            _o_mdt = released_info.objects.filter(is_delete=0, layer=_tf_layer_name, node=_tf_design_rule,
                                                  tone=_tf_mask_tone, grade=_tf_mask_grade, tool=tool_id, blank=blank,
                                                  type='MDT').order_by('-version')[0]
        else:
            mdt_type = 2
            _o_mdt = released_info_alta.objects.filter(is_delete=0, layer=_tf_layer_name, node=_tf_design_rule,
                                                       tone=_tf_mask_tone, grade=_tf_mask_grade, tool=tool_id,
                                                       blank=blank,
                                                       type='MDT').order_by('-version')[0]
        if _o_mdt:
            _list_cat_layer = released_mdt.objects.filter(is_delete=0, released_id=_o_mdt.id, type=mdt_type)
            _text = ''
            for layer in _list_cat_layer:
                _text = _text + 'layer ' + layer.cad_layer + ';' + layer.data_type + '\n'
                _text = _text + layer.writer_mdt + '\n'
        else:
            _text = 'MDT未定义'
        return _text

    # check db count
    def check_source_db(self, tip_no, _device_name, _boolean_index):
        # get source_db
        _db_list = self.get_source_db(tip_no, _device_name, _boolean_index)
        # check source_db count,if has db1 only
        _source_db1 = ''
        _source_db2 = ''
        _count = _db_list.__len__()
        if _db_list.count == 0:
            raise Exception(Constant.FRACTURE_SOURCE_DB_COUNT_ERROR)
        if _count == 1 and Constant.TOOLING_FORM_DEVICE_INFO_SOURCE_DB1 in _db_list:
            _source_db1 = Constant.TOOLING_FORM_DEVICE_INFO_SOURCE_DB1
            return _source_db1, ''
        elif _count == 1 and Constant.TOOLING_FORM_DEVICE_INFO_SOURCE_DB2 in _db_list:
            _source_db2 = Constant.TOOLING_FORM_DEVICE_INFO_SOURCE_DB2
            return '', _source_db2
        elif _count > 1 and Constant.TOOLING_FORM_DEVICE_INFO_SOURCE_DB1 in _db_list \
                and Constant.TOOLING_FORM_DEVICE_INFO_SOURCE_DB2 in _db_list:
            _source_db1 = Constant.TOOLING_FORM_DEVICE_INFO_SOURCE_DB1
            _source_db2 = Constant.TOOLING_FORM_DEVICE_INFO_SOURCE_DB2
            return _source_db1, _source_db2

    # validate mdt table data
    def validate_Fracture_mdt_table(self, lot_id, tip_no, mask_name, tool_id, device_name, stage_name):
        data = {}

        # tooling form Design rule
        tooling_prod_inf = tooling_product_info.objects.filter(tip_no=tip_no, is_delete='0').first()
        _tf_design_rule = tooling_prod_inf.design_rule
        customer = tooling_prod_inf.customer
        # tooling form layer name
        if mask_name.find("-") >= 0:
            _layerver = mask_name.split("-")[1]
            _tf_layer_name = _layerver[0:3]
            product = mask_name.split("-")[0]

        # tooling form tone
        _device_in = tooling_device_info.objects.filter(tip_no=tip_no, mask_name=mask_name,
                                                        device_name=device_name, is_delete='0').first()
        _tf_mask_tone = tooling_boolean_info.objects.filter(tip_no=tip_no, mask_name=mask_name,
                                                            boolean_index=_device_in.boolean_index,
                                                            is_delete='0').first().tone
        # tooling form mask_grade
        _tape_inf = tooling_tapeout_info.objects.filter(tip_no=tip_no, mask_name=mask_name, layer_name=_tf_layer_name,
                                                        is_delete='0').first()
        _tf_mask_grade = _tape_inf.grade
        _tf_mask_type = _tape_inf.mask_type
        _blank = mes_blank_code.objects.filter(tone=_tf_mask_tone, mask_type=_tf_mask_type, is_delete='0').first()
        try:
            # mdt table design_rule
            if tool_id != 'MS03':
                mdt_type = 1
                _o_mdt = released_info.objects.filter(is_delete=0, blank=_blank.blank_code, layer=_tf_layer_name,
                                                      node=_tf_design_rule,
                                                      tone=_tf_mask_tone, grade=_tf_mask_grade, tool=tool_id,
                                                      customer=customer,
                                                      type='MDT').order_by('-version')[0]
            else:
                mdt_type = 2
                _o_mdt = released_info_alta.objects.get(is_delete=0, blank=_blank.blank_code, layer=_tf_layer_name,
                                                        node=_tf_design_rule,
                                                        tone=_tf_mask_tone, grade=_tf_mask_grade, tool=tool_id,
                                                        customer=customer,
                                                        type='MDT').order_by('-version')[0]
            data['success'] = True
            data['msg'] = 'success'
        except:
            traceback.print_exc()
            _o_mdt = None
            # raise Exception('layer name error in mdt table!')
            data["success"] = False
            data[
                "msg"] = 'info tree is not defined'
            return data, '', '', '', ''

        _mdt_mask_tone = _o_mdt.tone
        _mdt_mask_grade = _o_mdt.grade
        _mdt = _o_mdt.value
        w_m = writer_mapping.objects.order_by('seq').filter(Q(customer=tooling_prod_inf.customer) | Q(customer='*'),
                                                            Q(design_rule=_tf_design_rule) | Q(design_rule='*'),
                                                            Q(product=product) | Q(product='*'),
                                                            Q(layer_name=_tf_layer_name) | Q(layer_name='*'),
                                                            Q(product_type=tooling_prod_inf.product_type) | Q(
                                                                product_type='*'),
                                                            Q(mask_type=_tape_inf.mask_type) | Q(mask_type='*'),
                                                            Q(tone=_mdt_mask_tone) | Q(tone='*'),
                                                            grade_from__lte=_mdt_mask_grade,
                                                            grade_to__gte=_mdt_mask_grade,
                                                            is_delete=0
                                                            # grade_from__in=[chr(x) for x in range(65, 91)],
                                                            )
        t_m = tool_maintain.objects.get(tool_id=w_m.first().catalog_tool_id)
        _machine = tool_name_route.objects.get(catalog_tool_id=t_m.tool_id)
        if _machine.machine_type == Constant.WRITER_TYPE_MODE5:
            _format = 'MODE5'
        elif _machine.machine_type == Constant.WRITER_TYPE_VSB:
            if _mdt == 'Y':
                _format = 'VSB12I'
            elif _mdt == 'N':
                _format = 'VSB12'
        fracture_inf = fracture_deck.objects.filter(format=_format, stage_name=stage_name).first()

        if _mdt == 'Y':
            # query operation from tooling form
            _list_operation = list()
            _list_operation = tooling_boolean_info.objects.filter(mask_name=mask_name, is_delete=0)
            _operation_str = ''
            for operation in _list_operation:
                _operation_str = _operation_str + operation.operation
            _list_operation = re.findall(r'\d+;\d+', _operation_str)

            _list_cat_layer = released_mdt.objects.filter(is_delete=0, released_id=_o_mdt.id, type=mdt_type)
            if _list_cat_layer:
                for cat_layer in _list_cat_layer:
                    _layer = cat_layer.cad_layer + ';' + cat_layer.data_type
                    if _layer not in _list_operation:
                        data["success"] = False
                        data["msg"] = Constant.FRACTURE_CAD_LAYER_NOT_DEFINE_IN_TOOLING_FORM.format(_layer)
                        return data, _mdt, _o_mdt, fracture_inf.file, fracture_inf.path
            else:
                data['success'] = False
                data['msg'] = 'cad layer is not define'
                return data, _mdt, _o_mdt

        return data, _mdt, _o_mdt, fracture_inf.file, fracture_inf.path

    def generate_deck_content(self, lot_id, tip_no, device_name, mask_name, boolean_index, mdt, stage_name, _db_path):
        # get source_db
        _source_db1, _source_db2 = self.check_source_db(tip_no, device_name, boolean_index)
        _format = ''
        _db_cnt = 0
        # query writer type by lot_id  from lot_info
        _lot_info = lot_info.objects.get(lot_id=lot_id)
        _machine = tool_name_route.objects.get(id=_lot_info.machine_id)
        if _machine.machine_type == Constant.WRITER_TYPE_MODE5:
            if _source_db1 != '' and _source_db2 == '':
                _format = 'MODE5'
                _db_cnt = 1
            elif _source_db1 != '' and _source_db2 != '':
                _format = 'MODE5'
                _db_cnt = 2
            else:
                # raise Exception('source db error!')
                return Constant.COMMON_METHOD_RETURN_FLAG_ERROR, Constant.FRACTURE_SOURCE_DB_ERROR, '', ''
        elif _machine.machine_type == Constant.WRITER_TYPE_VSB:
            if mdt == 'Y' and _source_db1 != '' and _source_db2 == '':
                _format = 'VSB12I'
                _db_cnt = 1
            elif mdt == 'Y' and _source_db1 != '' and _source_db2 != '':
                _format = 'VSB12I'
                _db_cnt = 2
            elif mdt == 'N' and _source_db1 != '' and _source_db2 == '':
                _format = 'VSB12'
                _db_cnt = 1
            elif mdt == 'N' and _source_db1 != '' and _source_db2 != '':
                _format = 'VSB12'
                _db_cnt = 2
            else:
                # raise Exception('source db error!')
                return Constant.COMMON_METHOD_RETURN_FLAG_ERROR, Constant.FRACTURE_SOURCE_DB_ERROR, '', ''
        else:
            return Constant.COMMON_METHOD_RETURN_FLAG_ERROR, Constant.FRACTURE_WRITER_ERROR, '', ''

        _o = fracture_deck.objects.filter(db_count=_db_cnt)
        _o = fracture_deck.objects.get(format=_format, db_count=_db_cnt)
        _template_content = file_readline(_o.path + _o.file)
        _file_name, _deck_content = self.deck_replacement(tip_no=tip_no, template_content=_template_content,
                                                          db_cnt=_db_cnt, writer=_format, device_name=device_name,
                                                          mask_name=mask_name, boolean_index=boolean_index,
                                                          _db_path=_db_path)
        return _file_name, _deck_content

    def deck_replacement(self, tip_no, template_content, db_cnt, writer, device_name, mask_name, boolean_index,
                         _db_path):
        _list = deck_para.objects.filter(writer__contains=writer, db_count=db_cnt)
        _template_content = []
        _file_name = ''
        for para in _list:
            if _template_content.__len__() > 0:
                template_content = copy.deepcopy(_template_content)
                _template_content.clear()
            _value = catch_value(val=para.value_out.strip(), device_name=device_name, mask_name=mask_name,
                                 tip_no=tip_no, boolean_index=boolean_index, _db_path=_db_path)
            if para.item.strip() == 'Input':
                _value = join_path(_db_path, _value)
            if para.item.strip() == 'Resolution':
                _value = float(_value) * 4
                _value = str(_value)
            if para.item.strip() == 'Attributes':
                _value = _value.replace('-', '_', 1) + '.attr'
            if para.ref1.strip() == 'deck_name':
                _value_tp = _value.split(",")
                if writer == 'MODE5':
                    _file_name = _value_tp[0] + '_' + _value_tp[1].split('-')[-1] + '_' + _value_tp[2] + '_MEBES.sh'
                if writer == 'VSB12' or writer == 'VSB12I':
                    _file_name = _value_tp[0] + '_' + _value_tp[1].split('-')[-1] + '_' + _value_tp[2] + '_fracture.sh'
            if para.ref2:
                if para.ref1.strip() == 'SWITCH':
                    ref_flag = 0
                    for line in template_content:
                        if line.__len__() > 3:
                            _list_line = line.split()
                            if _list_line[0] == para.ref1.strip():
                                ref_flag = 1
                                continue
                            if _list_line[0] == para.ref2.strip() and ref_flag == 1:
                                if para.ref2.strip() == 'Limits':
                                    _value_tp = _value.split(",")
                                    line = _list_line[0] + ' (INPUT ' + _value_tp[0] + ',' + _value_tp[
                                        1] + ') (INPUT ' + _value_tp[2] + ',' + _value_tp[3] + ')' + "\n"
                                elif para.ref2.strip() == 'Layers':
                                    _value = _value.replace('(', '', 6)
                                    _value = _value.replace(')', '', 6)
                                    _value = _value.replace('L', '', 6)
                                    _value = _value.replace('+', ' ', 6)
                                    line = _list_line[0] + ' ' + _value + "\n"
                                elif para.ref2.strip() == 'Output':
                                    _value_tp = _value.split(",")
                                    if writer == 'MODE5':
                                        line = _list_line[0] + ' ./' + _value_tp[0] + '_' + _value_tp[
                                            1] + '_00.cflt' + "\n"
                                    if writer == 'VSB12' or writer == 'VSB12I':
                                        line = _list_line[0] + ' ./' + _value_tp[0] + '_' + _value_tp[
                                            1] + '/chip.cnf' + "\n"
                                else:
                                    line = line.replace(_list_line[1], _value)
                        _template_content.append(line)
            else:
                for line in template_content:
                    if line.__len__() > 3:
                        _list_line = line.split()
                        if _list_line[0] == para.ref1.strip():
                            if para.ref1.strip() == 'Limits':
                                _value_tp = _value.split(",")
                                line = _list_line[0] + ' (INPUT ' + _value_tp[0] + ',' + _value_tp[1] + ') (INPUT ' + \
                                       _value_tp[2] + ',' + _value_tp[3] + ')' + "\n"
                            elif para.ref1.strip() == 'Layers':
                                _value = _value.replace('(', '', 6)
                                _value = _value.replace(')', '', 6)
                                _value = _value.replace('L', '', 6)
                                _value = _value.replace('+', ' ', 6)
                                line = _list_line[0] + ' ' + _value + "\n"
                            elif para.ref1.strip() == 'Output':
                                _value_tp = _value.split(",")
                                if writer == 'MODE5':
                                    line = _list_line[0] + ' ./' + _value_tp[1].replace('-', '_', 1) + '_' + _value_tp[
                                        2] + '_00.cflt' + "\n"
                                if writer == 'VSB12' or writer == 'VSB12I':
                                    line = _list_line[0] + ' ./' + _value_tp[1].replace('-', '_', 1) + '_' + _value_tp[
                                        2] + '/chip.cnf' + "\n"
                            else:
                                line = line.replace(_list_line[1], _value)
                    _template_content.append(line)
        template_content_ = ''
        for line in _template_content:
            template_content_ = template_content_ + line

        return _file_name, template_content_

    def convert_deck(self, lot_id, tip_no, mask_name, device_name, _stage, _prestage, _pre_stage_path, _file, deck_type,
                     customer, input_path, input_path2, output_path, input_name, out_gds_path, recipe_id):
        tool_id = lot_info.objects.filter(tip_no=tip_no, mask_name=mask_name, is_delete=0).first().info_tree_tool_id
        data = {}
        old_line = ''
        _template_content = file_readline(_file)
        template_content = []
        if mask_name.find("-") >= 0:
            _layerver = mask_name.split("-")[1]
            mask_id = _layerver[0:3]
            product = mask_name.split("-")[0]
        if mask_name.find("_") >= 0:
            _layerver = mask_name.split("_")[1]
            mask_id = _layerver[0:3]
            product = mask_name.split("_")[0]
        base_path = get_work_path(product, mak=1)
        device_path = get_device_path(join_path(base_path, Constant.FILE_PATH_DEVICE), device_name, mak=1)
        db_path = get_db_path(device_path, mak=1)
        if customer == 'out':
            _device_inf = tooling_device_info.objects.filter(tip_no=tip_no, device_name=device_name,
                                                             mask_name=mask_name, is_delete=0).first()
            _topcell = _device_inf.top_structure
            _source_db = _device_inf.file_name
            if _stage == Constant.STAGE_FRACTURE or _stage == Constant.STAGE_FRACTURE_XOR:
                _structure = tooling_device_info.objects.filter(tip_no=tip_no, mask_name=mask_name,
                                                                device_name=device_name,
                                                                is_delete=0).first().top_structure
                _resolution = str(float(
                    tooling_boolean_info.objects.filter(tip_no=tip_no, mask_name=mask_name,
                                                        boolean_index=_device_inf.boolean_index,
                                                        is_delete=0).first().grid) * 4)
                _operation = tooling_boolean_info.objects.filter(tip_no=tip_no, mask_name=mask_name,
                                                                 boolean_index=_device_inf.boolean_index,
                                                                 is_delete=0).first().operation
                _layers = _operation.replace("+", " ").replace("(", "").replace(")", "").replace("L", "")
                #                _layers = '51;0 51;2 51;3'
                #                if _layerver[0] == '8':
                #                    _layers = '61;0 61;2 61;3'
                lay_str = ""
                _xor_layer = _layers.split()
                cnt1 = 0
                for _lay in _xor_layer:
                    if cnt1 == 0:
                        lay_str = lay_str + 'INPUT1.' + _lay.replace(";", ":")
                    else:
                        lay_str = lay_str + ' INPUT1.' + _lay.replace(";", ":")
                    cnt1 = cnt1 + 1
                _lbx = _device_inf.lb_x
                _lby = _device_inf.lb_y
                _rtx = _device_inf.rt_x
                _rty = _device_inf.rt_y
                if _stage == Constant.STAGE_FRACTURE_XOR:
                    _lbx = str(float(_device_inf.lb_x) * 1000)
                    _lby = str(float(_device_inf.lb_y) * 1000)
                    _rtx = str(float(_device_inf.rt_x) * 1000)
                    _rty = str(float(_device_inf.rt_y) * 1000)
                _limits = '(INPUT ' + _lbx + ',' + _lby + ') (INPUT ' + _rtx + ',' + _rty + ')'
                _chip_window = '(' + _lbx + ' ' + _lby + ' ' + _rtx + ' ' + _rty + ')'
                _scale = tooling_tapeout_info.objects.filter(tip_no=tip_no, mask_name=mask_name,
                                                             is_delete=0).first().mask_mag
                _grow = tooling_boolean_info.objects.filter(tip_no=tip_no, mask_name=mask_name,
                                                            boolean_index=_device_inf.boolean_index,
                                                            is_delete=0).first().total_bias
                _orientation = _device_inf.rotate
                _attributes = mask_name.replace('-', '_', 1) + '.attr'
        out_source_type = 'OASIS'
        source_db_path = join_path(db_path, _source_db)
        # in_gds_name = tip_no + '_' + device_name + '_' + _layerver + '_' + _prestage.replace(" ", "_", 1) + '.oas'
        in_gds_name = _source_db
        in_gds_path = join_path(_pre_stage_path, in_gds_name)
        if (_prestage == 'TIP start' or _prestage == ''):
            in_gds_path = source_db_path
        out_gds_name = tip_no + '_' + device_name + '_' + _layerver + '_' + _stage.replace(" ", "_", 1) + '.oas'
        source_type = 'OASIS'
        if in_gds_name.lower().find('gds') >= 0:
            source_type = 'GDS2'
        if _stage == Constant.STAGE_FRACTURE:
            alta_name = self.Alta_naming(tip_no, product, device_name, mask_name)
            con_ = convert_status.objects.filter(tip_no=tip_no, device_name=device_name, mask_name=mask_name,
                                                 stage=Constant.STAGE_FRACTURE).first()
            con_.alta_name = alta_name
            con_.save()
            for line in _template_content:
                if line.__len__() > 3:
                    _list_line = line.split()
                    if _list_line[0] == 'Resolution':
                        val = _resolution
                        line = line.replace(_list_line[1], val)
                    if _list_line[0] == 'Input':
                        val = in_gds_path
                        line = line.replace(_list_line[1], val)
                    if _list_line[0] == 'Structure':
                        val = _structure
                        line = line.replace(_list_line[1], val)
                    if _list_line[0] == 'Layers':
                        val = _layers
                        line = 'Layers ' + _layers + "\n"
                    if _list_line[0] == 'Limits':
                        val = _limits
                        line = 'Limits ' + _limits + "\n"
                    if _list_line[0] == 'Scale':
                        val = _scale
                        line = line.replace(_list_line[1], val)
                    if _list_line[0] == 'Grow':
                        val = _grow
                        line = line.replace(_list_line[1], val)
                    if _list_line[0] == 'Orientation':
                        val = _orientation
                        line = line.replace(_list_line[1], val)
                    if _list_line[0] == 'Attributes':
                        val = _attributes
                        line = line.replace(_list_line[1], val)
                    if _list_line[0] == 'Output':
                        val = './' + product + '_' + _layerver + '_' + device_name + '/chip.cnf'
                        line = line.replace(_list_line[1], val)
                    if _list_line[0] == 'out':
                        val = './' + product + '_' + _layerver + '_' + device_name + '_JDV' + '/' + alta_name + '_00.cflt'
                        line = line.replace(_list_line[1], val)
                template_content.append(line)
        if _stage == Constant.STAGE_FRACTURE_XOR:
            source_type = 'OASIS'
            if source_type.find("GDS") >= 0:
                source_type = 'GDS2'
            input_flag = 0
            output_flag = 0
            cmd_flag = 0
            for line in _template_content:
                if line.find("MASTER_WORK") >= 0:
                    master_time = './master' + time.strftime("%Y%m%d%H%M%S", time.localtime())
                    _value = line.split("=")
                    line = _value[0] + '= ' + master_time + ";\n"
                if line.find("INPUT1") >= 0:
                    input_flag = 1
                    output_flag = 0
                    gds_name = source_db_path
                    if gds_name.lower().find('.gds') >= 0:
                        source_type = 'GDS2'
                    if gds_name.lower().find('.oas') >= 0:
                        source_type = 'OASIS'
                if line.find("INPUT2") >= 0:
                    input_flag = 2
                    output_flag = 0
                    layer_path = get_layer_path(join_path(device_path, Constant.FILE_PATH_LAYER), _layerver, mak=1)
                    _pre_stage_path = get_fracture_path(layer_path, mak=1)
                    chip_dir = join_path(_pre_stage_path, mask_name.replace("-", "_") + '_' + device_name)
                    gds_name = join_path(chip_dir, 'chip.cnf')
                if line.find("OUTPUT") >= 0:
                    output_flag = 1
                    input_flag = 0
                    gds_name = out_gds_name
                if line.find("COMMAND") >= 0:
                    cmd_flag = 1
                if line.__len__() > 3:
                    if line.find("FILENAME") >= 0:
                        _value = line.split("=")
                        line = _value[0] + '= ' + gds_name + ";\n"
                    if input_flag == 1 and line.find("TOPCELL") >= 0:
                        _value = line.split("=")
                        line = _value[0] + '= ' + _topcell + ";\n"
                    if input_flag == 1 and line.find("TYPE") >= 0:
                        _value = line.split("=")
                        line = _value[0] + '= ' + source_type + ";\n"
                    if input_flag == 1 and line.find("SCALE") >= 0:
                        _value = line.split("=")
                        line = _value[0] + '= ' + _scale + ";\n"
                    if input_flag == 1 and line.find("CHIP_WINDOW") >= 0:
                        _value = line.split("=")
                        line = _value[0] + '= ' + _chip_window + ";\n"
                    if output_flag == 1 and line.find("TOPCELL") >= 0:
                        _value = line.split("=")
                        line = _value[0] + '= ' + _topcell + ";\n"
                    if cmd_flag == 1 and line.find("OR INPUT1") >= 0:
                        line = line.replace("INPUT1.51", lay_str)
                template_content.append(line)
        template_content_ = ''
        for line in template_content:
            template_content_ = template_content_ + line
        create_file(_file, template_content_)

        data["success"] = True
        data["msg"] = "success"
        return data

    def Alta_naming(self, tip_no, prod, device_name, mask_name):
        today = datetime.now().strftime("%Y-%m-%d")
        tapeout_ = tooling_tapeout_info.objects.filter(tip_no=tip_no, mask_name=mask_name, is_delete=0).first()
        version_ = tapeout_.version[0:1]
        layer_ = tapeout_.no
        alta_list = alta_naming_table.objects.filter(prod_name=prod, device_name=device_name, layer=tapeout_.no,
                                                     version=version_).order_by("-id").first()
        dev_ = ''
        prod_count_ = ''
        if alta_list:
            ver_ser = alta_list.version_serial
            #           if ver_ser == 'Z':
            #               ver_ = alta_list.version
            #               ver_ = int(ver_, 36)
            #               ver_ = ver_ + 1
            #               new_ver_ = self.to_36(int(ver_))
            #               new_ver_ser = '0'
            #               alta_name_ = alta_list.alta_name[0:9] + new_ver_  + new_ver_ser
            #               alta_list.version = new_ver_
            #           else:
            if ver_ser == 'Z':
                ver_ser = '0'
            ver_ser = int(ver_ser, 36)
            ver_ser = ver_ser + 1
            new_ver_ser = self.to_36(int(ver_ser))
            alta_name_ = alta_list.alta_name[0:10] + new_ver_ser

            alta_list.alta_name = alta_name_
            alta_list.version_serial = new_ver_ser
            alta_list.save()

        else:
            year_ = datetime.now().strftime("%Y")[2:4]
            month_ = str(hex(int(datetime.now().strftime("%m")))).replace('0x', '')
            day_ = self.to_36(int(datetime.now().strftime("%d")))
            prod_day_alta_list_cnt = alta_naming_table.objects.filter(submit_date=today, prod_name=prod,
                                                                      device_name=device_name).count()
            if prod_day_alta_list_cnt > 0:
                prod_count_ = self.to_36(int(prod_day_alta_list_cnt))
                prod_day_alta_list = alta_naming_table.objects.filter(submit_date=today, prod_name=prod,
                                                                      device_name=device_name)
                for prod_ in prod_day_alta_list:
                    if (prod_.device_serial[0:1].upper().find("M") >= 0 or prod_.device_serial[0:1].upper().find(
                            "N") or prod_.device_serial[0:1].upper().find("O") or prod_.device_serial[0:1].upper().find(
                        "P") or prod_.device_serial[0:1].upper().find("Q") or prod_.device_serial[0:1].upper().find(
                        "R") or prod_.device_serial[0:1].upper().find("S")):
                        M_serial = prod_.device_serial
                    if (prod_.device_serial[0:1].upper().find("F") >= 0):
                        F_serial = prod_.device_serial
                    if (prod_.device_serial[0:1].upper().find("T") or prod_.device_serial[0:1].upper().find(
                            "U") or prod_.device_serial[0:1].upper().find("V") or prod_.device_serial[0:1].upper().find(
                        "W") or prod_.device_serial[0:1].upper().find("X") or prod_.device_serial[0:1].upper().find(
                        "Y") or prod_.device_serial[0:1].upper().find("Z")):
                        T_serial = prod_.device_serial
                deviceinfo_ = tooling_device_info.objects.filter(tip_no=tip_no, device_name=device_name,
                                                                 is_delete=0).first()
                if deviceinfo_.device_type == "Main":
                    if M_serial[1] == 'Z':
                        m_ = int(M_serial[0], 36) + 1
                        dev_ = self.to_36(m_) + '1'
                    else:
                        m_ = int(M_serial[1], 36) + 1
                        dev_ = M_serial[0] + self.to_36(m_)
                if deviceinfo_.device_type == "Frame" or deviceinfo_.device_type == "F+M":
                    if F_serial[1] == 'Z':
                        m_ = int(F_serial[0], 36) + 1
                        dev_ = self.to_36(m_) + '1'
                    else:
                        m_ = int(F_serial[1], 36) + 1
                        dev_ = F_serial[0] + self.to_36(m_)
                if deviceinfo_.device_type == "Test":
                    if T_serial[1] == 'Z':
                        m_ = int(T_serial[0], 36) + 1
                        dev_ = self.to_36(m_) + '1'
                    else:
                        m_ = int(T_serial[1], 36) + 1
                        dev_ = T_serial[0] + self.to_36(m_)


            else:
                day_alta_list_cnt = alta_naming_table.objects.filter(submit_date=today).values(
                    'prod_name').distinct().count()
                prod_count_ = self.to_36(day_alta_list_cnt + 1)
                deviceinfo_ = tooling_device_info.objects.filter(tip_no=tip_no, device_name=device_name,
                                                                 is_delete=0).first()
                if deviceinfo_.device_type == "Main":
                    dev_ = 'M1'
                if deviceinfo_.device_type == "Frame" or deviceinfo_.device_type == "F+M":
                    dev_ = 'F1'
                if deviceinfo_.device_type == "Test":
                    dev_ = 'T1'
            alta_name_ = year_ + month_ + day_ + prod_count_ + dev_ + str(layer_) + '_' + version_ + '0'
            alta_naming_table.objects.create(tip_no=tip_no, mask_name=mask_name, submit_date=today, prod_name=prod,
                                             prod_serial=prod_count_, device_name=device_name, device_serial=dev_,
                                             layer=str(layer_), version=version_, version_serial='0',
                                             alta_name=alta_name_)

        return alta_name_

    def to_36(self, number):
        num_str = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if number == 0:
            return '0'

        base36 = []
        while number != 0:
            number, i = divmod(number, 36)  # 返回 number// 36 , number%36
            base36.append(num_str[i])

        return ''.join(reversed(base36))
