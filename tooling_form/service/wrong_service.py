# coding:utf-8
from typing import List, Any

from django.db.models import Q
from django.forms import model_to_dict

from utilslibrary.base.base import BaseService
from utilslibrary.proxy.log_db_proxy import ProxyFactory,InvocationHandler

from django.http.response import JsonResponse
from django.template.context_processors import request
from django.db import transaction
from tooling_form.models import import_data_temp, import_error_list, product_info_temp, tapeout_info_temp, \
    device_info_temp, ccd_table_temp, boolean_info_temp, layout_info_temp, mlm_info_temp, product_info, tapeout_info, \
    device_info, ccd_table, boolean_info, layout_info, mlm_info, import_check_list, import_list

#@ProxyFactory(InvocationHandler)
from utilslibrary.utils.date_utils import getDateStr, getMilliSecond


class WrongService(BaseService):
    #update wrong data
    @transaction.atomic
    def updata_wrong_data(self,id,import_data_id,import_data_value):
        data={}
        data["success"] = "false"
        data["msg"] = "Failed"
        try:
            _o_import_data = import_data_temp.objects.get(id=import_data_id)
            _o_import_data.import_data = import_data_value
            flag = self.upd_import_data(_o_import_data)
            if flag==1:
                _o_import_error_message_log = import_error_list.objects.get(id=id)
                _o_import_error_message_log.is_delete = 1
                flag = self.upd_wrong_data(_o_import_error_message_log)
                if flag==1:
                    data["success"] = "true"
                    data["msg"] = "Success"
                else:
                    data["success"] = "false"
                    data["msg"] = "Failed"
            else:
                data["success"] = "false"
                data["msg"] = "Failed"
        except Exception as e:
            print(e)
            data["success"] = "false"
            data["msg"] = "Failed"
        return JsonResponse(data,safe = False)
    def upd_import_data(self,import_data):
        try:

            import_data.save()
            return 1
        except Exception as e:
            print(e)
            return 0
    def upd_wrong_data(self,import_error_message_log):

        try:
            import_error_message_log.save()
            return 1
        except Exception as e:
            print(e)
            return 0

    # 根据tip_no查询临时表资料，并将临时表资料新增到正式表中 并删除临时表资料
    @transaction.atomic
    def add_import_data_copy_temp(self, tip_no):

        # 1.product_info_temp
        _product_info_temp = product_info_temp.objects.filter(tip_no=tip_no, is_delete=0)

        if _product_info_temp:

            for loop in _product_info_temp:
                _o = product_info()

                _o.tip_no = loop.tip_no
                _o.customer = loop.customer
                _o.fab = loop.fab
                _o.product = loop.product
                _o.layout_type_application_type = loop.layout_type_application_type
                _o.mask_size = loop.mask_size
                _o.design_rule = loop.design_rule
                _o.mask_vendor = loop.mask_vendor
                _o.product_type = loop.product_type
                _o.d_h = loop.d_h
                _o.payment = loop.payment
                _o.tooling_version = loop.tooling_version
                _o.delivery_fab = loop.delivery_fab
                _o.order_type = loop.order_type
                _o.priority = loop.priority
                _o.security_type = loop.security_type
                _o.tech_process = loop.tech_process
                _o.cr_border_extend = loop.cr_border_extend
                _o.create_by = loop.create_by
                _o.create_date = getDateStr()
                _o.create_time = getMilliSecond()

                _o.save()

            _product_info_temp.update(is_delete=1)

        # 2.tapeout_info_temp
        _tapeout_info_temp = tapeout_info_temp.objects.filter(tip_no=tip_no, is_delete=0)

        mask_name_list: List[Any] = []

        if _tapeout_info_temp:

            for loop in _tapeout_info_temp:
                _o = tapeout_info()

                _o.tip_no = loop.tip_no
                _o.t_o = loop.t_o
                _o.layer_name = loop.layer_name
                _o.version = loop.version
                _o.mask_name = loop.mask_name
                _o.grade = loop.grade
                _o.mask_mag = loop.mask_mag
                _o.mask_type = loop.mask_type
                _o.alignment = loop.alignment
                _o.pellicle = loop.pellicle
                _o.light_sourse = loop.light_sourse
                _o.rotation = loop.rotation
                _o.barcode = loop.barcode
                _o.inspection = loop.inspection
                _o.create_by = loop.create_by
                _o.create_date = getDateStr()
                _o.create_time = getMilliSecond()

                _o.save()

                mask_name_list.append(loop.mask_name)

            _tapeout_info_temp.update(is_delete=1)

        # 3.device_info_temp
        '''
            特殊处理:
            1.根据tapeout_info_temp表中的mask_name,查询Boolean_Info表
            2.根据Boolean_Info表中的Boolean_Index、Source_DB,查询Device_Info表并去重
        '''
        if mask_name_list:

            for mask_name_loop in mask_name_list:

                results = boolean_info_temp.objects.filter(mask_name=mask_name_loop, is_delete=0)

                boolean_index_list: List[Any] = []
                source_db_list: List[Any] = []

                if results:

                    for loop in results:
                        boolean_index_list.append(loop.boolean_index)
                        source_db_list.append(loop.source_db)

                    _device_info_temp = device_info_temp.objects.filter(boolean_index__in=boolean_index_list,
                                                                        source_db__in=source_db_list,
                                                                        is_delete=0).distinct()

                    if _device_info_temp:

                        for loop_device_info in _device_info_temp:
                            _o = device_info()

                            _o.tip_no = loop_device_info.tip_no
                            _o.psm = loop_device_info.psm
                            _o.source_db = loop_device_info.source_db
                            _o.device_type = loop_device_info.device_type
                            _o.device_name = loop_device_info.device_name
                            _o.boolean_index = loop_device_info.boolean_index
                            _o.bias_sequence = loop_device_info.bias_sequence
                            _o.rotate = loop_device_info.rotate
                            _o.file_name = loop_device_info.file_name
                            _o.top_structure = loop_device_info.top_structure
                            _o.source_mag = loop_device_info.source_mag
                            _o.shrink = loop_device_info.shrink
                            _o.lb_x = loop_device_info.lb_x
                            _o.lb_y = loop_device_info.lb_y
                            _o.rt_x = loop_device_info.rt_x
                            _o.rt_y = loop_device_info.rt_y
                            _o.check_method = loop_device_info.check_method
                            _o.value = loop_device_info.value
                            _o.file_size = loop_device_info.file_size
                            _o.create_by = loop_device_info.create_by
                            _o.create_date = getDateStr()
                            _o.create_time = getMilliSecond()
                            _o.mask_name = mask_name_loop

                            _o.save()

                        _device_info_temp.update(is_delete=1)

        # 4.ccd_table_temp
        _ccd_table_temp = ccd_table_temp.objects.filter(tip_no=tip_no, is_delete=0)

        if _ccd_table_temp:

            for loop in _ccd_table_temp:
                _o = ccd_table()

                _o.no = loop.no
                _o.tip_no = loop.tip_no
                _o.mask_name = loop.mask_name
                _o.type = loop.type
                _o.coor_x = loop.coor_x
                _o.coor_y = loop.coor_y
                _o.item = loop.item
                _o.tone = loop.tone
                _o.direction = loop.direction
                _o.cd_4x_nm = loop.cd_4x_nm
                _o.create_by = loop.create_by
                _o.create_date = getDateStr()
                _o.create_time = getMilliSecond()

                _o.save()

            _ccd_table_temp.update(is_delete=1)

        # 5.boolean_info_temp
        _boolean_info_temp = boolean_info_temp.objects.filter(tip_no=tip_no, is_delete=0)

        if _boolean_info_temp:

            for loop in _boolean_info_temp:
                _o = boolean_info()

                _o.tip_no = loop.tip_no
                _o.boolean_index = loop.boolean_index
                _o.source_db = loop.source_db
                _o.mask_name = loop.mask_name
                _o.grid = loop.grid
                _o.operation = loop.operation
                _o.total_bias = loop.total_bias
                _o.tone = loop.tone
                _o.create_by = loop.create_by
                _o.create_date = getDateStr()
                _o.create_time = getMilliSecond()

                _o.save()

            _boolean_info_temp.update(is_delete=1)

        # 6.layout_info_temp
        _layout_info_temp = layout_info_temp.objects.filter(tip_no=tip_no, is_delete=0)

        if _layout_info_temp:

            for loop in _layout_info_temp:
                _o = layout_info()

                _o.tip_no = loop.tip_no
                _o.mask_name = loop.mask_name
                _o.psm = loop.psm
                _o.device_name = loop.device_name
                _o.mask_mag = loop.mask_mag
                _o.source_mag = loop.source_mag
                _o.original = loop.original
                _o.x1 = loop.x1
                _o.y1 = loop.y1
                _o.pitch_x = loop.pitch_x
                _o.pitch_y = loop.pitch_y
                _o.array_x = loop.array_x
                _o.array_y = loop.array_y
                _o.create_by = loop.create_by
                _o.create_date = getDateStr()
                _o.create_time = getMilliSecond()

                _o.save()

            _layout_info_temp.update(is_delete=1)

        # 7.mlm_info_temp
        _mlm_info_temp = mlm_info_temp.objects.filter(tip_no=tip_no, is_delete=0)

        if _mlm_info_temp:

            for loop in _mlm_info_temp:
                _o = mlm_info()

                _o.tip_no = loop.tip_no
                _o.mlm_mask_id = loop.mlm_mask_id
                _o.mask_name = loop.mask_name
                _o.field_name = loop.field_name
                _o.shift_x = loop.shift_x
                _o.shift_y = loop.shift_y
                _o.create_by = loop.create_by
                _o.create_date = getDateStr()
                _o.create_time = getMilliSecond()

                _o.save()

            _mlm_info_temp.update(is_delete=1)


    def check_list_delete(self, id, u_id):
        data = {}
        try:

            with transaction.atomic():
                import_check_list_item = import_check_list.objects.get(id=id)

                import_check_list.objects.filter(tip_no=import_check_list_item.tip_no,
                                                 mask_name=import_check_list_item.mask_name,
                                                 is_delete='0').update(is_delete='1', update_date=getDateStr(),
                                                                       update_time=getMilliSecond())

                # 查询该top_no在check_list中是否有未同步完成的数据
                import_one = import_check_list.objects.filter(~Q(sheet_name=""),
                                                              tip_no=import_check_list_item.tip_no,
                                                              is_delete=0,
                                                              status__in=[0, 2])

                # 如果都同步完成
                if not import_one:
                    # 将import_list中check_status改为0
                    import_list.objects.filter(tip_no=import_check_list_item.tip_no, is_delete=0) \
                        .update(check_status=0, update_date=getDateStr(), update_time=getMilliSecond(), update_by=u_id)
            data["success"] = True
            data["msg"] = "delete success"
            return JsonResponse(data, safe=False)
        except Exception as e:
            print(e)

            data["success"] = False
            data["msg"] = "delete failed"
            return JsonResponse(data, safe=False)
