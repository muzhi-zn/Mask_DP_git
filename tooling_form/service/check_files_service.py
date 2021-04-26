# -*- coding: utf-8 -*-
import hashlib
import json
import re
import os
import traceback
import uuid

from django.http import JsonResponse

from system.websocket_view import send_msg, send_notice
from utilslibrary.system_constant import Constant
from utilslibrary.utils import iems_utils
from utilslibrary.utils.ssh_utils import SSHManager
from tooling_form.models import device_info, boolean_info, import_data_temp, import_list
from tooling_form.models import file_analysis_info
from utilslibrary.base.base import BaseService
from django.conf import settings
from django.contrib import messages
import logging
from django.db.models.query_utils import Q

log = logging.getLogger('log')


class CheckFileService(BaseService):

    def check_file(self, file_path, tip_no, file_name):
        try:
            """检查文件是否存在 ,md5是否匹配，file_size是否匹配"""
            # if False:
            #     pass
            if not self.check_exists(file_path, tip_no, file_name):
                return 0, " [file not exist]", "#FF0000"
            elif not self.check_file_size(tip_no, file_name):
                return 0, " [file_size not match]", "#FF0000"
            elif not self.check_value(tip_no, file_name):
                return 0, " [value not match]", "#FF0000"
            else:
                if self.execute_calibrewb(file_path, tip_no, file_name):  # 执行分析命令
                    obj = file_analysis_info.objects.get(tip_no=tip_no, file_name=file_name, upload_status=1)
                    analysis_status = obj.analysis_status
                    if analysis_status == 1:  # 分析进行中，job还未取得结果
                        return 0, "[calibrewb in progress]", "#00FFFF"
                    elif analysis_status == 3:  # 分析完成，job取得结果
                        precision_flag, precision_msg = self.check_precision(tip_no, file_name)
                        if not precision_flag:
                            return 0, precision_msg, "#FF0000"
                        else:
                            topcell_flag, topcell_msg = self.check_topcell(tip_no, file_name)
                            if not topcell_flag:
                                return 0, topcell_msg, "#FF0000"
                            else:
                                layers_flag, layers_msg = self.check_layers(tip_no, file_name)
                                if not layers_flag:
                                    return 0, layers_msg, "#FF0000"
                                else:
                                    bbox_flag, bbox_msg = self.check_bbox(tip_no, file_name)
                                    if not bbox_flag:
                                        return 0, bbox_msg, "#FF0000"
                                    else:
                                        if obj.analysis_check_status != 1:
                                            obj.analysis_check_status = 1
                                            obj.save()
                                        return 1, "[success]", "#00C957"  # 绿色
                    else:
                        return 0, "[calibrewb fail]", "#FF0000"
                else:
                    return 0, "[calibrewb fail]", "#FF0000"
        except Exception as e:
            log.error("check_file出现错误:" + str(e))
            traceback.print_exc()
            return 0, "[calibrewb fail]", "#FF0000"


    def check_exists(self, file_path, tip_no, file_name):
        """校验文件是否存在"""
        if not os.path.exists(file_path):
            return False
        else:
            fai = file_analysis_info.objects.filter(tip_no=tip_no, file_name=file_name, upload_status=1)
            if fai:
                return True
            else:
                obj = file_analysis_info.objects.create(tip_no=tip_no, file_name=file_name, upload_status=1)  # 保存文件信息
                md5, sha512 = get_file_md5(file_path)
                obj.file_md5 = md5
                obj.file_sha512 = sha512
                obj.file_size = os.path.getsize(file_path)
                uid = str(uuid.uuid4())
                suid = ''.join(uid.split('-'))
                obj.result_file_name = suid + '.txt'
                obj.save()
                return True
        # fai = file_analysis_info.objects.filter(tip_no=tip_no, file_name=file_name, upload_status=1)
        # if not fai:
        #     return False
        # else:
        #     if not os.path.exists(file_path):
        #         return False
        # return True

    def check_value(self, tip_no, file_name):
        """检查文件MD5是否一致"""
        excel_value = device_info.objects.filter(tip_no=tip_no, file_name=file_name, is_delete=0).first()
        actual_value = file_analysis_info.objects.get(tip_no=tip_no, file_name=file_name, upload_status=1)
        if excel_value and actual_value:
            check_type = excel_value.check_method
            if check_type == 'md5sum':
                if excel_value.value == actual_value.file_md5:
                    if actual_value.md5_check_status != 1:
                        actual_value.md5_check_status = 1
                        actual_value.save()
                    return True
                else:
                    if actual_value.md5_check_status != 2:
                        actual_value.md5_check_status = 2
                        actual_value.save()
                    return False
            elif check_type == 'sha-512':
                if excel_value.value == actual_value.file_sha512:
                    if actual_value.sha512_check_status != 1:
                        actual_value.sha512_check_status = 1
                        actual_value.save()
                    return True
                else:
                    if actual_value.sha512_check_status != 2:
                        actual_value.sha512_check_status = 2
                        actual_value.save()
                    return False
        else:
            log.error("check_md5方法下%s中%s文件读取数据库信息为空" % (tip_no, file_name))
            return False

    def check_file_size(self, tip_no, file_name):
        """检查文件大小是否一致"""
        excel_file_size = device_info.objects.filter(tip_no=tip_no, file_name=file_name, is_delete=0).first()
        actual_file_size = file_analysis_info.objects.get(tip_no=tip_no, file_name=file_name, upload_status=1)
        if excel_file_size and actual_file_size:
            try:
                if int(excel_file_size.file_size) == actual_file_size.file_size:
                    if actual_file_size.size_check_status != 1:
                        actual_file_size.size_check_status = 1
                        actual_file_size.save()
                    return True
                else:
                    if actual_file_size.size_check_status != 2:
                        actual_file_size.size_check_status = 2
                        actual_file_size.save()
                    return False
            except ValueError:
                log.error("file_size数据无法转为int类型")
                return False
        else:
            log.error("check_file_size方法下%s中%s文件读取数据库信息为空" % (tip_no, file_name))
            return False

    def check_precision(self, tip_no, file_name):
        """检查precision"""
        flag = True
        msg = ''
        device_info_obj = device_info.objects.values('source_db', 'boolean_index').filter(tip_no=tip_no,
                                                                                          file_name=file_name,
                                                                                          is_delete=0).first()
        if device_info_obj:
            excel_precision_list = boolean_info.objects.values('grid').filter(~Q(grid=''), tip_no=tip_no,
                                                                              boolean_index=device_info_obj[
                                                                                  'boolean_index'],
                                                                              source_db=device_info_obj['source_db'],
                                                                              is_delete=0)
            actual_precision = file_analysis_info.objects.get(tip_no=tip_no, file_name=file_name, upload_status=1)
            for excel_precision in excel_precision_list:
                if excel_precision and actual_precision:
                    excel_grid = float(excel_precision['grid'])
                    actual_grid = 1 / float(actual_precision.precision)
                    if excel_grid == actual_grid:
                        if actual_precision.precision_check_status != 1:
                            actual_precision.precision_check_status = 1
                            actual_precision.save()
                    else:
                        flag = False
                        if actual_precision.precision_check_status != 2:
                            actual_precision.precision_check_status = 2
                            actual_precision.save()
                        msg = '[grid not match,calculated value is 1/precision = %s]' % actual_grid
                else:
                    log.error("check_precision方法下%s中%s文件读取数据库信息为空" % (tip_no, file_name))
                    msg = '[check precision error]'
        else:
            log.error("device_info表中不存在tip_no=%s,file_name=%s的相关信息" % (tip_no, file_name))
            msg = '[check precision error]'
        return flag, msg

    def check_topcell(self, tip_no, file_name):
        """检查topcell"""
        flag = False
        msg = ''
        excel_topcell = device_info.objects.filter(tip_no=tip_no, file_name=file_name, is_delete=0).first()
        actual_topcell = file_analysis_info.objects.get(tip_no=tip_no, file_name=file_name, analysis_status=3)
        if excel_topcell and actual_topcell:
            if excel_topcell.top_structure == actual_topcell.topcell:
                if actual_topcell.topcell_check_status != 1:
                    actual_topcell.topcell_check_status = 1
                    actual_topcell.save()
                flag = True
            else:
                if actual_topcell.topcell_check_status != 2:
                    actual_topcell.topcell_check_status = 2
                    actual_topcell.save()
                msg = '[topcell not match, calculated value is %s]' % actual_topcell.topcell
        else:
            log.error("check_topcell方法下%s中%s文件读取数据库信息为空" % (tip_no, file_name))
            msg = '[check topcell error]'
        return flag, msg

    def check_layers(self, tip_no, file_name):
        """检查layers是否符合要求
            layer在excel中的公式有可能包括[DB2]、[DB3]等，如(([DB2]L51;0+[DB3]L51;2)+L51;3)
                            需要保证DB2后的L51;0存在于DB2文件运行结果内，保证DB3后的L51;2存在与DB3文件的运行结果内，其余的都要在当前DB的运算结果内
        """
        flag = True
        msg = ''
        device_info_obj = device_info.objects.values('source_db', 'boolean_index', 'mask_name').filter(tip_no=tip_no,
                                                                                                       file_name=file_name,
                                                                                                       is_delete=0).first()
        if device_info:
            excel_layers_list = boolean_info.objects.values('operation').filter(~Q(operation=''), tip_no=tip_no,
                                                                                boolean_index=device_info_obj[
                                                                                    'boolean_index'],
                                                                                source_db=device_info_obj[
                                                                                    'source_db'], is_delete=0,
                                                                                mask_name=device_info_obj['mask_name'])
            actual_layers = file_analysis_info.objects.get(tip_no=tip_no, file_name=file_name, analysis_status=3)
            for excel_layers in excel_layers_list:
                if excel_layers and actual_layers:
                    e_layers = excel_layers['operation']
                    e_layers_list = re.findall(r'\d+;\d+', e_layers)
                    a_layers = actual_layers.layers
                    a_layers_list = a_layers.split(',')
                    for e in e_layers_list:
                        db_list = re.findall(r'\[(\w+)?\]\w' + e, e_layers)  # 匹配DB信息
                        if db_list:
                            for db in db_list:
                                db_device_info = device_info.objects.filter(tip_no=tip_no,
                                                                            boolean_index=device_info.boolean_index,
                                                                            source_db=db, is_delete=0)
                                if db_device_info:
                                    db_fai_list = file_analysis_info.objects.get(tip_no=tip_no,
                                                                                 file_name=db_device_info[0].file_name,
                                                                                 analysis_status=3)
                                    if db_fai_list:
                                        db_layers_list = db_fai_list[0].layers.spilt(',')
                                        if e not in db_layers_list:
                                            flag = False
                                            msg = '[layers [%s]%s is out-of-band]' % (db, e)
                                    else:
                                        flag = False
                                        msg = '[layers [%s]%s is out-of-band]' % (db, e)
                                else:
                                    flag = False
                                    msg = '[layers %s is non-existent]' % db
                        else:
                            if e not in a_layers_list:
                                flag = False
                                msg = '[layers %s is out-of-band]' % e
                else:
                    flag = False
                    msg = '[check layers fail]'
            if flag:
                if actual_layers.layers_check_status != 1:
                    actual_layers.layers_check_status = 1
                    actual_layers.save()
            else:
                if actual_layers.layers_check_status != 2:
                    actual_layers.layers_check_status = 2
                    actual_layers.save()
        return flag, msg

    def check_bbox(self, tip_no, file_name):
        """检查bbox是否符合要求"""
        flag = True
        errors = ''
        values = ''
        excel_bbox = device_info.objects.filter(tip_no=tip_no, file_name=file_name, is_delete=0).first()
        actual_bbox = file_analysis_info.objects.get(tip_no=tip_no, file_name=file_name, analysis_status=3)
        if excel_bbox and actual_bbox:
            bbox_str = re.findall(r' {(.+)}', actual_bbox.bbox)[0]
            precision = float(actual_bbox.precision)
            if bbox_str:
                # {Leo {438400 -394400 692824000 918136000}}
                num_list = re.findall(r'-?\d+', bbox_str)
                if num_list:
                    lbx = excel_bbox.lb_x
                    lby = excel_bbox.lb_y
                    rtx = excel_bbox.rt_x
                    rty = excel_bbox.rt_y
                    A = float(num_list[0]) / precision
                    B = float(num_list[1]) / precision
                    C = float(num_list[2]) / precision
                    D = float(num_list[3]) / precision
                    if A < float(lbx):
                        flag = False
                        errors += 'LB(X)|'
                        values += str(A) + '|'
                    if B < float(lby):
                        flag = False
                        errors += 'LB(Y)|'
                        values += str(B) + '|'
                    if (A + C) > float(rtx):
                        flag = False
                        errors += 'RT(X)|'
                        values += str(A + C) + '|'
                    if (B + D) > float(rty):
                        flag = False
                        errors += 'RT(Y)'
                        values += str(B + D)
                else:
                    log.error("%s_%s在file_analysis_info表中对应的bbox无法解析出数字" % (tip_no, file_name))
                    flag = False
                    return flag, '[check bbox error]'
            else:
                log.error("%s_%s在file_analysis_info表中未找到对应的bbox" % (tip_no, file_name))
                flag = False
                return flag, '[check bbox error]'
        else:
            log.error("check_bbox方法下%s中%s文件读取数据库信息为空" % (tip_no, file_name))
            flag = False
            return flag, '[check bbox error]'
        if flag:
            if actual_bbox.bbox_check_status != 1:
                actual_bbox.bbox_check_status = 1
                actual_bbox.save()
        else:
            if actual_bbox.bbox_check_status != 2:
                actual_bbox.bbox_check_status = 2
                actual_bbox.save()
        return flag, '[%s not match, calculated value is %s]' % (errors, values)

    def execute_calibrewb(self, file_path, tip_no, file_name):
        """执行calibrewb命令"""
        obj = file_analysis_info.objects.get(tip_no=tip_no, file_name=file_name, upload_status=1)
        try:
            if obj.analysis_status == 0 or obj.analysis_status == 2:
                result_json = iems_utils.execute_cmd_wb('T00002', file_path)
                print(result_json)
                if result_json.get('code') == 200:
                    obj.analysis_status = 1
                    obj.analysis_message = result_json.get('message')
                    obj.iems_record_no = result_json.get('record_no')
                    obj.save()
                    return True
                else:
                    obj.analysis_status = 2
                    obj.analysis_message = result_json.get('message')
                    obj.save()
                    return False
            else:
                return True
        except Exception as e:
            log.error("execute_calibrewb方法下%s中%s文件执行calibrewb命令出现错误" % (tip_no, file_name))
            log.error(e)
            print(str(e))
            obj.analysis_status = 2
            obj.save()
            return False


