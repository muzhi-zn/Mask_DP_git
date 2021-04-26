# _*_ coding: utf-8 _*_
import xlrd, pandas as pd
from tooling_form.models import product_info, tapeout_info, device_info, boolean_info, layout_info, mlm_info, ccd_table, \
    product_info_temp, tapeout_info_temp, device_info_temp, ccd_table_temp, boolean_info_temp, layout_info_temp, \
    mlm_info_temp
from tooling_form.service.tooling_service import str_strip
from utilslibrary.system_constant import Constant
from utilslibrary.utils.date_utils import getDateStr, getMilliSecond


class save_excel_data:

    def save_data(self, file_path, tip_no, u_id):
        # workbook = xlrd.open_workbook(file_path)
        # workbook = pd.read_excel()
        self.insert_device_info_temp(tip_no, 0, u_id, file_path)
        self.insert_product_info(tip_no, u_id, file_path)
        self.insert_tapeout_info(tip_no, u_id, file_path)
        self.insert_ccd_table(tip_no, u_id, file_path)
        self.insert_boolean_info(tip_no, u_id, file_path)
        self.insert_layout_info(tip_no, u_id, file_path)
        self.insert_mlm_info(tip_no, u_id, file_path)
        self.insert_device_info(tip_no, u_id, file_path)

    def save_data_temp(self, file_path, tip_no, import_id, u_id):
        # workbook = xlrd.open_workbook(file_path)
        # workbook = pd.read_excel(file_path)
        self.insert_product_info_temp(tip_no, import_id, u_id, file_path)
        self.insert_tapeout_info_temp(tip_no, import_id, u_id, file_path)
        self.insert_device_info_temp(tip_no, import_id, u_id, file_path)
        self.insert_ccd_table_temp(tip_no, import_id, u_id, file_path)
        self.insert_boolean_info_temp(tip_no, import_id, u_id, file_path)
        self.insert_layout_info_temp(tip_no, import_id, u_id, file_path)
        self.insert_mlm_info_temp(tip_no, import_id, u_id, file_path)

    def insert_product_info(self, tip_no, u_id, file_path):
        """批量插入产品信息"""
        p_list = product_info.objects.select_for_update().filter(tip_no=tip_no)
        if p_list:
            p_list.delete()

        workbook = pd.read_excel(file_path, sheet_name=Constant.TOOLING_FORM_EXCEL_SHEET_PRODUCT_INFO, keep_default_na=False)
        # sheet = workbook.sheet_by_name('Product_Info')
        # row_num = sheet.nrows
        product_info_list = list()
        for i in range(1, len(workbook)):
            p = product_info()
            p.customer = workbook.iloc[i, 0]
            p.fab = workbook.iloc[i, 1]
            p.product = workbook.iloc[i, 2]
            p.layout_type_application_type = workbook.iloc[i, 3]
            p.mask_size = workbook.iloc[i, 4]
            p.design_rule = workbook.iloc[i, 5]
            p.mask_vendor = workbook.iloc[i, 6]
            p.product_type = workbook.iloc[i, 7]
            p.d_h = workbook.iloc[i, 8]
            p.payment = workbook.iloc[i, 9]
            p.tooling_version = workbook.iloc[i, 10]
            p.delivery_fab = workbook.iloc[i, 11]
            p.order_type = workbook.iloc[i, 12]
            p.priority = workbook.iloc[i, 13]
            p.security_type = workbook.iloc[i, 14]
            p.tech_process = workbook.iloc[i, 15]
            p.cr_border_extend = workbook.iloc[i, 16]
            p.tip_no = tip_no
            p.create_by = u_id
            p.create_date = getDateStr()
            p.create_time = getMilliSecond()

            if p.customer == '' and p.fab == '' and p.product == '' and p.layout_type_application_type == '' \
                    and p.mask_size == '' and p.design_rule == '' and p.mask_vendor == '' and p.product_type == '' \
                    and p.d_h == '' and p.payment == '' and p.tooling_version == '' and p.delivery_fab != '' \
                    and p.order_type == '' and p.priority == '' and p.security_type == '' and p.tech_process == '' \
                    and p.cr_border_extend == '':
                continue
            else:
                product_info_list.append(p)
        product_info.objects.bulk_create(product_info_list)

    def insert_tapeout_info(self, tip_no, u_id, file_path):
        """批量插入tapeout信息"""
        t_list = tapeout_info.objects.select_for_update().filter(tip_no=tip_no)
        if t_list:
            t_list.delete()
        # sheet = workbook.sheet_by_name('Tapeout_Info')
        workbook = pd.read_excel(file_path, sheet_name=Constant.TOOLING_FORM_EXCEL_SHEET_TAPEOUT_INFO, keep_default_na=False)
        # row_num = sheet.nrows
        tapeout_info_list = list()
        ii = 0
        for i in range(2, len(workbook)):
            ii = ii + 1
            # row = sheet.row_values(i)
            t = tapeout_info()
            t.tip_no = tip_no
            t.t_o = workbook.iloc[i, 0]
            t.layer_name = str(int(workbook.iloc[i, 1])) if ".0" in str(workbook.iloc[i, 1]) else workbook.iloc[i, 1]
            t.version = workbook.iloc[i, 2]
            t.mask_name = workbook.iloc[i, 3]
            t.grade = workbook.iloc[i, 4]
            t.mask_mag = workbook.iloc[i, 5]
            t.mask_type = workbook.iloc[i, 6]
            t.alignment = workbook.iloc[i, 7]
            t.pellicle = workbook.iloc[i, 8]
            t.light_sourse = workbook.iloc[i, 9]
            t.rotation = workbook.iloc[i, 10]
            t.barcode = workbook.iloc[i, 11]
            t.inspection = workbook.iloc[i, 12]
            t.create_by = u_id
            t.create_date = getDateStr()
            t.create_time = getMilliSecond()
            t.no = ii

            if t.t_o == '' and t.layer_name == '' and t.version == '' and t.mask_name == '' and t.grade == '' \
                    and t.mask_mag == '' and t.mask_type == '' and t.alignment == '' and t.pellicle == '' \
                    and t.light_sourse == '' and t.rotation == '' and t.barcode == '' and t.inspection == '':

                continue
            else:
                tapeout_info_list.append(t)
        tapeout_info.objects.bulk_create(tapeout_info_list)

    def insert_device_info(self, tip_no, u_id, file_path):
        """批量插入device信息"""

        boolean_info_list = boolean_info.objects.filter(tip_no=tip_no, is_delete='0')

        device_info_list = list()

        for boolean_info_item in boolean_info_list:

            device_info_temp_list = device_info_temp.objects.filter(tip_no=tip_no,
                                                                    boolean_index=boolean_info_item.boolean_index,
                                                                    source_db=boolean_info_item.source_db,
                                                                    is_delete='0',
                                                                    create_by=u_id)

            for device_info_temp_item in device_info_temp_list:

                d = device_info()
                d.tip_no = device_info_temp_item.tip_no
                d.mask_name = boolean_info_item.mask_name
                d.psm = device_info_temp_item.psm
                d.source_db = device_info_temp_item.source_db
                d.device_type = device_info_temp_item.device_type
                d.device_name = device_info_temp_item.device_name
                d.boolean_index = device_info_temp_item.boolean_index
                d.bias_sequence = device_info_temp_item.bias_sequence
                d.rotate = device_info_temp_item.rotate
                d.file_name = device_info_temp_item.file_name
                d.top_structure = device_info_temp_item.top_structure
                d.source_mag = device_info_temp_item.source_mag
                d.shrink = device_info_temp_item.shrink
                d.lb_x = device_info_temp_item.lb_x
                d.lb_y = device_info_temp_item.lb_y
                d.rt_x = device_info_temp_item.rt_x
                d.rt_y = device_info_temp_item.rt_y
                d.check_method = device_info_temp_item.check_method
                d.value = device_info_temp_item.value
                d.file_size = device_info_temp_item.file_size
                d.create_by = u_id
                d.create_date = getDateStr()
                d.create_time = getMilliSecond()
                device_info_list.append(d)

        device_info.objects.bulk_create(device_info_list)

    def insert_ccd_table(self, tip_no, u_id, file_path):
        """批量插入CCD_table信息"""
        c_list = ccd_table.objects.filter(tip_no=tip_no).delete()
        # sheet = workbook.sheet_by_name('CCD_Table')
        workbook = pd.read_excel(file_path, sheet_name=Constant.TOOLING_FORM_EXCEL_SHEET_CCD_TABLE, keep_default_na=False)
        # row_num = sheet.nrows
        ccd_table_list = list()
        for i in range(1, len(workbook)):
            # row = sheet.row_values(i)
            c = ccd_table()
            c.tip_no = tip_no
            c.no = str_strip(workbook.iloc[i, 0])
            c.type = workbook.iloc[i, 1]
            c.coor_x = str_strip(workbook.iloc[i, 2])
            c.coor_y = str_strip(workbook.iloc[i, 3])
            c.item = workbook.iloc[i, 4]
            c.tone = workbook.iloc[i, 5]
            c.direction = workbook.iloc[i, 6]
            c.cd_4x_nm = workbook.iloc[i, 7]
            c.mask_name = workbook.iloc[i, 8]
            c.create_by = u_id
            c.create_date = getDateStr()
            c.create_time = getMilliSecond()

            if c.no == '' and c.type == '' and c.coor_x == '' and c.coor_y == '' and c.item == '' and c.tone == '' \
                    and c.direction == '' and c.cd_4x_nm == '' and c.mask_name == '':

                continue
            else:
                ccd_table_list.append(c)
        ccd_table.objects.bulk_create(ccd_table_list)

    def insert_boolean_info(self, tip_no, u_id, file_path):
        """批量插入boolean信息"""
        b_list = boolean_info.objects.select_for_update().filter(tip_no=tip_no)
        if b_list:
            b_list.delete()
        # sheet = workbook.sheet_by_name('Boolean_Info')
        workbook = pd.read_excel(file_path, sheet_name=Constant.TOOLING_FORM_EXCEL_SHEET_BOOLEAN_INFO, keep_default_na=False)
        # row_num = sheet.nrows
        boolean_info_list = list()
        for i in range(1, len(workbook)):
            # row = sheet.row_values(i)
            b = boolean_info()
            b.tip_no = tip_no
            b.boolean_index = workbook.iloc[i, 0]
            b.source_db = workbook.iloc[i, 1]
            b.mask_name = workbook.iloc[i, 2]
            b.grid = workbook.iloc[i, 3]
            b.operation = workbook.iloc[i, 4]
            b.total_bias = workbook.iloc[i, 5]
            b.tone = workbook.iloc[i, 6]
            b.create_by = u_id
            b.create_date = getDateStr()
            b.create_time = getMilliSecond()

            if b.boolean_index == '' and b.source_db == '' and b.mask_name == '' and b.grid == '' \
                    and b.operation == '' and b.total_bias == '' and b.tone == '':

                continue
            else:
                boolean_info_list.append(b)
        boolean_info.objects.bulk_create(boolean_info_list)

    def insert_layout_info(self, tip_no, u_id, file_path):
        """批量插入layout信息"""
        l_list = layout_info.objects.select_for_update().filter(tip_no=tip_no)
        if l_list:
            l_list.delete()
        # sheet = workbook.sheet_by_name('Layout_Info')
        workbook = pd.read_excel(file_path, sheet_name=Constant.TOOLING_FORM_EXCEL_SHEET_LAYOUT_INFO, keep_default_na=False)
        # row_num = sheet.nrows
        layout_info_list = list()
        for i in range(1, len(workbook)):
            # row = sheet.row_values(i)
            l = layout_info()
            l.tip_no = tip_no
            l.psm = workbook.iloc[i, 0]
            l.device_name = workbook.iloc[i, 1]
            l.mask_mag = workbook.iloc[i, 2]
            l.source_mag = workbook.iloc[i, 3]
            l.original = workbook.iloc[i, 4]
            l.x1 = workbook.iloc[i, 5]
            l.y1 = workbook.iloc[i, 6]
            l.pitch_x = str_strip(workbook.iloc[i, 7])
            l.pitch_y = str_strip(workbook.iloc[i, 8])
            l.array_x = str_strip(workbook.iloc[i, 9])
            l.array_y = str_strip(workbook.iloc[i, 10])
            l.mask_name = workbook.iloc[i, 11]
            l.create_by = u_id
            l.create_date = getDateStr()
            l.create_time = getMilliSecond()

            if l.psm == '' and l.device_name == '' and l.mask_mag == '' and l.source_mag == '' and l.original == '' and l.x1 == '' \
                    and l.y1 == '' and l.pitch_x == '' and l.pitch_y == '' and l.array_x == '' and l.array_y == '' \
                    and l.mask_name == '':
                continue
            else:
                layout_info_list.append(l)
        layout_info.objects.bulk_create(layout_info_list)

    def insert_mlm_info(self, tip_no, u_id, file_path):
        """批量插入mlm信息"""
        m_list = mlm_info.objects.select_for_update().filter(tip_no=tip_no)
        if m_list:
            m_list.delete()
        # sheet = workbook.sheet_by_name('MLR_Info')
        workbook = pd.read_excel(file_path, sheet_name=Constant.TOOLING_FORM_EXCEL_SHEET_MLM_INFO, keep_default_na=False)
        # sheet = workbook.sheet_by_name('MLM_Info')
        # row_num = sheet.nrows
        mlm_info_list = list()
        for i in range(1, len(workbook)):
            # row = sheet.row_values(i)
            m = mlm_info()
            m.tip_no = tip_no
            m.mlm_mask_id = workbook.iloc[i, 0]
            m.mask_name = workbook.iloc[i, 1]
            m.field_name = workbook.iloc[i, 2]
            m.shift_x = str_strip(workbook.iloc[i, 3])
            m.shift_y = str_strip(workbook.iloc[i, 4])
            m.create_by = u_id
            m.create_date = getDateStr()
            m.create_time = getMilliSecond()

            if m.mlm_mask_id == '' and m.mask_name == '' and m.field_name == '' and m.shift_x == '' and m.shift_y == '':
                continue
            else:
                mlm_info_list.append(m)
        mlm_info.objects.bulk_create(mlm_info_list)

    def insert_product_info_temp(self, tip_no, import_id, u_id, file_path):
        """批量插入产品信息"""
        p_list = product_info_temp.objects.select_for_update().filter(tip_no=tip_no)
        if p_list:
            p_list.delete()
        # sheet = workbook.sheet_by_name('Product_Info')
        workbook = pd.read_excel(file_path, sheet_name=Constant.TOOLING_FORM_EXCEL_SHEET_PRODUCT_INFO, keep_default_na=False)
        # row_num = sheet.nrows
        product_info_list = list()
        for i in range(1, len(workbook)):
            # row = sheet.row_values(i)
            p = product_info_temp()
            p.customer = workbook.iloc[i, 0]
            p.fab = workbook.iloc[i, 1]
            p.product = workbook.iloc[i, 2]
            p.layout_type_application_type = workbook.iloc[i, 3]
            p.mask_size = workbook.iloc[i, 4]
            p.design_rule = workbook.iloc[i, 5]
            p.mask_vendor = workbook.iloc[i, 6]
            p.product_type = workbook.iloc[i, 7]
            p.d_h = workbook.iloc[i, 8]
            p.payment = workbook.iloc[i, 9]
            p.tooling_version = workbook.iloc[i, 10]
            p.delivery_fab = workbook.iloc[i, 11]
            p.order_type = workbook.iloc[i, 12]
            p.priority = workbook.iloc[i, 13]
            p.security_type = workbook.iloc[i, 14]
            p.tech_process = workbook.iloc[i, 15]
            p.cr_border_extend = workbook.iloc[i, 16]
            p.tip_no = tip_no
            p.import_id = import_id
            p.create_by = u_id
            p.create_date = getDateStr()
            p.create_time = getMilliSecond()

            if p.customer == '' and p.fab == '' and p.product == '' and p.layout_type_application_type == '' \
                    and p.mask_size == '' and p.design_rule == '' and p.mask_vendor == '' and p.product_type == '' \
                    and p.d_h == '' and p.payment == '' and p.tooling_version == '' and p.delivery_fab != '' \
                    and p.order_type == '' and p.priority == '' and p.security_type == '' and p.tech_process == '' \
                    and p.cr_border_extend == '':
                continue
            else:
                product_info_list.append(p)
        product_info_temp.objects.bulk_create(product_info_list)

    def insert_tapeout_info_temp(self, tip_no, import_id, u_id, file_path):
        """批量插入tapeout信息"""
        t_list = tapeout_info_temp.objects.select_for_update().filter(tip_no=tip_no)
        if t_list:
            t_list.delete()
        # sheet = workbook.sheet_by_name('Tapeout_Info')
        workbook = pd.read_excel(file_path, sheet_name=Constant.TOOLING_FORM_EXCEL_SHEET_TAPEOUT_INFO, keep_default_na=False)
        # row_num = sheet.nrows
        tapeout_info_list = list()
        for i in range(2, len(workbook)):
            # row = sheet.row_values(i)
            t = tapeout_info_temp()
            t.tip_no = tip_no
            t.t_o = workbook.iloc[i, 0]
            t.layer_name = str(int(workbook.iloc[i, 1])) if ".0" in str(workbook.iloc[i, 1]) else workbook.iloc[i, 1]
            t.version = workbook.iloc[i, 2]
            t.mask_name = workbook.iloc[i, 3]
            t.grade = workbook.iloc[i, 4]
            t.mask_mag = workbook.iloc[i, 5]
            t.mask_type = workbook.iloc[i, 6]
            t.alignment = workbook.iloc[i, 7]
            t.pellicle = workbook.iloc[i, 8]
            t.light_sourse = workbook.iloc[i, 9]
            t.rotation = workbook.iloc[i, 10]
            t.barcode = workbook.iloc[i, 11]
            t.inspection = workbook.iloc[i, 12]
            t.import_id = import_id
            t.create_by = u_id
            t.create_date = getDateStr()
            t.create_time = getMilliSecond()

            if t.t_o == '' and t.layer_name == '' and t.version == '' and t.mask_name == '' and t.grade == '' \
                    and t.mask_mag == '' and t.mask_type == '' and t.alignment == '' and t.pellicle == '' \
                    and t.light_sourse == '' and t.rotation == '' and t.barcode == '' and t.inspection == '':

                continue
            else:
                tapeout_info_list.append(t)
        tapeout_info_temp.objects.bulk_create(tapeout_info_list)

    def insert_device_info_temp(self, tip_no, import_id, u_id, file_path):
        """批量插入device信息"""
        d_list = device_info_temp.objects.select_for_update().filter(tip_no=tip_no)
        if d_list:
            d_list.delete()
        # sheet = workbook.sheet_by_name('Device_Info')
        workbook = pd.read_excel(file_path, sheet_name=Constant.TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO, keep_default_na=False)
        # row_num = sheet.nrows
        device_info_list = list()
        for i in range(1, len(workbook)):
            # row = sheet.row_values(i)
            d = device_info_temp()
            d.tip_no = tip_no
            d.psm = workbook.iloc[i, 0].strip()
            d.source_db = workbook.iloc[i, 1].strip()
            d.device_type = workbook.iloc[i, 2].strip()
            d.device_name = workbook.iloc[i, 3].strip()
            d.boolean_index = workbook.iloc[i, 4].strip()
            d.bias_sequence = workbook.iloc[i, 5].strip()
            d.rotate = workbook.iloc[i, 6]
            d.file_name = workbook.iloc[i, 7].strip()
            d.top_structure = workbook.iloc[i, 8].strip() if not isinstance(workbook.iloc[i, 8], float) else str(int(workbook.iloc[i, 8]))
            d.source_mag = workbook.iloc[i, 9]
            d.shrink = workbook.iloc[i, 10]
            d.lb_x = workbook.iloc[i, 11]
            d.lb_y = workbook.iloc[i, 12]
            d.rt_x = workbook.iloc[i, 13]
            d.rt_y = workbook.iloc[i, 14]
            d.check_method = workbook.iloc[i, 15].strip()
            d.value = workbook.iloc[i, 16].strip()
            d.file_size = workbook.iloc[i, 17] if not workbook.iloc[i, 17] == '' else 0
            d.import_id = import_id
            d.create_by = u_id
            d.create_date = getDateStr()
            d.create_time = getMilliSecond()

            if d.psm == '' and d.source_db == '' and d.device_type == '' and d.device_name == '' and d.boolean_index == '' and d.bias_sequence == '' \
                    and d.rotate == '' and d.file_name == '' and d.top_structure == '' and d.source_mag == '' and d.shrink == '' and d.lb_x == '' \
                    and d.lb_y == '' and d.rt_x == '' and d.rt_y == '' and d.check_method == '' and d.value == '':
                continue
            else:
                device_info_list.append(d)
        device_info_temp.objects.bulk_create(device_info_list)

    def insert_ccd_table_temp(self, tip_no, import_id, u_id, file_path):
        """批量插入CCD_table信息"""
        c_list = ccd_table_temp.objects.filter(tip_no=tip_no).delete()
        # sheet = workbook.sheet_by_name('CCD_Table')
        workbook = pd.read_excel(file_path, sheet_name=Constant.TOOLING_FORM_EXCEL_SHEET_CCD_TABLE, keep_default_na=False)
        # row_num = sheet.nrows
        ccd_table_list = list()
        for i in range(1, len(workbook)):
            # row = sheet.row(i)
            c = ccd_table_temp()
            c.tip_no = tip_no
            c.no = str_strip(workbook.iloc[i, 0])
            c.type = workbook.iloc[i, 1]
            c.coor_x = str(round(float(str_strip(workbook.iloc[i, 2])), 1))
            c.coor_y = str(round(float(str_strip(workbook.iloc[i, 3])), 1))
            c.item = workbook.iloc[i, 4]
            c.tone = workbook.iloc[i, 5]
            c.direction = workbook.iloc[i, 6]
            c.cd_4x_nm = workbook.iloc[i, 7]
            c.mask_name = workbook.iloc[i, 8]
            c.import_id = import_id
            c.create_by = u_id
            c.create_date = getDateStr()
            c.create_time = getMilliSecond()

            if c.no == '' and c.type == '' and c.coor_x == '' and c.coor_y == '' and c.item == '' and c.tone == '' \
                    and c.direction == '' and c.cd_4x_nm == '' and c.mask_name == '':
                continue
            else:
                ccd_table_list.append(c)
        ccd_table_temp.objects.bulk_create(ccd_table_list)

    def insert_boolean_info_temp(self, tip_no, import_id, u_id, file_path):
        """批量插入boolean信息"""
        b_list = boolean_info_temp.objects.select_for_update().filter(tip_no=tip_no)
        if b_list:
            b_list.delete()
        # sheet = workbook.sheet_by_name('Boolean_Info')
        workbook = pd.read_excel(file_path, sheet_name=Constant.TOOLING_FORM_EXCEL_SHEET_BOOLEAN_INFO, keep_default_na=False)
        # row_num = sheet.nrows
        boolean_info_list = list()
        for i in range(1, len(workbook)):
            # row = sheet.row_values(i)
            b = boolean_info_temp()
            b.tip_no = tip_no
            b.boolean_index = workbook.iloc[i, 0]
            b.source_db = workbook.iloc[i, 1]
            b.mask_name = workbook.iloc[i, 2]
            b.grid = workbook.iloc[i, 3]
            b.operation = workbook.iloc[i, 4]
            b.total_bias = workbook.iloc[i, 5]
            b.tone = workbook.iloc[i, 6]
            b.import_id = import_id
            b.create_by = u_id
            b.create_date = getDateStr()
            b.create_time = getMilliSecond()

            if b.boolean_index == '' and b.source_db == '' and b.mask_name == '' and b.grid == '' \
                    and b.operation == '' and b.total_bias == '' and b.tone == '':

                continue
            else:
                boolean_info_list.append(b)
        boolean_info_temp.objects.bulk_create(boolean_info_list)

    def insert_layout_info_temp(self, tip_no, import_id, u_id, file_path):
        """批量插入layout信息"""
        l_list = layout_info_temp.objects.select_for_update().filter(tip_no=tip_no)
        if l_list:
            l_list.delete()
        # sheet = workbook.sheet_by_name('Layout_Info')
        workbook = pd.read_excel(file_path, sheet_name=Constant.TOOLING_FORM_EXCEL_SHEET_LAYOUT_INFO, keep_default_na=False)
        # row_num = sheet.nrows
        layout_info_list = list()
        for i in range(1, len(workbook)):
            # row = sheet.row_values(i)
            l = layout_info_temp()
            l.tip_no = tip_no
            l.psm = workbook.iloc[i, 0]
            l.device_name = workbook.iloc[i, 1]
            l.mask_mag = workbook.iloc[i, 2]
            l.source_mag = workbook.iloc[i, 3]
            l.original = workbook.iloc[i, 4]
            l.x1 = str_strip(workbook.iloc[i, 5])
            l.y1 = str_strip(workbook.iloc[i, 6])
            l.pitch_x = str_strip(workbook.iloc[i, 7])
            l.pitch_y = str_strip(workbook.iloc[i, 8])
            l.array_x = str_strip(workbook.iloc[i, 9])
            l.array_y = str_strip(workbook.iloc[i, 10])
            l.mask_name = workbook.iloc[i, 11]
            l.import_id = import_id
            l.create_by = u_id
            l.create_date = getDateStr()
            l.create_time = getMilliSecond()

            if l.psm == '' and l.device_name == '' and l.mask_mag == '' and l.source_mag == '' and l.original == '' and l.x1 == '' \
                    and l.y1 == '' and l.pitch_x == '' and l.pitch_y == '' and l.array_x == '' and l.array_y == '' \
                    and l.mask_name == '':
                continue
            else:
                layout_info_list.append(l)
        layout_info_temp.objects.bulk_create(layout_info_list)

    def insert_mlm_info_temp(self, tip_no, import_id, u_id, file_path):
        """批量插入mlm信息"""
        m_list = mlm_info_temp.objects.select_for_update().filter(tip_no=tip_no)
        if m_list:
            m_list.delete()
        # sheet = workbook.sheet_by_name('MLR_Info')
        workbook = pd.read_excel(file_path, sheet_name=Constant.TOOLING_FORM_EXCEL_SHEET_MLM_INFO, keep_default_na=False)
        # sheet = workbook.sheet_by_name('MLM_Info')
        # row_num = sheet.nrows
        mlm_info_list = list()
        for i in range(1, len(workbook)):
            # row = sheet.row_values(i)
            m = mlm_info_temp()
            m.tip_no = tip_no
            m.mlm_mask_id = workbook.iloc[i, 0]
            m.mask_name = workbook.iloc[i, 1]
            m.field_name = workbook.iloc[i, 2]
            m.shift_x = str_strip(workbook.iloc[i, 3])
            m.shift_y = str_strip(workbook.iloc[i, 4])
            m.import_id = import_id
            m.create_by = u_id
            m.create_date = getDateStr()
            m.create_time = getMilliSecond()

            if m.mlm_mask_id == '' and m.mask_name == '' and m.field_name == '' and m.shift_x == '' and m.shift_y == '':
                continue
            else:
                mlm_info_list.append(m)
        mlm_info_temp.objects.bulk_create(mlm_info_list)
