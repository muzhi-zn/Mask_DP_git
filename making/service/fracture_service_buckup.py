# coding:utf-8
"""jdv/generate file/ process method

"""
import os
import re
import logging
from utilslibrary.base.base import BaseService
from system.models import template, dict
from machine.models import machine_basic
from django.conf import settings
from shutil import rmtree
from django.db import transaction

from utilslibrary.utils.common_utils import getCurrentSessionID, getCurrentSessionName
from utilslibrary.utils.file_utils import create_file
from utilslibrary.system_constant import Constant
from tooling.models import import_data
from django.http.response import HttpResponseRedirect, JsonResponse
from utilslibrary.utils.file_utils import *
from making.models import mdt_info, mdt_cad_layer
from jdv.models import lot_info, lot_trail
from jdv.service.lot_trail_service import LotTrailService
log = logging.getLogger('LOGGING')


class GenerateFileService(BaseService):

    def fracture_deck(self, user_id, user_name, lot_id, tip_no, mask_name, device_name):
        # _o = lot_info.objects.get(lot_id=lot_id)

        # mask_name = _o.mask_name
        # tip_no = _o.tip_no
        # query data from db
        # product
        _product = self.get_value_from_db(tip_no, Constant.TOOLING_FORM_EXCEL_SHEET_PRODUCT_INFO,
                                          Constant.TOOLING_FORM_EXCEL_SHEET_PRODUCT_INFO_PRODUCT)
        # validate data
        data, mdt = self.validate_Fracture_mdt_table(lot_id, tip_no, mask_name)
        if data.__len__() > 0:
            LotTrailService().insert_trail(user_id=user_id, user_name=user_name, lot_id=lot_id, tip_no=tip_no, stage='Generate File',
                                           stage_desc=data['msg'], remark='', is_error=Constant.LOT_STAGE_IS_ERROR_YES)
            return data

        return self.fracture_template_generate(user_id=user_id, user_name=user_name,lot_id=lot_id, device_name=device_name,
                                               mask_name=mask_name, tip_no=tip_no,
                                               product=_product, mdt=mdt)

    # template file generate
    # mask_name:
    # tip_no:
    # product:
    # host_file_content:
    # mrcexe_lsf_content:
    # mdt:Y：vsb12i,need generate .attr file N:vsb12.donnot generate .attr file
    def fracture_template_generate(self, user_id, user_name, lot_id, device_name, mask_name, tip_no, product, mdt):
        # get layer name:120A1 in TIM001-120A1
        _layer = mask_name[-5:]
        # response data
        data = {}
        # generated file list
        _list_file = ''
        # make dirs
        base_path = get_work_path(product, mak=1)

        # query device list by tip_no
        _device_list = []
        if device_name:
            _device_list.append({'import_data': device_name})
        else:
            _device_list = import_data.objects.values().filter(is_delete=0, tip_no=tip_no,
                                                               sheet_name=Constant.TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO,
                                                               column_name=Constant.TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO_DEVICE_NAME)
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
            #delete all file
            del_file(_fracture_path)
            # get boolean_index
            _boolean_index = self.get_device_boolean(tip_no, _device_name)
            # get source_db
            _source_db1, _source_db2 = self.check_source_db(tip_no, _device_name, _boolean_index)
            _code,_msg,_template_file_name,_template_text = self.get_fracture_template(lot_id=lot_id,tip_no=tip_no,device_name=_device_name,
                                                                                       boolean_index=_boolean_index,mdt=mdt)
            if _code == Constant.COMMON_METHOD_RETURN_FLAG_ERROR:
                # raise Exception('source db error!')
                data["success"] = False
                data["msg"] = _msg
                LotTrailService().insert_trail(user_id=user_id, user_name=user_name, lot_id=lot_id, tip_no=tip_no, stage='Generate File',
                                               stage_desc=data['msg'], remark='',
                                               is_error=Constant.LOT_STAGE_IS_ERROR_YES)

                return data

            file_name, template_text = self.package_fracture_file_content(lot_id=lot_id,_fracture_path=_fracture_path, tip_no=tip_no,
                                                                                 _device_name=_device_name, mask_name=mask_name,
                                                                                 boolean_index=_boolean_index,
                                                                                 _layer=_layer, _db_path=_db_path,
                                                                                 template_file_name=_template_file_name,
                                                                                 template_text=_template_text)
            # generate fracture file
            path = join_path(_fracture_path, file_name)
            create_file(path, template_text)
            _list_file = _list_file + path + '<br>'
            # package host_file content
            host_file_content = self.package_host_file()
            # generate host_file
            path = join_path(_fracture_path, Constant.FRACTURE_VSB12I_HOST_FILE_NAME)
            create_file(path, host_file_content)
            _list_file = _list_file + path + '<br>'
            # generate attr
            if mdt == 'Y':
                _attr_content = self.get_vsb12i_attr_content_from_mdt_table(tip_no, mask_name)
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

        LotTrailService().insert_trail(user_id=user_id, user_name=user_name, lot_id=_o.id, tip_no=tip_no, stage='Generate File',
                                       stage_desc=_list_file, remark='')

        data["success"] = True
        data["msg"] = "success"
        return data

    def fracture_xor_deck(self, user_id, user_name, lot_id):
        print(lot_id)
        _o = lot_info.objects.get(lot_id=lot_id)

        mask_name = _o.mask_name
        tip_no = _o.tip_no
        # query data from db
        # product
        _product = self.get_value_from_db(tip_no, Constant.TOOLING_FORM_EXCEL_SHEET_PRODUCT_INFO,
                                          Constant.TOOLING_FORM_EXCEL_SHEET_PRODUCT_INFO_PRODUCT)
        # if vsb12i
        return self.fracture_xor_template_generate(user_id=user_id, user_name=user_name, lot_id=lot_id, mask_name=mask_name, tip_no=tip_no,
                                                   product=_product)

        # template file generate
        # mask_name:
        # tip_no:
        # product:

    def fracture_xor_template_generate(self, user_id, user_name, lot_id, mask_name, tip_no, product):
        # get layer name:120A1 in TIM001-120A1
        _layer = mask_name[-5:]
        # response data
        data = {}
        # generated file list
        _list_file = ''
        # make dirs
        base_path = get_work_path(product, mak=1)

        # query device list by tip_no
        _device_list = import_data.objects.filter(is_delete=0, tip_no=tip_no,
                                                  sheet_name=Constant.TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO,
                                                  column_name=Constant.TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO_DEVICE_NAME)
        # while device,mkdir
        for _device in _device_list:
            _device_name = _device.import_data

            # package device_path start
            _device_path = get_device_path(join_path(base_path, Constant.FILE_PATH_DEVICE), _device_name, mak=1)
            # package  device/db path
            _db_path = get_db_path(_device_path, mak=1)
            # package device/layer path
            _layer_path = join_path(_device_path, Constant.FILE_PATH_LAYER, mak=1)
            _mask_name_path = get_layer_path(_layer_path, _layer, mak=1)

            _fracture_path = join_path(_mask_name_path, Constant.FILE_PATH_FRACTURE, mak=1)

            # package device_path end

            # get boolean_index

            _boolean_index = self.get_device_boolean(tip_no, _device_name)
            # get source_db
            print(tip_no)
            print(_device_name)
            print(_boolean_index)
            _source_db1, _source_db2 = self.check_source_db(tip_no, _device_name, _boolean_index)

            # generate  fracture xor
            file_name, text = self.package_fracture_xor_file(_fracture_path, tip_no, mask_name, _boolean_index,
                                                           _source_db1, _device_name, _layer, _db_path)
            # generate  xor file start
            _fracture_xor_path = get_fracture_XOR_path(_fracture_path, mak=1)

            path = join_path(_fracture_xor_path, file_name)
            create_file(path, text)
            _list_file = _list_file + path + '<br>'
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

        LotTrailService().insert_trail(user_id=user_id, user_name=user_name, lot_id=_o.id, tip_no=tip_no, stage='Generate File',
                                       stage_desc=_list_file, remark='')

        data["success"] = True
        data["msg"] = "success"
        return data







    # package fracture vsb12i template content
    def package_fracture_file_content(self, lot_id,_fracture_path, tip_no, _device_name, mask_name, boolean_index,
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
                value = self.sheet_column_to_db_value(tip_no=tip_no, device_name=_device_name, mask_name=mask_name, boolean_index=boolean_index,
                                                      sheet_column=it.value,_db_path= _db_path, fracture_path= '',fracture_type= 1)
                template_text = template_text.replace(temp, str(value))
            if temp in file_name:
                value = self.sheet_column_to_db_value(tip_no=tip_no, device_name=_device_name, mask_name=mask_name, boolean_index= boolean_index,
                                                      sheet_column=it.value, _db_path=_db_path,fracture_path= '', fracture_type=1)

                file_name = file_name.replace(temp, str(value))
        template_text = template_text.encode('utf-8').decode('utf-8')
        file_name = file_name.encode('utf-8').decode('utf-8')
        return file_name, template_text

    #return:
    #code,msg,filename,template_text
    def get_fracture_template(self,lot_id,tip_no,device_name,boolean_index,mdt):
        # get source_db
        _source_db1, _source_db2 = self.check_source_db(tip_no, device_name, boolean_index)

        #query writer type by lot_id  from lot_info
        _lot_info = lot_info.objects.get(lot_id=lot_id)
        _machine = machine_basic.objects.get(id=_lot_info.machine_id)
        if _machine.machine_type == Constant.WRITER_TYPE_MODE5:
            if _source_db1 != '' and _source_db2 == '':
                # get template1
                _template_file_name, _template_text = self.get_mode5_db1_template_content()
            elif _source_db1 != '' and _source_db2 != '':
                # get template2
                _template_file_name, _template_text = self.get_mode5_db1_db2_template_content()
            else:
                # raise Exception('source db error!')
                return Constant.COMMON_METHOD_RETURN_FLAG_ERROR,Constant.FRACTURE_SOURCE_DB_ERROR,'',''
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
                return Constant.COMMON_METHOD_RETURN_FLAG_ERROR,Constant.FRACTURE_SOURCE_DB_ERROR,'',''
        else:
            return Constant.COMMON_METHOD_RETURN_FLAG_ERROR, Constant.FRACTURE_WRITER_ERROR, '', ''
        return Constant.COMMON_METHOD_RETURN_FLAG_SUCCESS,'',_template_file_name,_template_text

    # generate fracture xor file
    def package_fracture_xor_file(self, _fracture_path, tip_no, mask_name, boolean_index, source_db, _device_name, _layer,
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
                    value = self.sheet_column_to_db_value(tip_no=tip_no,device_name= _device_name,mask_name= mask_name, boolean_index=boolean_index,
                                                          sheet_column=it.value,_db_path= _db_path,fracture_path=  _fracture_path,fracture_type= 2)

                    text = text.replace(temp, str(value))
                if temp in file_name:
                    value = self.sheet_column_to_db_value(tip_no=tip_no,device_name=_device_name,mask_name=mask_name, boolean_index=boolean_index,
                                                          sheet_column=it.value,_db_path= _db_path,fracture_path= _fracture_path, fracture_type=2)

                    file_name = file_name.replace(temp, str(value))
            text = text.encode('utf-8').decode('utf-8')
            file_name = file_name.encode('utf-8').decode('utf-8')
            return file_name, text

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
        print('tip_no=%s,sheet_name=%s,column_name=%s,data_key=%s'%(tip_no,sheet_name,column_name,data_key))
        log.info('get_value_from_db_by_data_key():tip_no=%s,sheet_name=%s,column_name=%s,data_key=%s'%(tip_no,sheet_name,column_name,data_key))
        _o = import_data.objects.get(is_delete=0, tip_no=tip_no, sheet_name=sheet_name, column_name=column_name,
                                     data_key__contains=data_key)
        return _o.import_data

    # query list from db
    def get_list_from_db_by_data_key(self, tip_no, sheet_name, column_name, data_key):
        _list = import_data.objects.filter(is_delete=0, tip_no=tip_no, sheet_name=sheet_name, column_name=column_name,
                                           data_key__contains=data_key)
        return _list

    # query data from db
    def get_value_from_db(self, tip_no, sheet_name, column_name):
        _o = import_data.objects.get(is_delete=0, tip_no=tip_no, sheet_name=sheet_name, column_name=column_name)
        return _o.import_data

    # get total_bias
    def get_mask_tone(self, tip_no, mask_name):
        _list = import_data.objects.filter(is_delete=0, tip_no=tip_no,
                                           sheet_name=Constant.TOOLING_FORM_EXCEL_SHEET_BOOLEAN_INFO,
                                           column_name=Constant.TOOLING_FORM_EXCEL_SHEET_BOOLEAN_INFO_TONE,
                                           data_key__contains=mask_name)
        if _list.count() > 0:
            _o = _list[0]
            return _o.import_data
        return ''

    # get boolean by device
    def get_device_boolean(self, tip_no, device_name):
        _o_list = import_data.objects.filter(is_delete=0, tip_no=tip_no,
                                             sheet_name=Constant.TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO, \
                                             column_name=Constant.TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO_BOOLEAN_INDEX, \
                                             data_key__contains=device_name)
        if _o_list.count() > 0:
            return _o_list[0].import_data

    # get db
    def get_source_db(self, tip_no, device_name, boolean_index):
        _data_key = device_name + '_' + boolean_index
        _list_db = import_data.objects.filter(is_delete=0, tip_no=tip_no, \
                                              sheet_name=Constant.TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO, \
                                              column_name=Constant.TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO_SOURCE_DB, \
                                              data_key__contains=_data_key)
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
    def get_vsb12i_attr_content_from_mdt_table(self, tip_no, mask_name):
        # query layer_name from tooling form
        _tf_layer_name = self.get_value_from_db_by_data_key(tip_no, Constant.TOOLING_FORM_EXCEL_SHEET_TAPEOUT_INFO,
                                                            Constant.TOOLING_FORM_EXCEL_SHEET_TAPEOUT_INFO_LAYER_NAME,
                                                            mask_name)
        # query mdt from mdt_info by layer_name
        _o_mdt = mdt_info.objects.get(is_delete=0, layer_name=_tf_layer_name)
        # query mdt_cad_layer
        _list_cat_layer = mdt_cad_layer.objects.filter(is_delete=0, mdt_id=_o_mdt.id)
        _text = ''
        for layer in _list_cat_layer:
            _text = _text + 'layer ' + layer.cad_layer + ';' + layer.data_type + '\n'
            _text = _text + layer.writer_mdt + '\n'
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
    def validate_Fracture_mdt_table(self, lot_id, tip_no, mask_name):
        data = {}

        # tooling form Design rule
        _tf_design_rule = self.get_value_from_db(tip_no, Constant.TOOLING_FORM_EXCEL_SHEET_PRODUCT_INFO,
                                                 Constant.TOOLING_FORM_EXCEL_SHEET_PRODUCT_INFO_DESIGN_RULE)
        # tooling form layer name
        _tf_layer_name = self.get_value_from_db_by_data_key(tip_no, Constant.TOOLING_FORM_EXCEL_SHEET_TAPEOUT_INFO,
                                                            Constant.TOOLING_FORM_EXCEL_SHEET_TAPEOUT_INFO_LAYER_NAME,
                                                            mask_name)
        # tooling form tone
        _tf_mask_tone = self.get_mask_tone(tip_no, mask_name)
        # tooling form mask_grade
        _tf_mask_grade = self.get_value_from_db_by_data_key(tip_no, Constant.TOOLING_FORM_EXCEL_SHEET_TAPEOUT_INFO,
                                                            Constant.TOOLING_FORM_EXCEL_SHEET_TAPEOUT_INFO_GRADE,
                                                            mask_name)

        try:
            # mdt table design_rule
            _o_mdt = mdt_info.objects.get(is_delete=0, layer_name=_tf_layer_name, design_rule=_tf_design_rule,
                                          mask_tone=_tf_mask_tone, mask_grade=_tf_mask_grade)
        except:
            _o_mdt = None
            # raise Exception('layer name error in mdt table!')
            data["success"] = False
            data[
                "msg"] = "[" + _tf_design_rule + "," + _tf_layer_name + "," + _tf_mask_tone + "," + _tf_mask_grade + "]data not define in mdt table!"
            return data, ''

        _mdt_mask_tone = _o_mdt.mask_tone
        _mdt_mask_grade = _o_mdt.mask_grade
        _mdt = _o_mdt.mdt
        _mdt_total_bias = _o_mdt.tooling_bias

        if _mdt_mask_tone == 'D' and _mdt_total_bias < 0:
            data["success"] = False
            data["msg"] = Constant.FRACTURE_TOTAL_BIAS_ERROR_IN_MDT_TABLE
            return data, _mdt
        elif _mdt_mask_tone == 'C' and _mdt_total_bias > 0:
            data["success"] = False
            data["msg"] = Constant.FRACTURE_TOTAL_BIAS_ERROR_IN_MDT_TABLE
            return data, _mdt

        # validate cad layer between mdt table and tooling form
        if _mdt == 'Y':
            # query operation from tooling form
            _list_operation = self.get_list_from_db_by_data_key(tip_no, Constant.TOOLING_FORM_EXCEL_SHEET_BOOLEAN_INFO,
                                                                Constant.TOOLING_FORM_EXCEL_SHEET_BOOLEAN_INFO_OPERATION,
                                                                mask_name)
            _operation_str = ''
            for operation in _list_operation:
                _operation_str = _operation_str + operation.import_data
            _list_operation = re.findall(r'\d+;\d+', _operation_str)

            _list_cat_layer = mdt_cad_layer.objects.filter(is_delete=0, mdt_id=_o_mdt.id)
            for cat_layer in _list_cat_layer:
                _layer = cat_layer.cad_layer + ';' + cat_layer.data_type
                if _layer not in _list_operation:
                    data["success"] = False
                    data["msg"] = Constant.FRACTURE_CAD_LAYER_NOT_DEFINE_IN_TOOLING_FORM.format(_layer)
                    return data, _mdt

        return data, _mdt