def calibrewb_callback(request):
    """calibrewb回调方法"""
    param = request.body.decode('utf-8')
    param_json = json.loads(param)
    code = param_json.get('code')
    success = param_json.get('success')
    record_no = param_json.get('record_no')
    callback_result = param_json.get('result')
    fai = file_analysis_info.objects.filter(iems_record_no=record_no, analysis_status=1).first()
    u = import_list.objects.filter(tip_no=fai.tip_no, is_delete=0).first()
    if success:
        searchStr = re.search(r'precision (.*)', callback_result)
        if searchStr:
            result = searchStr.group(0)
            fai.result = result
            search_result = re.search(r'precision (.*) topcell (.*) layers (.*) bbox (.*)', result)
            if search_result:
                precision = search_result.group(1)
                fai.precision = precision
                topcell = search_result.group(2)
                fai.topcell = topcell
                l = ''
                layers = re.findall(r'\d+ \d+', search_result.group(3))
                for layer in layers:
                    l += layer.replace(' ', ';') + ','
                fai.layers = l
                bbox = search_result.group(4)
                fai.bbox = bbox
                fai.analysis_status = 3
                fai.save()
        send_notice(int(u.create_by), 'calibrewb done', notice_type=Constant.NOTICE_TYPE_SUCCESS)
        send_msg(int(u.create_by), {'is_callback': True})
    return JsonResponse({'success': True}, safe=False)


def get_file_md5(file_path):
    m = hashlib.md5()  # 创建md5对象
    sha512 = hashlib.sha512()
    with open(file_path, 'rb') as fobj:
        while True:
            data = fobj.read(40960)
            if not data:
                break
            m.update(data)  # 更新md5对象
            sha512.update(data)
    return m.hexdigest(), sha512.hexdigest()  # 返回md5对象
