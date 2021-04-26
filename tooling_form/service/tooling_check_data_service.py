from django.db.models import Q

from jdv.models import lot_info
from system.websocket_view import send_msg
from tooling_form.models import tapeout_info_temp, tapeout_info, ccd_table_temp, ccd_table, boolean_info_temp, \
    boolean_info, \
    layout_info_temp, layout_info, mlm_info_temp, mlm_info, device_info_temp, device_info, import_check_list, \
    product_info, import_list
from utilslibrary.base.base import BaseService
from utilslibrary.system_constant import Constant
from utilslibrary.utils.date_utils import getDateStr, getMilliSecond


class tooling_check_data_service(BaseService):

    def check_data_main(self, tip_no, import_id, u_id):

        print("上传的tip_no为：" + tip_no)
        send_msg(u_id, {'is_tooling_msg': True, 'msg': 'Start Check'})
        # 临时表内容
        tapeout_temp_list = tapeout_info_temp.objects.filter(tip_no=tip_no)

        check_flag = True

        # 用来判断文件是否有改动
        change_flag = False

        for tapeout_temp_item in tapeout_temp_list:

            # 判断 mask_name ===================================================================================== start
            send_msg(u_id, {'is_tooling_msg': True, 'msg': 'Start Check Mask:' + tapeout_temp_item.mask_name})
            product_info_list = product_info.objects.filter(is_delete='0', tip_no=tip_no)
            product_name = product_info_list[0].product

            tapeout_info_item = tapeout_info.objects.filter(tip_no=tip_no, mask_name=tapeout_temp_item.mask_name)

            if tapeout_info_item.__len__() == 0:

                # 列表无值  走新增mask流程
                self.add_new_tapeout(tip_no, tapeout_temp_item.mask_name, u_id)
                change_flag = True
                continue
                pass
            send_msg(u_id, {'is_tooling_msg': True, 'msg': 'End Check Mask'})
            # 判断 mask_name ===================================================================================== end

            # 列表有值  走更新检核流程

            # 是否锁定 =========================================================================================== start
            send_msg(u_id, {'is_tooling_msg': True, 'msg': 'Start Check Lot Status'})
            lot_list = lot_info.objects.filter(mask_name=tapeout_temp_item.mask_name, tip_no=tip_no,
                                               writer_op_status='3', is_delete=0)

            if lot_list:
                # 如果有值 表示 这个 mask 已经被锁定 不做处理
                continue
            send_msg(u_id, {'is_tooling_msg': True, 'msg': 'End Check Lot Status'})
            # 是否锁定 =========================================================================================== end
            # 只要是走到这一步 肯定会生成check_list 所以会有check不通过
            check_flag = False

            # 判断Tapeout_Info 的T_O 是否为 Y ==================================================================== start
            send_msg(u_id, {'is_tooling_msg': True, 'msg': 'Start Check T_O'})
            if tapeout_temp_item.t_o == 'N':
                # T_O 为N 跳过
                add_import_check_list = import_check_list(tip_no=tip_no,
                                                          import_id=import_id,
                                                          product_name=product_name,
                                                          mask_name=tapeout_temp_item.mask_name,
                                                          check_code='CHECK_TIP_001',
                                                          description='Mask_Name 在 Tapeout_Info 的 T_O 为 N',
                                                          sheet_name='',
                                                          create_by=u_id,
                                                          create_date=getDateStr(),
                                                          create_time=getMilliSecond())

                add_import_check_list.save()


                continue
            send_msg(u_id, {'is_tooling_msg': True, 'msg': 'End Check T_O'})
            # 判断Tapeout_Info 的T_O 是否为 Y ==================================================================== end

            # 判断数据是否一致 和 是否为改变影响Convert结果的因素 ================================================ start
            send_msg(u_id, {'is_tooling_msg': True, 'msg': 'Start Check Data And Convert'})
            self.check_data_consistency(tip_no, import_id, product_name, tapeout_temp_item.mask_name, u_id, change_flag)
            send_msg(u_id, {'is_tooling_msg': True, 'msg': 'End Check Data And Convert'})
            # 判断数据是否一致 和 是否为改变影响Convert结果的因素 ================================================ end

        # if not check_flag:
        #     import_list.objects.filter(id=import_id).update(check_status='1')
        return check_flag, change_flag

    # 新增mask
    def add_new_tapeout(self, tip_no, mask_name, u_id):

        # 新增tapeout ===================================================================================== start
        tapeout_info_list = tapeout_info_temp.objects.filter(tip_no=tip_no, mask_name=mask_name, is_delete='0')
        ii = 0
        t_list = []
        for tapeout_info_item in tapeout_info_list:
            ii = ii + 1
            t = tapeout_info()
            t.tip_no = tip_no
            t.t_o = tapeout_info_item.t_o
            t.layer_name = tapeout_info_item.layer_name
            t.version = tapeout_info_item.version
            t.mask_name = tapeout_info_item.mask_name
            t.grade = tapeout_info_item.grade
            t.mask_mag = tapeout_info_item.mask_mag
            t.mask_type = tapeout_info_item.mask_type
            t.alignment = tapeout_info_item.alignment
            t.pellicle = tapeout_info_item.pellicle
            t.light_sourse = tapeout_info_item.light_sourse
            t.rotation = tapeout_info_item.rotation
            t.barcode = tapeout_info_item.barcode
            t.inspection = tapeout_info_item.inspection
            t.import_id = tapeout_info_item.import_id
            t.create_by = u_id
            t.create_date = getDateStr()
            t.create_time = getMilliSecond()
            t.no = ii
            t_list.append(t)
        tapeout_info.objects.bulk_create(t_list)
        # 新增tapeout ===================================================================================== end

        # 新增ccd_table ===================================================================================== start
        ccd_table_list = ccd_table_temp.objects.filter(tip_no=tip_no, mask_name=mask_name, is_delete='0')
        c_list = []
        for ccd_table_item in ccd_table_list:
            c = ccd_table()
            c.tip_no = tip_no
            c.no = ccd_table_item.no
            c.type = ccd_table_item.type
            c.coor_x = ccd_table_item.coor_x
            c.coor_y = ccd_table_item.coor_y
            c.item = ccd_table_item.item
            c.tone = ccd_table_item.tone
            c.direction = ccd_table_item.direction
            c.cd_4x_nm = ccd_table_item.cd_4x_nm
            c.mask_name = ccd_table_item.mask_name
            c.create_by = u_id
            c.create_date = getDateStr()
            c.create_time = getMilliSecond()
            c_list.append(c)
        ccd_table.objects.bulk_create(c_list)
        # 新增ccd_table ===================================================================================== end

        # 新增Boolean_Info ===================================================================================== start
        boolean_info_list = boolean_info_temp.objects.filter(tip_no=tip_no, mask_name=mask_name, is_delete='0')
        b_list = []
        for boolean_info_item in boolean_info_list:
            b = boolean_info()
            b.tip_no = tip_no
            b.boolean_index = boolean_info_item.boolean_index
            b.source_db = boolean_info_item.source_db
            b.mask_name = boolean_info_item.mask_name
            b.grid = boolean_info_item.grid
            b.operation = boolean_info_item.operation
            b.total_bias = boolean_info_item.total_bias
            b.tone = boolean_info_item.tone
            b.create_by = u_id
            b.create_date = getDateStr()
            b.create_time = getMilliSecond()
            b_list.append(b)

            # other_mask_booling = device_info_temp.objects.filter(~Q(mask_name=mask_name), tip_no=tip_no,
            #                                                      boolean_index=boolean_info_item.boolean_index,
            #                                                      source_db=boolean_info_item.source_db, is_delete='0')
            #
            # 新增Device_Info ===================================================================================== start
            # if other_mask_booling.__len__() == 0:
            device_info_list = device_info_temp.objects.filter(tip_no=tip_no,
                                                               boolean_index=boolean_info_item.boolean_index,
                                                               source_db=boolean_info_item.source_db, is_delete='0')
            d_list = []
            for device_info_item in device_info_list:
                d = device_info()
                d.tip_no = tip_no
                d.mask_name = mask_name
                d.psm = device_info_item.psm
                d.source_db = device_info_item.source_db
                d.device_type = device_info_item.device_type
                d.device_name = device_info_item.device_name
                d.boolean_index = device_info_item.boolean_index
                d.bias_sequence = device_info_item.bias_sequence
                d.rotate = device_info_item.rotate
                d.file_name = device_info_item.file_name
                d.top_structure = device_info_item.top_structure
                d.source_mag = device_info_item.source_mag
                d.shrink = device_info_item.shrink
                d.lb_x = device_info_item.lb_x
                d.lb_y = device_info_item.lb_y
                d.rt_x = device_info_item.rt_x
                d.rt_y = device_info_item.rt_y
                d.check_method = device_info_item.check_method
                d.value = device_info_item.value
                d.file_size = device_info_item.file_size
                d.create_by = u_id
                d.create_date = getDateStr()
                d.create_time = getMilliSecond()
                d_list.append(d)
            device_info.objects.bulk_create(d_list)
            # 新增Device_Info ===================================================================================== end
        boolean_info.objects.bulk_create(b_list)
        # 新增Boolean_Info ===================================================================================== end

        # 新增Layout_Info ===================================================================================== start
        layout_info_list = layout_info_temp.objects.filter(tip_no=tip_no, mask_name=mask_name, is_delete='0')
        l_list = []
        for layout_info_item in layout_info_list:
            l = layout_info()
            l.tip_no = tip_no
            l.psm = layout_info_item.psm
            l.device_name = layout_info_item.device_name
            l.mask_mag = layout_info_item.mask_mag
            l.source_mag = layout_info_item.source_mag
            l.original = layout_info_item.original
            l.x1 = layout_info_item.x1
            l.y1 = layout_info_item.y1
            l.pitch_x = layout_info_item.pitch_x
            l.pitch_y = layout_info_item.pitch_y
            l.array_x = layout_info_item.array_x
            l.array_y = layout_info_item.array_y
            l.mask_name = layout_info_item.mask_name
            l.create_by = u_id
            l.create_date = getDateStr()
            l.create_time = getMilliSecond()
            l_list.append(l)
        layout_info.objects.bulk_create(l_list)
        # 新增Layout_Info ===================================================================================== end

        # 新增MLM_Info ===================================================================================== start
        mlm_info_list = mlm_info_temp.objects.filter(tip_no=tip_no, mask_name=mask_name, is_delete='0')
        m_list = []
        for mlm_info_item in mlm_info_list:
            m = mlm_info()
            m.tip_no = tip_no
            m.no = mlm_info_item.no
            m.mlm_mask_id = mlm_info_item.mlm_mask_id
            m.mask_name = mlm_info_item.mask_name
            m.field_name = mlm_info_item.field_name
            m.shift_x = mlm_info_item.shift_x
            m.shift_y = mlm_info_item.shift_y
            m.create_by = u_id
            m.create_date = getDateStr()
            m.create_time = getMilliSecond()
            m_list.append(m)
        mlm_info.objects.bulk_create(m_list)
        # 新增MLM_Info ===================================================================================== end

    # 检核数据一致性
    def check_data_consistency(self, tip_no, import_id, product_name, mask_name, u_id, change_flag):

        # 判断tapeout ============================================================== start
        tapeout_info_check_status = self.check_tapeout_info(tip_no, import_id, product_name, mask_name, u_id)
        # 判断tapeout ============================================================== end

        # 判断device ============================================================== start
        device_info_check_status = self.check_devie_info(tip_no, import_id, product_name, mask_name, u_id)
        # 判断device ============================================================== end

        # 判断CCD_Table ============================================================== start
        ccd_table_check_status = self.check_ccd_table(tip_no, import_id, product_name, mask_name, u_id)
        # 判断CCD_Table ============================================================== end

        # 判断Boolean_Info ============================================================== start
        boolean_info_check_status = self.check_boolean_info(tip_no, import_id, product_name, mask_name, u_id)
        # 判断Boolean_Info ============================================================== end

        # 判断Layout_Info ============================================================== start
        layout_info_check_status = self.check_layout_info(tip_no, import_id, product_name, mask_name, u_id)
        # 判断Layout_Info ============================================================== end

        # 判断MLM_Info ============================================================== start
        mlm_info_check_status = self.check_mlm_info(tip_no, import_id, product_name, mask_name, u_id)
        # 判断MLM_Info ============================================================== end

        status = tapeout_info_check_status + device_info_check_status + ccd_table_check_status + \
                 boolean_info_check_status + layout_info_check_status + mlm_info_check_status

        if status == 0:
            add_import_check_list = import_check_list(tip_no=tip_no,
                                                      import_id=import_id,
                                                      product_name=product_name,
                                                      mask_name=mask_name,
                                                      check_code='CHECK_TIP_002',
                                                      description='The data is completely consistent and not processed',
                                                      sheet_name='',
                                                      create_by=u_id,
                                                      create_date=getDateStr(),
                                                      create_time=getMilliSecond())

            add_import_check_list.save()
            # 将原有import_list状态复原
            # old_import_list_status = import_list.objects.filter(tip_no=tip_no,
            #                                                     is_delete=1).order_by("-id").first().status
            # import_list.objects.filter(tip_no=tip_no, is_delete=0).update(status=old_import_list_status)
        else:
            change_flag = True



    def check_tapeout_info(self, tip_no, import_id, product_name, mask_name, u_id):

        tapeout_info_temp_list = tapeout_info_temp.objects.filter(tip_no=tip_no, mask_name=mask_name, is_delete='0')
        tapeout_info_list = tapeout_info.objects.filter(tip_no=tip_no, mask_name=mask_name, is_delete='0')

        # 用于一致性检测
        tapeout_info_temp_str_list = []
        tapeout_info_str_list = []

        # 用于影响 Convert 检测
        convert_tapeout_info_temp_str_list = []
        convert_tapeout_info_str_list = []

        for tapeout_info_temp_item in tapeout_info_temp_list:
            tapeout_info_temp_str = tapeout_info_temp_item.t_o + tapeout_info_temp_item.layer_name + \
                                    tapeout_info_temp_item.version + tapeout_info_temp_item.mask_name + \
                                    tapeout_info_temp_item.grade + tapeout_info_temp_item.mask_mag + \
                                    tapeout_info_temp_item.mask_type + tapeout_info_temp_item.alignment + \
                                    tapeout_info_temp_item.pellicle + tapeout_info_temp_item.light_sourse + \
                                    tapeout_info_temp_item.rotation + tapeout_info_temp_item.barcode + \
                                    tapeout_info_temp_item.inspection

            convert_tapeout_info_temp_str = tapeout_info_temp_item.mask_mag + tapeout_info_temp_item.alignment + \
                                            tapeout_info_temp_item.rotation + tapeout_info_temp_item.barcode

            tapeout_info_temp_str_list.append(tapeout_info_temp_str)
            convert_tapeout_info_temp_str_list.append(convert_tapeout_info_temp_str)

        for tapeout_info_item in tapeout_info_list:
            tapeout_info_str = tapeout_info_item.t_o + tapeout_info_item.layer_name + \
                               tapeout_info_item.version + tapeout_info_item.mask_name + \
                               tapeout_info_item.grade + tapeout_info_item.mask_mag + \
                               tapeout_info_item.mask_type + tapeout_info_item.alignment + \
                               tapeout_info_item.pellicle + tapeout_info_item.light_sourse + \
                               tapeout_info_item.rotation + tapeout_info_item.barcode + \
                               tapeout_info_item.inspection

            convert_tapeout_info_str = tapeout_info_item.mask_mag + tapeout_info_item.alignment + \
                                       tapeout_info_item.rotation + tapeout_info_item.barcode

            tapeout_info_str_list.append(tapeout_info_str)
            convert_tapeout_info_str_list.append(convert_tapeout_info_str)

        tapeout_info_check_status = 0
        for i in range(0, tapeout_info_temp_str_list.__len__()):

            if tapeout_info_temp_str_list[i] not in tapeout_info_str_list:
                if tapeout_info_check_status < 1:
                    tapeout_info_check_status = 1

                if convert_tapeout_info_temp_str_list[i] not in convert_tapeout_info_str_list:
                    if tapeout_info_check_status < 2:
                        tapeout_info_check_status = 2

        if tapeout_info_check_status == 1:
            add_import_check_list = import_check_list(tip_no=tip_no,
                                                     import_id=import_id,
                                                     product_name=product_name,
                                                     mask_name=mask_name,
                                                     check_code='CHECK_TIP_003',
                                                     description='Data changes, Convert has no effect',
                                                     sheet_name=Constant.TOOLING_FORM_EXCEL_SHEET_TAPEOUT_INFO,
                                                     create_by=u_id,
                                                     create_date=getDateStr(),
                                                     create_time=getMilliSecond())

            add_import_check_list.save()

        if tapeout_info_check_status == 2:
            add_import_check_list = import_check_list(tip_no=tip_no,
                                                     import_id=import_id,
                                                     product_name=product_name,
                                                     mask_name=mask_name,
                                                     check_code='CHECK_TIP_004',
                                                     description='Data changes, Convert has an effect',
                                                     sheet_name=Constant.TOOLING_FORM_EXCEL_SHEET_TAPEOUT_INFO,
                                                     create_by=u_id,
                                                     create_date=getDateStr(),
                                                     create_time=getMilliSecond())
            add_import_check_list.save()

        return tapeout_info_check_status

    def check_devie_info(self, tip_no, import_id, product_name, mask_name, u_id):

        tapeout_info_temp_list = boolean_info_temp.objects.filter(tip_no=tip_no, mask_name=mask_name, is_delete='0')
        tapeout_info_list = boolean_info.objects.filter(tip_no=tip_no, mask_name=mask_name, is_delete='0')

        # 临时表mask中所有device
        q_temp = Q()
        q_temp.connector = 'and'
        q_temp.children.append(('is_delete', 0))  # 错误显示状态，0为需要显示，1为不显示
        q_temp.children.append(('tip_no', tip_no))
        q_temp.children.append(('create_by', u_id))


        q_temp_or = Q()
        q_temp_or.connector = 'or'
        for tapeout_info_temp_item in tapeout_info_temp_list:

            q_temp_item = Q()
            q_temp_item.connector = 'and'
            q_temp_item.children.append(('source_db', tapeout_info_temp_item.source_db))
            q_temp_item.children.append(('boolean_index', tapeout_info_temp_item.boolean_index))
            q_temp_or.children.append(q_temp_item)

        q_temp.children.append(q_temp_or)

        device_info_temp_list = device_info_temp.objects.filter(q_temp)

        # 正式表mask中所有device
        # q = Q()
        # q.connector = 'and'
        # q.children.append(('is_delete', 0))  # 错误显示状态，0为需要显示，1为不显示
        # q.children.append(('tip_no', tip_no))
        #
        # q_or = Q()
        # q_or.connector = 'or'
        # for tapeout_info_item in tapeout_info_list:
        #     q_item = Q()
        #     q_item.connector = 'and'
        #     q_item.children.append(('source_db', tapeout_info_item.source_db))
        #     q_item.children.append(('boolean_index', tapeout_info_item.boolean_index))
        #     q_or.children.append(q_item)
        #
        # q.children.append(q_or)

        device_info_list = device_info.objects.filter(tip_no=tip_no, mask_name=mask_name, is_delete='0')

        device_info_check_status = 0

        if device_info_temp_list.__len__() != device_info_list.__len__():
            device_info_check_status = 2
        else:
            # 用于一致性 和 Convert 检测
            device_info_temp_str_list = []
            device_info_str_list = []

            for device_info_temp_item in device_info_temp_list:
                device_info_temp_str = device_info_temp_item.psm + device_info_temp_item.source_db + \
                                       device_info_temp_item.device_type + device_info_temp_item.device_name + \
                                       device_info_temp_item.boolean_index + device_info_temp_item.bias_sequence + \
                                       device_info_temp_item.rotate + device_info_temp_item.file_name + \
                                       device_info_temp_item.top_structure + device_info_temp_item.source_mag + \
                                       device_info_temp_item.shrink + device_info_temp_item.lb_x + \
                                       device_info_temp_item.lb_y + device_info_temp_item.rt_x + \
                                       device_info_temp_item.rt_y + device_info_temp_item.check_method + \
                                       device_info_temp_item.value + str(device_info_temp_item.file_size)

                device_info_temp_str_list.append(device_info_temp_str)

            for device_info_item in device_info_list:
                device_info_str = device_info_item.psm + device_info_item.source_db + \
                                   device_info_item.device_type + device_info_item.device_name + \
                                   device_info_item.boolean_index + device_info_item.bias_sequence + \
                                   device_info_item.rotate + device_info_item.file_name + \
                                   device_info_item.top_structure + device_info_item.source_mag + \
                                   device_info_item.shrink + device_info_item.lb_x + \
                                   device_info_item.lb_y + device_info_item.rt_x + \
                                   device_info_item.rt_y + device_info_item.check_method + \
                                   device_info_item.value + str(device_info_item.file_size)

                device_info_str_list.append(device_info_str)

            for i in range(0, device_info_temp_str_list.__len__()):

                if device_info_temp_str_list[i] not in device_info_str_list:
                    if device_info_check_status < 2:
                        device_info_check_status = 2

        if device_info_check_status == 2:
            add_import_check_list = import_check_list(tip_no=tip_no,
                                                      import_id=import_id,
                                                      product_name=product_name,
                                                      mask_name=mask_name,
                                                      check_code='CHECK_TIP_004',
                                                      description='Data changes, Convert has an effect',
                                                      sheet_name=Constant.TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO,
                                                      create_by=u_id,
                                                      create_date=getDateStr(),
                                                      create_time=getMilliSecond())
            add_import_check_list.save()

        return device_info_check_status

    def check_ccd_table(self, tip_no, import_id, product_name, mask_name, u_id):

        ccd_table_temp_list = ccd_table_temp.objects.filter(tip_no=tip_no, mask_name=mask_name, is_delete='0')
        ccd_table_list = ccd_table.objects.filter(tip_no=tip_no, mask_name=mask_name, is_delete='0')

        ccd_table_check_status = 0

        if ccd_table_temp_list.__len__() != ccd_table_list.__len__():
            ccd_table_check_status = 1
        else:
            # 用于一致性 和 Convert 检测
            ccd_table_temp_str_list = []
            ccd_table_str_list = []

            for ccd_table_temp_item in ccd_table_temp_list:
                ccd_table_temp_str = ccd_table_temp_item.no + ccd_table_temp_item.type + \
                                     ccd_table_temp_item.coor_x + ccd_table_temp_item.coor_y + \
                                     ccd_table_temp_item.item + ccd_table_temp_item.tone + \
                                     ccd_table_temp_item.direction + ccd_table_temp_item.cd_4x_nm + \
                                     ccd_table_temp_item.mask_name

                ccd_table_temp_str_list.append(ccd_table_temp_str)

            for ccd_table_item in ccd_table_list:
                ccd_table_str = ccd_table_item.no + ccd_table_item.type + \
                                 ccd_table_item.coor_x + ccd_table_item.coor_y + \
                                 ccd_table_item.item + ccd_table_item.tone + \
                                 ccd_table_item.direction + ccd_table_item.cd_4x_nm + \
                                 ccd_table_item.mask_name

                ccd_table_str_list.append(ccd_table_str)

            for i in range(0, ccd_table_temp_str_list.__len__()):

                if ccd_table_temp_str_list[i] not in ccd_table_str_list:
                    if ccd_table_check_status < 1:
                        ccd_table_check_status = 1

        if ccd_table_check_status == 1:
            add_import_check_list = import_check_list(tip_no=tip_no,
                                                     import_id=import_id,
                                                     product_name=product_name,
                                                     mask_name=mask_name,
                                                     check_code='CHECK_TIP_003',
                                                     description='Data changes, Convert has no effect',
                                                     sheet_name=Constant.TOOLING_FORM_EXCEL_SHEET_CCD_TABLE,
                                                     create_by=u_id,
                                                     create_date=getDateStr(),
                                                     create_time=getMilliSecond())

            add_import_check_list.save()

        return ccd_table_check_status

    def check_boolean_info(self, tip_no, import_id, product_name, mask_name, u_id):

        boolean_info_temp_list = boolean_info_temp.objects.filter(tip_no=tip_no, mask_name=mask_name, is_delete='0')
        boolean_info_list = boolean_info.objects.filter(tip_no=tip_no, mask_name=mask_name, is_delete='0')

        boolean_info_check_status = 0

        if boolean_info_temp_list.__len__() != boolean_info_list.__len__():
            boolean_info_check_status = 2
        else:
            # 用于一致性 和 Convert 检测
            boolean_info_temp_str_list = []
            boolean_info_str_list = []

            for boolean_info_temp_item in boolean_info_temp_list:
                boolean_info_temp_str = boolean_info_temp_item.boolean_index + boolean_info_temp_item.source_db + \
                                        boolean_info_temp_item.mask_name + boolean_info_temp_item.grid + \
                                        boolean_info_temp_item.operation + boolean_info_temp_item.total_bias + \
                                        boolean_info_temp_item.tone

                boolean_info_temp_str_list.append(boolean_info_temp_str)

            for boolean_info_item in boolean_info_list:
                boolean_info_str = boolean_info_item.boolean_index + boolean_info_item.source_db + \
                                    boolean_info_item.mask_name + boolean_info_item.grid + \
                                    boolean_info_item.operation + boolean_info_item.total_bias + \
                                    boolean_info_item.tone

                boolean_info_str_list.append(boolean_info_str)

            for i in range(0, boolean_info_temp_str_list.__len__()):

                if boolean_info_temp_str_list[i] not in boolean_info_str_list:
                    if boolean_info_check_status < 2:
                        boolean_info_check_status = 2

        if boolean_info_check_status == 2:
            add_import_check_list = import_check_list(tip_no=tip_no,
                                                      import_id=import_id,
                                                      product_name=product_name,
                                                      mask_name=mask_name,
                                                      check_code='CHECK_TIP_004',
                                                      description='Data changes, Convert has an effect',
                                                      sheet_name=Constant.TOOLING_FORM_EXCEL_SHEET_BOOLEAN_INFO,
                                                      create_by=u_id,
                                                      create_date=getDateStr(),
                                                      create_time=getMilliSecond())

            add_import_check_list.save()

        return boolean_info_check_status

    def check_layout_info(self, tip_no, import_id, product_name, mask_name, u_id):

        layout_info_temp_list = layout_info_temp.objects.filter(tip_no=tip_no, mask_name=mask_name, is_delete='0')
        layout_info_list = layout_info.objects.filter(tip_no=tip_no, mask_name=mask_name, is_delete='0')

        layout_info_check_status = 0

        if layout_info_temp_list.__len__() != layout_info_list.__len__():
            layout_info_check_status = 2
        else:
            # 用于一致性 和 Convert 检测
            layout_info_temp_str_list = []
            layout_info_str_list = []

            for layout_info_temp_item in layout_info_temp_list:
                layout_info_temp_str = layout_info_temp_item.psm + layout_info_temp_item.device_name + \
                                        layout_info_temp_item.mask_mag + layout_info_temp_item.source_mag + \
                                        layout_info_temp_item.original + layout_info_temp_item.x1 + \
                                        layout_info_temp_item.y1 + layout_info_temp_item.pitch_x + \
                                        layout_info_temp_item.pitch_y + layout_info_temp_item.array_x + \
                                        layout_info_temp_item.array_y + layout_info_temp_item.mask_name

                layout_info_temp_str_list.append(layout_info_temp_str)

            for layout_info_item in layout_info_list:
                layout_info_str = layout_info_item.psm + layout_info_item.device_name + \
                                    layout_info_item.mask_mag + layout_info_item.source_mag + \
                                    layout_info_item.original + layout_info_item.x1 + \
                                    layout_info_item.y1 + layout_info_item.pitch_x + \
                                    layout_info_item.pitch_y + layout_info_item.array_x + \
                                    layout_info_item.array_y + layout_info_item.mask_name

                layout_info_str_list.append(layout_info_str)

            for i in range(0, layout_info_temp_str_list.__len__()):

                if layout_info_temp_str_list[i] not in layout_info_str_list:
                    if layout_info_check_status < 2:
                        layout_info_check_status = 2

        if layout_info_check_status == 2:
            add_import_check_list = import_check_list(tip_no=tip_no,
                                                      import_id=import_id,
                                                      product_name=product_name,
                                                      mask_name=mask_name,
                                                      check_code='CHECK_TIP_004',
                                                      description='Data changes, Convert has an effect',
                                                      sheet_name=Constant.TOOLING_FORM_EXCEL_SHEET_LAYOUT_INFO,
                                                      create_by=u_id,
                                                      create_date=getDateStr(),
                                                      create_time=getMilliSecond())

            add_import_check_list.save()

        return layout_info_check_status

    def check_mlm_info(self, tip_no, import_id, product_name, mask_name, u_id):

        mlm_info_temp_list = mlm_info_temp.objects.filter(tip_no=tip_no, mask_name=mask_name, is_delete='0')
        mlm_info_list = mlm_info.objects.filter(tip_no=tip_no, mask_name=mask_name, is_delete='0')

        mlm_info_check_status = 0

        if mlm_info_temp_list.__len__() != mlm_info_list.__len__():
            mlm_info_check_status = 1
        else:
            # 用于一致性 和 Convert 检测
            mlm_info_temp_str_list = []
            mlm_info_str_list = []

            for mlm_info_temp_item in mlm_info_temp_list:
                mlm_info_temp_str = mlm_info_temp_item.mlm_mask_id + mlm_info_temp_item.mask_name + \
                                     mlm_info_temp_item.field_name + mlm_info_temp_item.shift_x + \
                                     mlm_info_temp_item.shift_y

                mlm_info_temp_str_list.append(mlm_info_temp_str)

            for mlm_info_item in mlm_info_list:
                mlm_info_str = mlm_info_item.mlm_mask_id + mlm_info_item.mask_name + \
                                 mlm_info_item.field_name + mlm_info_item.shift_x + \
                                 mlm_info_item.shift_y

                mlm_info_str_list.append(mlm_info_str)

            for i in range(0, mlm_info_temp_str_list.__len__()):

                if mlm_info_temp_str_list[i] not in mlm_info_str_list:
                    if mlm_info_check_status < 1:
                        mlm_info_check_status = 1

        if mlm_info_check_status == 1:
            add_import_check_list = import_check_list(tip_no=tip_no,
                                                     import_id=import_id,
                                                     product_name=product_name,
                                                     mask_name=mask_name,
                                                     check_code='CHECK_TIP_003',
                                                     description='Data changes, Convert has no effect',
                                                     sheet_name=Constant.TOOLING_FORM_EXCEL_SHEET_MLM_INFO,
                                                     create_by=u_id,
                                                     create_date=getDateStr(),
                                                     create_time=getMilliSecond())

            add_import_check_list.save()

        return mlm_info_check_status
