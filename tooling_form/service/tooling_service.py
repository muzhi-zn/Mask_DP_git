import time, pandas as pd, re

from Mask_DP.settings import Tooling_Form_Sheet
from tooling_form.models import setting, import_list, import_data_temp, tip_no_create, import_error_list, \
    tapeout_info, product_info, ccd_table, device_info, boolean_info, layout_info, mlm_info, layout_info_temp, \
    product_info_temp, tapeout_info_temp, device_info_temp, ccd_table_temp, boolean_info_temp, mlm_info_temp, \
    import_check_list
from django.db import transaction
from system.models import dict
from collections import Counter
from utilslibrary.system_constant import Constant
from utilslibrary.utils.date_utils import getDateStr, getMilliSecond
from utilslibrary.proxy.log_db_proxy import ProxyFactory, InvocationHandler
from utilslibrary.base.base import BaseService
from utilslibrary.decorators.catch_exception_decorators import catch_exception


class PRE_CONDITION_SERVICE(BaseService):

    def __init__(self, Tooling_Form_Sheet, upload_path, u_name):
        self.Product_Info = Tooling_Form_Sheet['Sheet_01']
        self.Tapeout_Info = Tooling_Form_Sheet['Sheet_02']
        self.Device_Info = Tooling_Form_Sheet['Sheet_03']
        self.CCD_Table = Tooling_Form_Sheet['Sheet_04']
        self.Boolean_Info = Tooling_Form_Sheet['Sheet_05']
        self.Layout_Info = Tooling_Form_Sheet['Sheet_06']
        # self.MLR_Info = Tooling_Form_Sheet['Sheet_07']
        self.MLM_Info = Tooling_Form_Sheet['Sheet_07']
        self.upload_path = upload_path
        self.u_name = u_name

    #@catch_exception
    def precondition_check_101(self):
        df = pd.read_excel(self.upload_path, sheet_name=self.Product_Info)
        P_Product_r = setting.objects.filter(sheet_name=self.Product_Info,
                                                column_name='Product').values('row')[0]['row'] + 1
        P_Product_l = setting.objects.filter(sheet_name=self.Product_Info,
                                                column_name='Product').values('column')[0]['column']

        P_Product = str_strip(df.iloc[P_Product_r, P_Product_l])
        P_Tooling_Version_r = setting.objects.filter(sheet_name=self.Product_Info,
                                                        column_name='Tooling_Version').values('row')[0]['row'] + 1
        P_Tooling_Version_l = setting.objects.filter(sheet_name=self.Product_Info,
                                                        column_name='Tooling_Version').values('column')[0]['column']

        P_Tooling_Version = str_strip(df.iloc[P_Tooling_Version_r, P_Tooling_Version_l])

        # 判斷 Product 字元長度
        if len(P_Product) <= 6:
            s = True
        else:
            s = False
            data_error_code = 'ERROR_TIP_1011'
            data_error_description = Constant.ERROR_TIP_1011
            data_error_status = s
            data_create_by = self.u_name
            ToolService().pre_import_error_list(data_error_code,
                                                       data_error_description,
                                                       data_error_status,
                                                       data_create_by)

        # 查詢 Productg
        # product_data_c = import_data_temp.objects.filter(sheet_name='Product_Info',
        #                                             column_name='Tooling_Version',
        #                                             data_key=P_Product,
        #                                             import_data=P_Tooling_Version,
        #                                             is_delete=0).count()

        # product_data_c = product_info.objects.filter(product=P_Product, tooling_version=P_Tooling_Version,
        #                                              is_delete='0').count()
        # # 判斷查詢回傳筆數(count)
        # if product_data_c != 0:
        #     s = False
        #     data_error_code = 'ERROR_TIP_1012'
        #     data_error_description = Constant.ERROR_TIP_1012
        #     data_error_status = s
        #     data_create_by = self.u_name
        #     ToolService().pre_import_error_list(data_error_code,
        #                                                data_error_description,
        #                                                data_error_status,
        #                                                data_create_by)

        # 判断该product是否正在上传
        # uploading_flag = False
        # p_flag = import_product_flag.objects.filter(product_name=P_Product, status=1)
        # if len(p_flag) > 0:  # 正在上传中
        #     uploading_flag = True
        # else:
        #     import_product_flag.objects.get_or_create(product_name=P_Product, status=1)

        return s, P_Product

    #@catch_exception
    def precondition_check_102(self):
        s = False
        df = pd.read_excel(self.upload_path, sheet_name=self.Product_Info)
        P_Design_Rule_r = setting.objects.filter(sheet_name=self.Product_Info,
                                                    column_name='Design_Rule').values('row')[0]['row'] + 1
        P_Design_Rule_l = setting.objects.filter(sheet_name=self.Product_Info,
                                                    column_name='Design_Rule').values('column')[0]['column']
        P_Tech_Process_l = setting.objects.filter(sheet_name=self.Product_Info,
                                                     column_name='Tech_Process').values('column')[0]['column']

        P_Mask_Size = str_strip(df.iloc[P_Design_Rule_r, P_Design_Rule_l])
        P_Tech_Process = str_strip(df.iloc[P_Design_Rule_r, P_Tech_Process_l])

        df_len = len(df)

        while P_Design_Rule_r < df_len:
            # 判斷 Mask_Size, Tech_Process 是否相等
            if P_Mask_Size == P_Tech_Process:
                s = True
            else:
                s = False
                data_error_code = 'ERROR_TIP_1021'
                data_error_description = Constant.ERROR_TIP_1021
                data_error_status = s
                data_create_by = self.u_name
                ToolService().pre_import_error_list(data_error_code,
                                                           data_error_description,
                                                           data_error_status,
                                                           data_create_by)
                return s
            P_Design_Rule_r += 1
        return s

    #@catch_exception
    def precondition_check_201(self):
        s = False
        df = pd.read_excel(self.upload_path, sheet_name=self.Tapeout_Info)
        T_Mask_Name_r = setting.objects.filter(sheet_name=self.Tapeout_Info,
                                                  column_name='Mask_Name').values('row')[0]['row'] + 1
        T_Mask_Name_l = setting.objects.filter(sheet_name=self.Tapeout_Info,
                                                  column_name='Mask_Name').values('column')[0]['column']
        df_len = len(df)

        while T_Mask_Name_r < df_len:
            T_Mask_Name = str_strip(df.iloc[T_Mask_Name_r, T_Mask_Name_l])
            if len(T_Mask_Name) <= 12:
                s = True
            else:
                s = False
                data_error_code = 'ERROR_TIP_2011'
                data_error_description = Constant.ERROR_TIP_2011
                data_error_status = s
                data_create_by = self.u_name
                ToolService().pre_import_error_list(data_error_code,
                                                           data_error_description,
                                                           data_error_status,
                                                           data_create_by)
                return s
            T_Mask_Name_r += 1
        return s

    #@catch_exception
    def precondition_check_202(self):
        s = False
        df = pd.read_excel(self.upload_path, sheet_name=self.Tapeout_Info)
        T_Mask_Name_r = setting.objects.filter(sheet_name=self.Tapeout_Info,
                                                  column_name='Mask_Name').values('row')[0]['row'] + 1
        T_Mask_Name_l = setting.objects.filter(sheet_name=self.Tapeout_Info,
                                                  column_name='Mask_Name').values('column')[0]['column']
        T_BARCODE_l = setting.objects.filter(sheet_name=self.Tapeout_Info,
                                                column_name='BARCODE').values('column')[0]['column']
        df_len = len(df)

        while T_Mask_Name_r < df_len:

            T_Mask_Name = str_strip(df.iloc[T_Mask_Name_r, T_Mask_Name_l])
            T_BARCODE = str_strip(df.iloc[T_Mask_Name_r, T_BARCODE_l])

            if T_Mask_Name == T_BARCODE:
                s = True
            else:
                s = False
                data_error_code = 'ERROR_TIP_2021'
                data_error_description = Constant.ERROR_TIP_2021
                data_error_status = s
                data_create_by = self.u_name
                ToolService().pre_import_error_list(data_error_code,
                                                           data_error_description,
                                                           data_error_status,
                                                           data_create_by)
                return s
            T_Mask_Name_r += 1
        return s

    #@catch_exception
    def precondition_check_203(self):
        s = False
        df_1 = pd.read_excel(self.upload_path, sheet_name=self.Product_Info)
        P_Product_r = setting.objects.filter(sheet_name=self.Product_Info,
                                                column_name='Product').values('row')[0]['row'] + 1
        P_Product_l = setting.objects.filter(sheet_name=self.Product_Info,
                                                column_name='Product').values('column')[0]['column']

        df_2 = pd.read_excel(self.upload_path, sheet_name=self.Tapeout_Info)
        T_Layer_Name_r = setting.objects.filter(sheet_name=self.Tapeout_Info,
                                                   column_name='Layer_Name').values('row')[0]['row'] + 1
        T_Layer_Name_l = setting.objects.filter(sheet_name=self.Tapeout_Info,
                                                   column_name='Layer_Name').values('column')[0]['column']
        T_Version_l = setting.objects.filter(sheet_name=self.Tapeout_Info,
                                                column_name='Version').values('column')[0]['column']
        T_Mask_Name_l = setting.objects.filter(sheet_name=self.Tapeout_Info,
                                                  column_name='Mask_Name').values('column')[0]['column']

        P_Product = str_strip(df_1.iloc[P_Product_r, P_Product_l])

        df_2_len = len(df_2)

        while T_Layer_Name_r < df_2_len:

            T_Layer_Name = str_strip(df_2.iloc[T_Layer_Name_r, T_Layer_Name_l])
            T_Version = str_strip(df_2.iloc[T_Layer_Name_r, T_Version_l])
            T_Mask_Name = str_strip(df_2.iloc[T_Layer_Name_r, T_Mask_Name_l])

            Mask_Name_Merge = P_Product + '-' + T_Layer_Name + T_Version
            if Mask_Name_Merge == T_Mask_Name:
                s = True
            else:
                s = False
                data_error_code = 'ERROR_TIP_2031'
                data_error_description = Constant.ERROR_TIP_2031
                data_error_status = s
                data_create_by = self.u_name
                ToolService().pre_import_error_list(data_error_code,
                                                           data_error_description,
                                                           data_error_status,
                                                           data_create_by)
                return s
            T_Layer_Name_r += 1
        return s

    #@catch_exception
    def precondition_check_204(self):
        df = pd.read_excel(self.upload_path, sheet_name=self.Device_Info)
        D_File_Name_r = setting.objects.filter(sheet_name=self.Device_Info,
                                                  column_name='File_Name').values('row')[0]['row'] + 1
        D_File_Name_l = setting.objects.filter(sheet_name=self.Device_Info,
                                                  column_name='File_Name').values('column')[0]['column']
        df_len = len(df)
        while D_File_Name_r < df_len:

            D_File_Name = str_strip(df.iloc[D_File_Name_r, D_File_Name_l])[-3:]
            if D_File_Name == 'oas' or D_File_Name == 'gds':
                s = True
            else:
                s = False
                data_error_code = 'ERROR_TIP_2041'
                data_error_description = Constant.ERROR_TIP_2041
                data_error_status = s
                data_create_by = self.u_name
                ToolService().pre_import_error_list(data_error_code,
                                                           data_error_description,
                                                           data_error_status,
                                                           data_create_by)
                return s
            D_File_Name_r += 1
        return s

    #@catch_exception
    def precondition_check_301(self):
        df = pd.read_excel(self.upload_path, sheet_name=self.Device_Info)
        D_Source_DB_r = setting.objects.filter(sheet_name=self.Device_Info,
                                                  column_name='Source_DB').values('row')[0]['row'] + 1
        D_Source_DB_l = setting.objects.filter(sheet_name=self.Device_Info,
                                                  column_name='Source_DB').values('column')[0]['column']
        D_PSM_l = setting.objects.filter(sheet_name=self.Device_Info,
                                            column_name='PSM').values('column')[0]['column']
        D_Device_Type_l = setting.objects.filter(sheet_name=self.Device_Info,
                                                    column_name='Device_Type').values('column')[0]['column']
        D_Device_Name_l = setting.objects.filter(sheet_name=self.Device_Info,
                                                    column_name='Device_Name').values('column')[0]['column']
        df_len = len(df)
        Source_DB_set = set()
        Device_Type_set = []

        while D_Source_DB_r < df_len:
            D_PSM = str_strip(df.iloc[D_Source_DB_r, D_PSM_l])
            D_Source_DB = str_strip(df.iloc[D_Source_DB_r, D_Source_DB_l])
            D_Device_Type = str_strip(df.iloc[D_Source_DB_r, D_Device_Type_l])
            D_Device_Name = str_strip(df.iloc[D_Source_DB_r, D_Device_Name_l])

            # 將 Source_DB 加入 Source_DB_set
            Source_DB_set.add(D_Source_DB)

            # 判斷 Device_Type
            if D_Device_Type == 'Frame':
                Device_Type_set.append(D_Device_Type)

            print(df_len, D_Source_DB_r, D_PSM, D_Source_DB, D_Device_Type, D_Device_Name)
            print(Source_DB_set)
            print(Device_Type_set)
            D_Source_DB_r += 1

            # if D_Device_Type == 'F+M' or D_Device_Type:
            #     s = True
            #     pass

        # 判斷 DB 與 Frame 數量是否一致
        if len(Source_DB_set) == len(Device_Type_set):
            s = True
        else:
            s = False
            data_error_code = 'ERROR_TIP_3011'
            data_error_description = Constant.ERROR_TIP_3011
            data_error_status = s
            data_create_by = self.u_name
            ToolService().pre_import_error_list(data_error_code,
                                                       data_error_description,
                                                       data_error_status,
                                                       data_create_by)
            return s

        return s

    #@catch_exception
    def precondition_check_302(self):
        df = pd.read_excel(self.upload_path, sheet_name=self.Device_Info)
        D_Device_Type_r = setting.objects.filter(sheet_name=self.Device_Info,
                                                    column_name='Device_Type').values('row')[0]['row'] + 1
        D_Device_Type_l = setting.objects.filter(sheet_name=self.Device_Info,
                                                    column_name='Device_Type').values('column')[0]['column']
        D_Device_Name_l = setting.objects.filter(sheet_name=self.Device_Info,
                                                    column_name='Device_Name').values('column')[0]['column']
        df_len = len(df)

        # MP001 REGEX
        pattern = re.compile("MP(?!000)[0-9]{3}")

        while D_Device_Type_r < df_len:
            D_Device_Type = str_strip(df.iloc[D_Device_Type_r, D_Device_Type_l])
            D_Device_Name = str_strip(df.iloc[D_Device_Type_r, D_Device_Name_l])
            m = pattern.match(D_Device_Name)

            if D_Device_Type == 'F+M':
                s = True
                pass
            elif D_Device_Type == 'Frame' and D_Device_Name == 'FRAME':
                s = True
            elif D_Device_Type == 'Main':
                if m is not None:
                    s = True
                else:
                    s = False
                    data_error_code = 'ERROR_TIP_3022'
                    data_error_description = Constant.ERROR_TIP_3022
                    data_error_status = s
                    data_create_by = self.u_name
                    ToolService().pre_import_error_list(data_error_code,
                                                               data_error_description,
                                                               data_error_status,
                                                               data_create_by)
                return s
            else:
                s = False
                data_error_code = 'ERROR_TIP_3021'
                data_error_description = Constant.ERROR_TIP_3021
                data_error_status = s
                data_create_by = self.u_name
                ToolService().pre_import_error_list(data_error_code, data_error_description,
                                                           data_error_status, data_create_by)
                return s
            D_Device_Type_r += 1
        return s

    #@catch_exception
    def precondition_check_303(self):
        df = pd.read_excel(self.upload_path, sheet_name=self.Device_Info)
        D_LB_X_r = setting.objects.filter(sheet_name=self.Device_Info,
                                             column_name='LB_X').values('row')[0]['row'] + 1
        D_LB_X_l = setting.objects.filter(sheet_name=self.Device_Info,
                                             column_name='LB_X').values('column')[0]['column']
        D_LB_Y_l = setting.objects.filter(sheet_name=self.Device_Info,
                                             column_name='LB_Y').values('column')[0]['column']
        D_RT_X_l = setting.objects.filter(sheet_name=self.Device_Info,
                                             column_name='RT_X').values('column')[0]['column']
        D_RT_Y_l = setting.objects.filter(sheet_name=self.Device_Info,
                                             column_name='RT_Y').values('column')[0]['column']
        df_len = len(df)

        while D_LB_X_r < df_len:
            D_LB_X = float_strip(df.iloc[D_LB_X_r, D_LB_X_l])
            D_LB_Y = float_strip(df.iloc[D_LB_X_r, D_LB_Y_l])
            D_RT_X = float_strip(df.iloc[D_LB_X_r, D_RT_X_l])
            D_RT_Y = float_strip(df.iloc[D_LB_X_r, D_RT_Y_l])

            if ((D_RT_X - D_LB_X) <= 26000) and ((D_RT_Y - D_LB_Y) <= 33000):
                s = True
            else:
                s = False
                data_error_code = 'ERROR_TIP_3031'
                data_error_description = Constant.ERROR_TIP_3031
                data_error_status = s
                data_create_by = self.u_name
                ToolService().pre_import_error_list(data_error_code,
                                                           data_error_description,
                                                           data_error_status,
                                                           data_create_by)
                return s
            D_LB_X_r += 1
        return s

    #@catch_exception
    def precondition_check_304(self):
        df_1 = pd.read_excel(self.upload_path, sheet_name=self.Device_Info)
        D_PSM_r = setting.objects.filter(sheet_name=self.Device_Info,
                                            column_name='PSM').values('row')[0]['row'] + 1
        D_PSM_l = setting.objects.filter(sheet_name=self.Device_Info,
                                            column_name='PSM').values('column')[0]['column']
        D_Device_Name_l = setting.objects.filter(sheet_name=self.Device_Info,
                                                    column_name='Device_Name').values('column')[0]['column']

        df_2 = pd.read_excel(self.upload_path, sheet_name=self.Layout_Info)
        L_PSM_r = setting.objects.filter(sheet_name=self.Layout_Info,
                                            column_name='PSM').values('row')[0]['row'] + 1
        L_PSM_l = setting.objects.filter(sheet_name=self.Layout_Info,
                                            column_name='PSM').values('column')[0]['column']
        L_Device_Name_l = setting.objects.filter(sheet_name=self.Layout_Info,
                                                    column_name='Device_Name').values('column')[0]['column']

        df_len_1 = len(df_1)
        df_len_2 = len(df_2)

        D_Y_LIST = set()
        D_N_LIST = set()
        L_Y_LIST = set()
        L_N_LIST = set()

        while D_PSM_r < df_len_1:
            D_PSM = str_strip(df_2.iloc[D_PSM_r, D_PSM_l])
            D_Device_Name = str_strip(df_2.iloc[D_PSM_r, D_Device_Name_l])

            if D_PSM == 'Y':
                D_Y_LIST.add(D_Device_Name)
            elif D_PSM == 'N':
                D_N_LIST.add(D_Device_Name)
            else:
                s = False
                data_error_code = 'ERROR_TIP_3041'
                data_error_description = str(Constant.ERROR_TIP_3041 % (D_PSM_r, 'Device_Info', D_PSM))
                data_error_status = s
                data_create_by = self.u_name
                ToolService().pre_import_error_list(data_error_code,
                                                           data_error_description,
                                                           data_error_status,
                                                           data_create_by)
                return s

            D_PSM_r += 1

        while L_PSM_r < df_len_2:
            L_PSM = str_strip(df_2.iloc[L_PSM_r, L_PSM_l])
            L_Device_Name = str_strip(df_2.iloc[L_PSM_r, L_Device_Name_l])

            if L_PSM == 'Y':
                L_Y_LIST.add(L_Device_Name)
            elif L_PSM == 'N':
                L_N_LIST.add(L_Device_Name)
            else:
                s = False
                data_error_code = 'ERROR_TIP_3041'
                data_error_description = str(Constant.ERROR_TIP_020 % (L_PSM_r, 'Layout_Info', L_PSM))
                data_error_status = s
                data_create_by = self.u_name
                ToolService().pre_import_error_list(data_error_code,
                                                           data_error_description,
                                                           data_error_status,
                                                           data_create_by)
                return s

            L_PSM_r += 1

        if ((D_Y_LIST > L_Y_LIST) - (D_Y_LIST < L_Y_LIST)) == 0 and (
                (D_N_LIST > L_N_LIST) - (D_N_LIST < L_N_LIST)) == 0:
            s = True
        else:
            s = False
            data_error_code = 'ERROR_TIP_021'
            data_error_description = str(Constant.ERROR_TIP_021)
            data_error_status = s
            data_create_by = self.u_name
            ToolService().pre_import_error_list(data_error_code,
                                                       data_error_description,
                                                       data_error_status,
                                                       data_create_by)
            return s

        return s

    #@catch_exception
    def precondition_check_305(self):
        df = pd.read_excel(self.upload_path, sheet_name=self.Device_Info)
        D_Check_method_r = setting.objects.filter(sheet_name=self.Device_Info,
                                                     column_name='Check_method').values('row')[0]['row'] + 1
        D_Check_method_l = setting.objects.filter(sheet_name=self.Device_Info,
                                                     column_name='Check_method').values('column')[0]['column']
        D_value_l = setting.objects.filter(sheet_name=self.Device_Info,
                                              column_name='value').values('column')[0]['column']

        df_len = len(df)

        while D_Check_method_r < df_len:
            D_Check_method = str_strip(df.iloc[D_Check_method_r, D_Check_method_l])
            D_value = str_strip(df.iloc[D_Check_method_r, D_value_l])

            if D_Check_method == 'md5sum' and len(D_value) == 32:
                s = True
            elif D_Check_method == 'sha-512' and len(D_value) == 128:
                s = True
            else:
                s = False
                data_error_code = 'ERROR_TIP_3051'
                data_error_description = Constant.ERROR_TIP_3051
                data_error_status = s
                data_create_by = self.u_name
                ToolService().pre_import_error_list(data_error_code,
                                                           data_error_description,
                                                           data_error_status,
                                                           data_create_by)
                return s
            D_Check_method_r += 1
        return s

    #@catch_exception
    def precondition_check_401(self):
        s = False
        df_1 = pd.read_excel(self.upload_path, sheet_name=self.CCD_Table)
        C_Coor_X_r = setting.objects.filter(sheet_name=self.CCD_Table,
                                               column_name='Coor_X').values('row')[0]['row'] + 1
        C_Coor_X_l = setting.objects.filter(sheet_name=self.CCD_Table,
                                               column_name='Coor_X').values('column')[0]['column']
        C_Coor_Y_l = setting.objects.filter(sheet_name=self.CCD_Table,
                                               column_name='Coor_Y').values('column')[0]['column']
        df_len_1 = len(df_1)

        while C_Coor_X_r < df_len_1:

            C_Coor_X = float_strip(df_1.iloc[C_Coor_X_r, C_Coor_X_l])
            C_Coor_Y = float_strip(df_1.iloc[C_Coor_X_r, C_Coor_Y_l])

            if C_Coor_X == '' or C_Coor_Y == '':
                s = False
                data_error_code = 'ERROR_TIP_NULL'
                data_error_description = str(Constant.ERROR_TIP_NULL % (self.CCD_Table, ' Coor_X,Coor_Y '))
                data_error_status = s
                data_create_by = self.u_name
                ToolService().pre_import_error_list(data_error_code,
                                                           data_error_description,
                                                           data_error_status,
                                                           data_create_by)
                return s
            elif (0 <= C_Coor_X <= 152400) and (0 <= C_Coor_Y <= 152400):
                s = True
            else:
                s = False
                data_error_code = 'ERROR_TIP_4011'
                data_error_description = str(Constant.ERROR_TIP_4011)
                data_error_status = s
                data_create_by = self.u_name
                ToolService().pre_import_error_list(data_error_code,
                                                           data_error_description,
                                                           data_error_status,
                                                           data_create_by)
                return s
            C_Coor_X_r += 1
        return s

    #@catch_exception
    def precondition_check_402(self):
        df_1 = pd.read_excel(self.upload_path, sheet_name=self.CCD_Table)
        C_Item_r = setting.objects.filter(sheet_name=self.CCD_Table,
                                             column_name='Item').values('row')[0]['row'] + 1
        C_Item_l = setting.objects.filter(sheet_name=self.CCD_Table,
                                             column_name='Item').values('column')[0]['column']
        df_len_1 = len(df_1)

        while C_Item_r < df_len_1:
            C_Item = str_strip(df_1.iloc[C_Item_r, C_Item_l])

            if len(C_Item) <= 120:
                s = True
            else:
                s = False
                data_error_code = 'ERROR_TIP_4021'
                data_error_description = str(Constant.ERROR_TIP_4021)
                data_error_status = s
                data_create_by = self.u_name
                # self.pre_import_error_message_log(sheet_name, column_name, data_error_code, data_error_description,
                #                                   data_error_status, data_create_by)
                ToolService().pre_import_error_list(data_error_code,
                                                           data_error_description,
                                                           data_error_status,
                                                           data_create_by)
                return s
            C_Item_r += 1
        return s

    #@catch_exception
    def precondition_check_403(self):
        df_1 = pd.read_excel(self.upload_path, sheet_name=self.CCD_Table)
        C_CD_4X_nm_r = setting.objects.filter(sheet_name=self.CCD_Table,
                                                 column_name='CD_4X_nm').values('row')[0]['row'] + 1
        C_CD_4X_nm_l = setting.objects.filter(sheet_name=self.CCD_Table,
                                                 column_name='CD_4X_nm').values('column')[0]['column']
        df_len_1 = len(df_1)

        while C_CD_4X_nm_r < df_len_1:
            # try:
            C_CD_4X_nm = float_strip(df_1.iloc[C_CD_4X_nm_r, C_CD_4X_nm_l])
            # except:
            #     s = False
            #     data_error_code = 'ERROR_TIP_301'
            #     data_error_description = str(Constant.ERROR_TIP_301)
            #     data_error_status = s
            #     data_create_by = u_name
            #     # self.pre_import_error_message_log(sheet_name, column_name, data_error_code, data_error_description,
            #     #                                   data_error_status, data_create_by)
            #     self.pre_import_error_message_log(data_error_code, data_error_description,
            #                                       data_error_status, data_create_by)
            #     return s

            if 0 <= C_CD_4X_nm <= 2000:
                s = True
            else:
                s = False
                data_error_code = 'ERROR_TIP_4031'
                data_error_description = str(Constant.ERROR_TIP_4031)
                data_error_status = s
                data_create_by = self.u_name
                # self.pre_import_error_message_log(sheet_name, column_name, data_error_code, data_error_description,
                #                                   data_error_status, data_create_by)
                ToolService().pre_import_error_list(data_error_code,
                                                           data_error_description,
                                                           data_error_status,
                                                           data_create_by)
                return s
            C_CD_4X_nm_r += 1
        return s

    #@catch_exception
    def precondition_check_501(self):
        df_1 = pd.read_excel(self.upload_path, sheet_name=self.Boolean_Info)
        B_Total_Bias_r = setting.objects.filter(sheet_name=self.Boolean_Info,
                                                   column_name='Total_Bias').values('row')[0]['row'] + 1
        B_Total_Bias_l = setting.objects.filter(sheet_name=self.Boolean_Info,
                                                   column_name='Total_Bias').values('column')[0]['column']

        df_len_1 = len(df_1)

        while B_Total_Bias_r < df_len_1:
            B_Total_Bias = float_strip(df_1.iloc[B_Total_Bias_r, B_Total_Bias_l])
            if B_Total_Bias <= 500:
                s = True
            else:
                s = False
                data_error_code = 'ERROR_TIP_5011'
                data_error_description = str(Constant.ERROR_TIP_5011 % B_Total_Bias)
                data_error_status = s
                data_create_by = self.u_name
                ToolService().pre_import_error_list(data_error_code,
                                                           data_error_description,
                                                           data_error_status,
                                                           data_create_by)
                return s
            B_Total_Bias_r += 1
        return s

    #@catch_exception
    def precondition_check_502(self):
        df_1 = pd.read_excel(self.upload_path, sheet_name=self.Tapeout_Info)
        T_Mask_Name_r = setting.objects.filter(sheet_name=self.Tapeout_Info,
                                                  column_name='Mask_Name').values('row')[0]['row'] + 1
        T_Mask_Name_l = setting.objects.filter(sheet_name=self.Tapeout_Info,
                                                  column_name='Mask_Name').values('column')[0]['column']
        T_T_O_l = setting.objects.filter(sheet_name=self.Tapeout_Info,
                                            column_name='T_O').values('column')[0]['column']

        df_2 = pd.read_excel(self.upload_path, sheet_name=self.Boolean_Info)
        B_Mask_Name_r = setting.objects.filter(sheet_name=self.Boolean_Info,
                                                  column_name='Mask_Name').values('row')[0]['row'] + 1
        B_Mask_Name_l = setting.objects.filter(sheet_name=self.Boolean_Info,
                                                  column_name='Mask_Name').values('column')[0]['column']

        df_len_1 = len(df_1)
        df_len_2 = len(df_2)

        tapeout_set = set()
        boolean_set = set()
        N_set = set()

        while T_Mask_Name_r < df_len_1:
            T_Mask_Name = str_strip(df_1.iloc[T_Mask_Name_r, T_Mask_Name_l])
            T_T_O = str_strip(df_1.iloc[T_Mask_Name_r, T_T_O_l])
            if T_T_O == 'Y':
                tapeout_set.add(T_Mask_Name)
            else:
                N_set.add(T_Mask_Name)
            T_Mask_Name_r += 1

        while B_Mask_Name_r < df_len_2:
            B_Mask_Name = str_strip(df_2.iloc[B_Mask_Name_r, B_Mask_Name_l])
            if B_Mask_Name not in N_set:
                boolean_set.add(B_Mask_Name)
            B_Mask_Name_r += 1

        # print(tapeout_set, boolean_set)
        if tapeout_set == boolean_set:
            s = True
        else:
            s = False
            data_error_code = 'ERROR_TIP_5021'
            data_error_description = str(Constant.ERROR_TIP_5021)
            data_error_status = s
            data_create_by = self.u_name
            ToolService().pre_import_error_list(data_error_code,
                                                       data_error_description,
                                                       data_error_status,
                                                       data_create_by)
            return s
        return s

    #@catch_exception
    def precondition_check_503(self):
        df_1 = pd.read_excel(self.upload_path, sheet_name=self.Boolean_Info)
        B_Mask_Name_r = setting.objects.filter(sheet_name=self.Boolean_Info,
                                                  column_name='Mask_Name').values('row')[0]['row'] + 1
        B_Mask_Name_l = setting.objects.filter(sheet_name=self.Boolean_Info,
                                                  column_name='Mask_Name').values('column')[0]['column']
        B_Tone_l = setting.objects.filter(sheet_name=self.Boolean_Info,
                                             column_name='Tone').values('column')[0]['column']

        df_len_1 = len(df_1)
        dict_all = {}

        while B_Mask_Name_r < df_len_1:
            B_Mask_Name = str_strip(df_1.iloc[B_Mask_Name_r, B_Mask_Name_l])
            B_Tone = str_strip(df_1.iloc[B_Mask_Name_r, B_Tone_l])

            get_result = dict_all.get(B_Mask_Name, None)

            if get_result is None:
                dict_one = {B_Mask_Name: B_Tone}
                dict_all.update(dict_one)
                s = True
            elif get_result == B_Tone:
                s = True
            else:
                s = False
                data_error_code = 'ERROR_TIP_5031'
                data_error_description = str(Constant.ERROR_TIP_5031 % B_Mask_Name_r)
                data_error_status = s
                data_create_by = self.u_name
                ToolService().pre_import_error_list(data_error_code,
                                                           data_error_description,
                                                           data_error_status,
                                                           data_create_by)
                return s
            B_Mask_Name_r += 1
        return s

    #@catch_exception
    def precondition_check_504(self):
        df_1 = pd.read_excel(self.upload_path, sheet_name=self.Device_Info)
        D_Source_DB_r = setting.objects.filter(sheet_name=self.Device_Info,
                                                  column_name='Source_DB').values('row')[0]['row'] + 1
        D_Source_DB_l = setting.objects.filter(sheet_name=self.Device_Info,
                                                  column_name='Source_DB').values('column')[0]['column']
        D_Boolean_Index_l = setting.objects.filter(sheet_name=self.Device_Info,
                                                      column_name='Boolean_Index').values('column')[0]['column']

        df_2 = pd.read_excel(self.upload_path, sheet_name=self.Boolean_Info)
        B_Source_DB_r = setting.objects.filter(sheet_name=self.Boolean_Info,
                                                  column_name='Source_DB').values('row')[0]['row'] + 1
        B_Source_DB_l = setting.objects.filter(sheet_name=self.Boolean_Info,
                                                  column_name='Source_DB').values('column')[0]['column']
        B_Boolean_Index_l = setting.objects.filter(sheet_name=self.Boolean_Info,
                                                      column_name='Boolean_Index').values('column')[0]['column']

        df_len_1 = len(df_1)
        df_len_2 = len(df_2)
        set_B = set()
        D_B_flag = True
        while B_Source_DB_r < df_len_2:
            B_Source_DB = str_strip(df_2.iloc[B_Source_DB_r, B_Source_DB_l])
            B_Boolean_Index = str_strip(df_2.iloc[B_Source_DB_r, B_Boolean_Index_l])
            set_B.add(B_Source_DB + '_' + B_Boolean_Index)
            B_Source_DB_r += 1

        while D_Source_DB_r < df_len_1:
            D_Source_DB = str_strip(df_1.iloc[D_Source_DB_r, D_Source_DB_l])
            D_Boolean_Index = str_strip(df_1.iloc[D_Source_DB_r, D_Boolean_Index_l])
            if (D_Source_DB + '_' + D_Boolean_Index) not in set_B:
                D_B_flag = False
                break
            D_Source_DB_r += 1

        if D_B_flag:
            s = True
        else:
            s = False
            data_error_code = 'ERROR_TIP_5041'
            data_error_description = Constant.ERROR_TIP_5041
            data_error_status = s
            data_create_by = self.u_name
            ToolService().pre_import_error_list(data_error_code,
                                                       data_error_description,
                                                       data_error_status,
                                                       data_create_by)
        return s

    #@catch_exception
    def precondition_check_601(self):
        df_1 = pd.read_excel(self.upload_path, sheet_name=self.Device_Info)
        D_PSM_r = setting.objects.filter(sheet_name=self.Device_Info,
                                            column_name='PSM').values('row')[0]['row'] + 1
        D_PSM_l = setting.objects.filter(sheet_name=self.Device_Info,
                                            column_name='PSM').values('column')[0]['column']
        D_Source_DB_l = setting.objects.filter(sheet_name=self.Device_Info,
                                                  column_name='Source_DB').values('column')[0]['column']

        df_2 = pd.read_excel(self.upload_path, sheet_name=self.Layout_Info)
        L_PSM_r = setting.objects.filter(sheet_name=self.Layout_Info,
                                            column_name='PSM').values('row')[0]['row'] + 1
        L_PSM_l = setting.objects.filter(sheet_name=self.Layout_Info,
                                            column_name='PSM').values('column')[0]['column']

        # 計算行數
        df_len_1 = len(df_1)
        df_len_2 = len(df_2)

        set_D_N = []
        set_D_Y = []
        set_L_N = []
        set_L_Y = []

        while D_PSM_r < df_len_1:
            D_PSM = str_strip(df_1.iloc[D_PSM_r, D_PSM_l])
            D_Source_DB = str_strip(df_1.iloc[D_PSM_r, D_Source_DB_l])
            if D_PSM == 'N':
                set_D_N.append(D_Source_DB)
            if D_PSM == 'Y':
                set_D_Y.append(D_Source_DB)
            D_PSM_r += 1

        while L_PSM_r < df_len_2:
            L_PSM = str_strip(df_2.iloc[L_PSM_r, L_PSM_l])
            if L_PSM == 'N':
                set_L_N.append(L_PSM)
            if L_PSM == 'Y':
                set_L_Y.append(L_PSM)
            L_PSM_r += 1

        D_N = Counter(set_D_N).most_common(1)
        D_Y = Counter(set_D_Y).most_common(1)
        L_N = Counter(set_L_N).most_common(1)
        L_Y = Counter(set_L_Y).most_common(1)

        if len(D_N):
            D_N_value = str(D_N[0][1])
        else:
            D_N_value = 0

        if len(D_Y):
            D_Y_value = str(D_Y[0][1])
        else:
            D_Y_value = 0

        if len(L_N):
            L_N_value = str(L_N[0][1])
        else:
            L_N_value = 0

        if len(L_Y):
            L_Y_value = str(L_Y[0][1])
        else:
            L_Y_value = 0

        if (int(L_N_value) >= int(D_N_value)) and (int(L_Y_value) >= int(D_Y_value)):
            s = True
        else:
            s = False
            data_error_code = 'ERROR_TIP_6011'
            data_error_description = Constant.ERROR_TIP_6011
            data_error_status = s
            data_create_by = self.u_name
            ToolService().pre_import_error_list(data_error_code,
                                                       data_error_description,
                                                       data_error_status,
                                                       data_create_by)
        return s

    #@catch_exception
    def precondition_check_602(self):
        df_1 = pd.read_excel(self.upload_path, sheet_name=self.Layout_Info)
        X1_r = setting.objects.filter(sheet_name=self.Layout_Info,
                                         column_name='X1').values('row')[0]['row'] + 1
        X1_l = setting.objects.filter(sheet_name=self.Layout_Info,
                                         column_name='X1').values('column')[0]['column']
        Y1_l = setting.objects.filter(sheet_name=self.Layout_Info,
                                         column_name='Y1').values('column')[0]['column']

        df_len_1 = len(df_1)

        while X1_r < df_len_1:
            X1 = float_strip(df_1.iloc[X1_r, X1_l])
            Y1 = float_strip(df_1.iloc[X1_r, Y1_l])

            if (X1 > -13000) and (X1 < 13000) and (Y1 > -16500) and (Y1 < 16500):
                s = True
            else:
                s = False
                data_error_code = 'ERROR_TIP_6021'
                data_error_description = Constant.ERROR_TIP_6021
                data_error_status = s
                data_create_by = self.u_name
                ToolService().pre_import_error_list(data_error_code,
                                                           data_error_description,
                                                           data_error_status,
                                                           data_create_by)
                return s
            X1_r += 1
        return s

    #@catch_exception
    def precondition_check_603(self):
        df_1 = pd.read_excel(self.upload_path, sheet_name=self.Layout_Info)
        L_Array_X_r = setting.objects.filter(sheet_name=self.Layout_Info,
                                                column_name='Array_X').values('row')[0]['row'] + 1
        L_Array_X_l = setting.objects.filter(sheet_name=self.Layout_Info,
                                                column_name='Array_X').values('column')[0]['column']
        L_Array_Y_l = setting.objects.filter(sheet_name=self.Layout_Info,
                                                column_name='Array_Y').values('column')[0]['column']
        L_Pitch_X_l = setting.objects.filter(sheet_name=self.Layout_Info,
                                                column_name='Pitch_X').values('column')[0]['column']
        L_Pitch_Y_l = setting.objects.filter(sheet_name=self.Layout_Info,
                                                column_name='Pitch_Y').values('column')[0]['column']

        df_len_1 = len(df_1)

        while L_Array_X_r < df_len_1:
            L_Pitch_X = df_1.iloc[L_Array_X_r, L_Pitch_X_l]
            L_Pitch_Y = df_1.iloc[L_Array_X_r, L_Pitch_Y_l]
            L_Array_X = df_1.iloc[L_Array_X_r, L_Array_X_l]
            L_Array_Y = df_1.iloc[L_Array_X_r, L_Array_Y_l]

            if ((str(L_Array_X) == 'nan') and (str(L_Array_Y) == 'nan') and
                    (str(L_Pitch_X) == 'nan') and (str(L_Pitch_Y) == 'nan')):
                s = True
            elif ((str(L_Array_X != 'nan')) and (str(L_Array_Y) != 'nan') and
                  (str(L_Pitch_X) != 'nan') and (str(L_Pitch_Y) != 'nan')):

                if ((float(L_Pitch_X) > 0) and (float(L_Pitch_Y) > 0) and
                        (int(L_Array_X) > 0) and (isinstance(L_Array_X, int)) and
                        (int(L_Array_Y) > 0) and (isinstance(L_Array_Y, int))):

                    if ((float(L_Pitch_X) > -13000) and (float(L_Pitch_X) < 1300) and
                            (float(L_Pitch_Y) > -16500) and (float(L_Pitch_Y) < 16500)):
                        s = True
                    else:
                        s = False
                        data_error_code = 'ERROR_TIP_6031'
                        data_error_description = Constant.ERROR_TIP_6031
                        data_error_status = s
                        data_create_by = self.u_name
                        ToolService().pre_import_error_list(data_error_code,
                                                                   data_error_description,
                                                                   data_error_status,
                                                                   data_create_by)
                        return s
                else:
                    s = False
                    data_error_code = 'ERROR_TIP_6032'
                    data_error_description = Constant.ERROR_TIP_6032
                    data_error_status = s
                    data_create_by = self.u_name
                    ToolService().pre_import_error_list(data_error_code,
                                                               data_error_description,
                                                               data_error_status,
                                                               data_create_by)
                    return s
            else:
                s = False
                data_error_code = 'ERROR_TIP_6033'
                data_error_description = Constant.ERROR_TIP_6033
                data_error_status = s
                data_create_by = self.u_name
                ToolService().pre_import_error_list(data_error_code,
                                                           data_error_description,
                                                           data_error_status,
                                                           data_create_by)
                return s
            L_Array_X_r += 1
        return s

    #@catch_exception
    def precondition_check_604(self):
        df_1 = pd.read_excel(self.upload_path, sheet_name=self.Layout_Info)

        L_Device_Name_r = setting.objects.filter(sheet_name=self.Layout_Info,
                                                    column_name='Device_Name').values('row')[0]['row'] + 1
        L_Device_Name_l = setting.objects.filter(sheet_name=self.Layout_Info,
                                                    column_name='Device_Name').values('column')[0]['column']
        L_X1_l = setting.objects.filter(sheet_name=self.Layout_Info,
                                           column_name='X1').values('column')[0]['column']
        L_Y1_l = setting.objects.filter(sheet_name=self.Layout_Info,
                                           column_name='Y1').values('column')[0]['column']

        df_2 = pd.read_excel(self.upload_path, sheet_name=self.Device_Info)
        D_Device_Name_r = setting.objects.filter(sheet_name=self.Device_Info,
                                                    column_name='Device_Name').values('row')[0]['row'] + 1
        D_Device_Name_l = setting.objects.filter(sheet_name=self.Device_Info,
                                                    column_name='Device_Name').values('column')[0]['column']
        D_LB_X_l = setting.objects.filter(sheet_name=self.Device_Info,
                                             column_name='LB_X').values('column')[0]['column']
        D_LB_Y_l = setting.objects.filter(sheet_name=self.Device_Info,
                                             column_name='LB_Y').values('column')[0]['column']
        D_RT_X_l = setting.objects.filter(sheet_name=self.Device_Info,
                                             column_name='RT_X').values('column')[0]['column']
        D_RT_Y_l = setting.objects.filter(sheet_name=self.Device_Info,
                                             column_name='RT_Y').values('column')[0]['column']

        df_len_1 = len(df_1)
        df_len_2 = len(df_2)

        while L_Device_Name_r < df_len_1:
            L_Device_Name = str_strip(df_1.iloc[L_Device_Name_r, L_Device_Name_l])
            L_X1 = float_strip(df_1.iloc[L_Device_Name_r, L_X1_l])
            L_Y1 = float_strip(df_1.iloc[L_Device_Name_r, L_Y1_l])

            while D_Device_Name_r < df_len_2:
                D_Device_Name = str_strip(df_2.iloc[D_Device_Name_r, D_Device_Name_l])
                D_LB_X = float_strip(df_2.iloc[D_Device_Name_r, D_LB_X_l])
                D_LB_Y = float_strip(df_2.iloc[D_Device_Name_r, D_LB_Y_l])
                D_RT_X = float_strip(df_2.iloc[D_Device_Name_r, D_RT_X_l])
                D_RT_Y = float_strip(df_2.iloc[D_Device_Name_r, D_RT_Y_l])

                if L_Device_Name == D_Device_Name:
                    L_X1_P = L_X1 + (D_RT_X - D_LB_X) / 2
                    L_X1_M = L_X1 - (D_RT_X - D_LB_X) / 2
                    L_Y1_P = L_Y1 + (D_RT_Y - D_LB_Y) / 2
                    L_Y1_M = L_Y1 - (D_RT_Y - D_LB_Y) / 2

                    if 13000 >= L_X1_P >= -13000 and 13000 >= L_X1_M >= -13000 \
                            and 16500 >= L_Y1_P >= -16500 and 16500 >= L_Y1_M >= -16500:
                        s = True
                    else:
                        s = False
                        data_error_code = 'ERROR_TIP_6041'
                        data_error_description = str(Constant.ERROR_TIP_6041 % L_Device_Name_r)
                        data_error_status = s
                        data_create_by = self.u_name
                        ToolService().pre_import_error_list(data_error_code,
                                                                   data_error_description,
                                                                   data_error_status,
                                                                   data_create_by)
                        return s
                D_Device_Name_r += 1
            L_Device_Name_r += 1
        return s

    #@catch_exception
    def precondition_check_605(self):
        layout_set = set()
        device_set = set()
        df_1 = pd.read_excel(self.upload_path, sheet_name=self.Layout_Info)

        L_Device_Name_r = setting.objects.filter(sheet_name=self.Layout_Info,
                                                 column_name='Device_Name').values('row')[0]['row'] + 1
        L_Device_Name_l = setting.objects.filter(sheet_name=self.Layout_Info,
                                                 column_name='Device_Name').values('column')[0]['column']
        df_2 = pd.read_excel(self.upload_path, sheet_name=self.Device_Info)
        D_Device_Name_r = setting.objects.filter(sheet_name=self.Device_Info,
                                                 column_name='Device_Name').values('row')[0]['row'] + 1
        D_Device_Name_l = setting.objects.filter(sheet_name=self.Device_Info,
                                                 column_name='Device_Name').values('column')[0]['column']
        df_len_1 = len(df_1)
        df_len_2 = len(df_2)
        while L_Device_Name_r < df_len_1:
            L_Device_Name = str_strip(df_1.iloc[L_Device_Name_r, L_Device_Name_l])
            if L_Device_Name not in layout_set:
                layout_set.add(L_Device_Name)
            L_Device_Name_r += 1
        while D_Device_Name_r < df_len_2:
            D_Device_Name = str_strip(df_2.iloc[D_Device_Name_r, D_Device_Name_l])
            if D_Device_Name not in device_set:
                device_set.add(D_Device_Name)
            D_Device_Name_r += 1
        if layout_set == device_set:
            s = True
        else:
            s = False
            diff_device = ','.join(list(layout_set ^ device_set))
            data_error_code = 'ERROR_TIP_6051'
            data_error_description = str(Constant.ERROR_TIP_6051 % diff_device)
            data_error_status = s
            data_create_by = self.u_name
            ToolService().pre_import_error_list(data_error_code,
                                                data_error_description,
                                                data_error_status,
                                                data_create_by)
            return s
        return s

    # =================================================
    #@catch_exception
    def precondition_check_05(self):
        df_1 = pd.read_excel(self.upload_path, sheet_name='Device_Info')
        D_Boolean_Index_r = setting.objects.filter(sheet_name='Device_Info',
                                                      column_name='Boolean_Index').values('row')[0]['row'] + 1
        D_Boolean_Index_l = setting.objects.filter(sheet_name='Device_Info',
                                                      column_name='Boolean_Index').values('column')[0]['column']
        df_2 = pd.read_excel(self.upload_path, sheet_name='Boolean_Info')
        B_Boolean_Index_r = setting.objects.filter(sheet_name='Boolean_Info',
                                                      column_name='Boolean_Index').values('row')[0]['row'] + 1
        B_Boolean_Index_l = setting.objects.filter(sheet_name='Boolean_Info',
                                                      column_name='Boolean_Index').values('column')[0]['column']

        df_1_len = len(df_1)
        D_Boolean_set = set()
        while D_Boolean_Index_r < df_1_len:
            D_Boolean = str_strip(df_2.iloc[D_Boolean_Index_r, D_Boolean_Index_l])
            D_Boolean_set.add(D_Boolean)
            D_Boolean_Index_r += 1

        df_2_len = len(df_2)
        B_Boolean_set = set()
        while B_Boolean_Index_r < df_2_len:
            B_Boolean = str_strip(df_2.iloc[B_Boolean_Index_r, B_Boolean_Index_l])
            B_Boolean_set.add(B_Boolean)
            B_Boolean_Index_r += 1

        D_len = len(D_Boolean_set)
        B_len = len(B_Boolean_set)

        if D_len == B_len:
            s = True
        else:
            s = False
            data_error_code = 'ERROR_TIP_005'
            data_error_description = Constant.ERROR_TIP_005
            data_error_status = s
            data_create_by = self.u_name
            self.pre_import_error_list(data_error_code, data_error_description,
                                              data_error_status, data_create_by)
            return s
        return s

    #@catch_exception
    def precondition_check_09(self):
        df_1 = pd.read_excel(self.upload_path, sheet_name='Device_Info')
        D_Source_DB_r = setting.objects.filter(sheet_name='Device_Info',
                                                  column_name='Source_DB').values('row')[0]['row'] + 1
        D_Source_DB_l = setting.objects.filter(sheet_name='Device_Info',
                                                  column_name='Source_DB').values('column')[0]['column']

        df_2 = pd.read_excel(self.upload_path, sheet_name='Boolean_Info')
        B_Source_DB_r = setting.objects.filter(sheet_name='Boolean_Info',
                                                  column_name='Source_DB').values('row')[0]['row'] + 1
        B_Source_DB_l = setting.objects.filter(sheet_name='Boolean_Info',
                                                  column_name='Source_DB').values('column')[0]['column']

        df_len_1 = len(df_1)
        df_len_2 = len(df_2)
        set_D = set()
        set_B = set()

        while D_Source_DB_r < df_len_1:
            D_Source_DB = str_strip(df_2.iloc[D_Source_DB_r, D_Source_DB_l])
            set_D.add(D_Source_DB)
            D_Source_DB_r += 1

        while B_Source_DB_r < df_len_2:
            B_Source_DB = str_strip(df_2.iloc[B_Source_DB_r, B_Source_DB_l])
            set_B.add(B_Source_DB)
            B_Source_DB_r += 1

        if set_D == set_B:
            s = True
        else:
            s = False
            data_error_code = 'ERROR_TIP_009'
            data_error_description = Constant.ERROR_TIP_009
            data_error_status = s
            data_create_by = self.u_name
            self.pre_import_error_list(data_error_code, data_error_description,
                                              data_error_status, data_create_by)
        return s

    # =================================================

    # #@catch_exception
    def precondition_check_main(self):
        # Product_Info.Product 不能超過6位元
        # pre_con_101 = True if self.precondition_check_101() is True else False
        # print('pre_con_101', pre_con_101)

        # Product_Info.Tech_Process = Product_Info.Design_Rule
        pre_con_102 = True if self.precondition_check_102() is True else False
        print('pre_con_102', pre_con_102)

        # Tapeout_Info.Mask_Name 不能超過12位元
        pre_con_201 = True if self.precondition_check_201() is True else False
        print('pre_con_201', pre_con_201)

        # Tapeout_Info.BARCODE與Tapeout_Info.Mask_Name在同一行的值必須相同
        pre_con_202 = True if self.precondition_check_202() is True else False
        print('pre_con_202', pre_con_202)

        # Tapeout_Info.Mask_Name = Product_Info.Product + '-' + Tapeout_Info.Layer_Name + Tapeout_Info.Version
        pre_con_203 = True if self.precondition_check_203() is True else False
        print('pre_con_203', pre_con_203)

        # Tapeout_Info.File_Name 副檔名必須為 oas 或 gds
        pre_con_204 = True if self.precondition_check_204() is True else False
        print('pre_con_204', pre_con_204)

        # 1. Device_Info.Device_Name在相同時Source_DB不重複，不同的Source_DB可以重複
        # 2. 相同的Source_DB只能有一個FRAME
        pre_con_301 = True if self.precondition_check_301() is True else False
        print('pre_con_301', pre_con_301)

        # Device_Info.Device_Type等於Frame時，Device_Info.Device_Name須為FRAME
        # Device_Info.Device_Type等於Main時，Device_Info.Device_Name須為MP001~MP999
        pre_con_302 = True if self.precondition_check_302() is True else False
        print('pre_con_302', pre_con_302)

        # Device_Info，RT_X - LB_X <= 26000 ，RT_Y - LB_Y <= 33000
        # pre_con_303 = True if self.precondition_check_303() is True else False
        # print('pre_con_303', pre_con_303)

        # Device_Info.Device_Name and Layout_Info.Device_Name 依照PSM分開對應
        # Device_Info.與 Layout_Info 的 Device_Name 依照不同的PSM(N or Y)分開對應
        pre_con_304 = True if self.precondition_check_304() is True else False
        print('pre_con_304', pre_con_304)

        # Device_Info.Check_method = md5sum, len(value) = 32
        # Device_Info.Check_method = sha-512, len(value) = 128
        pre_con_305 = True if self.precondition_check_305() is True else False
        print('pre_con_305', pre_con_305)

        # CCD_Table : 0 <= Coor_X <= 152400 and 0 <= Coor_Y <= 152400
        pre_con_401 = True if self.precondition_check_401() is True else False
        print('pre_con_401', pre_con_401)

        # CCD_Table len(Item) <= 120
        pre_con_402 = True if self.precondition_check_402() is True else False
        print('pre_con_402', pre_con_402)

        # CCD_Table 0 <= CD_4X_nm <= 2000
        pre_con_403 = True if self.precondition_check_403() is True else False
        print('pre_con_403', pre_con_403)

        # Boolean_Info.Total_Bias 必須小於等於500
        pre_con_501 = True if self.precondition_check_501() is True else False
        print('pre_con_501', pre_con_501)

        # Check Boolean_Info.Mask_Name的值必須是Tapeout_Info.Mask_Name有的
        pre_con_502 = True if self.precondition_check_502() is True else False
        print('pre_con_502', pre_con_502)

        # Boolean_Info 當Mask_Name相同時，Tone也相同
        pre_con_503 = True if self.precondition_check_503() is True else False
        print('pre_con_503', pre_con_503)

        # Check Device_Info & Boolean_Info，Source_DB & Boolean_Index
        pre_con_504 = True if self.precondition_check_504() is True else False
        print('pre_con_504', pre_con_504)

        # 1. Layout_Info.Device_Name,X1,Y1數量需與大於等於Device_Info中DB最多的數量
        # 2. PSM與非PSM分開計算(NY都要取一次最大的)
        # 3. 在不同DB內Device可以重複
        pre_con_601 = True if self.precondition_check_601() is True else False
        print('pre_con_601', pre_con_601)

        pre_check_605 = True if self.precondition_check_605() is True else False
        print('pre_con_605', pre_check_605)

        # Layout_Info.X1、Y1 ，13000 > X1 > -13000，16500 > Y1 > -16500
        # pre_con_602 = True if self.precondition_check_602() is True else False
        # print('pre_con_602', pre_con_602)

        # 1. Layout_Info.Array_X、Array_Y，數值須為正整數
        # 2. Layout_Info.Pitch_X、Pitch_Y，數值須為正數
        # 3. Layout_Info.Pitch_X、Pitch_Y，13000 > Pitch_X > -13000，16500 > Pitch_Y > -16500
        # pre_con_603 = True if self.precondition_check_603() is True else False
        # print('pre_con_603', pre_con_603)

        # Layout_Info X1, Y1
        # Device_Info RT_X, LB_X, RT_Y, LB_Y
        # 13000 > X1 + -Ldx/2 > -13000 , Ldx = RT_X - LB_X
        # 16500 > Y1 + -Ldy/2 > -16500 , Ldy = RT_Y - LB_Y
        # pre_con_604 = True if self.precondition_check_604() is True else False
        # print('pre_con_604', pre_con_604)

        # Device_Info.Boolean_Index 與 Boolean_Info.Boolean_Index 需對應
        # pre_con_05 = self.precondition_check_05(upload_path, u_name)

        # 1. Boolean_Info.Source_DB 與 Device_Info.Source_DB 的DB編號需對應，只有數值對應即可，順序與數量無關
        # 2. PSM與非PSM一起計算
        # pre_con_09 = self.precondition_check_09(upload_path, u_name)

        # pre_con_05, pre_con_09 取消驗證(保留)
        # pre_con_07 與 pre_con_06 合併
        # i = pre_con_101 and pre_con_102 and pre_con_201 and pre_con_202 and pre_con_203 and \
        #     pre_con_204 and pre_con_301 and pre_con_302 and pre_con_303 and pre_con_304 and \
        #     pre_con_305 and pre_con_401 and pre_con_402 and pre_con_403 and pre_con_501 and \
        #     pre_con_502 and pre_con_503 and pre_con_504 and pre_con_601 and pre_con_602 and \
        #     pre_con_603 and pre_con_604

        # pre_con_303, pre_con_602,pre_con_603,pre_con_604 暫時移除
        i = pre_con_102 and pre_con_201 and pre_con_202 and pre_con_203 and \
            pre_con_204 and pre_con_301 and pre_con_302 and pre_con_304 and \
            pre_con_305 and pre_con_401 and pre_con_402 and pre_con_403 and pre_con_501 and \
            pre_con_502 and pre_con_503 and pre_con_504 and pre_con_601 and pre_check_605

        print(i)

        if i:
            return True
        else:
            return False


class ToolService(BaseService):
    def check_data_exist(self, u_name, upload_path):
        import_set_all = setting.objects.filter(enable=1).order_by('sheet_no')
        print(import_set_all.count())
        set_sheet_name = setting.objects.all().values('sheet_name')
        set_column_name = setting.objects.all().values('column_name')
        set_row = setting.objects.all().values('row')
        set_column = setting.objects.all().values('column')
        set_required = setting.objects.all().values('required_field')

        i = import_set_all.count()
        x = 0
        while x < i:
            sheet_name_value = set_sheet_name[x]['sheet_name']
            column_name_value = set_column_name[x]['column_name']
            row_value = set_row[x]['row']
            column_value = set_column[x]['column']
            required = set_required[x]['required_field']

            df = pd.read_excel(upload_path, sheet_name=sheet_name_value)
            excel_row = len(df) - 1
            k = row_value
            if excel_row == k:
                required_dict = setting.objects.filter(enable=1, sheet_name=sheet_name_value).order_by(
                    'column_no').values('required_field')
                for val in required_dict:
                    if val['required_field'] == 1:
                        data_error_code = 'ERROR_TIP_NULL'
                        data_error_description = str(Constant.ERROR_TIP_NULL % (sheet_name_value, column_name_value))
                        data_error_status = False
                        data_create_by = u_name
                        ToolService().pre_import_error_list(data_error_code,
                                                                   data_error_description,
                                                                   data_error_status,
                                                                   data_create_by)
                        return False

            while excel_row > k:
                excel_data = str(df.iloc[excel_row, column_value])
                if (excel_data == 'nan' or excel_data is None or excel_data == '') and (
                        required == 1 or required == '1'):
                    print(False)
                    data_error_code = 'ERROR_TIP_NULL'
                    data_error_description = str(Constant.ERROR_TIP_NULL % (sheet_name_value, column_name_value))
                    data_error_status = False
                    data_create_by = u_name
                    ToolService().pre_import_error_list(data_error_code,
                                                               data_error_description,
                                                               data_error_status,
                                                               data_create_by)
                    return False
                print(True, required, sheet_name_value, column_name_value, excel_row, column_value, excel_data)
                excel_row -= 1
            x += 1
        return True

    def create_tip_no(self, u_name):
        # tip_no = TP + year(019,020,021) + auto_hex(0001,0002,0003)
        year = str(time.localtime().tm_year)[1:4]
        new_id = tip_no_create()
        new_id.save()
        hex_new_id = str(hex(new_id.id))[2:].zfill(4)
        new_tip_no = Constant.TIP_NO_PREFIX + year + hex_new_id

        add_tip_no = tip_no_create.objects.get(id=new_id.id)

        add_tip_no.tip_no = new_tip_no
        add_tip_no.create_by = u_name
        add_tip_no.create_date = getDateStr()
        add_tip_no.create_time = getMilliSecond()

        tooling_models().add_tip_no(add_tip_no)

        return (new_tip_no)

    # EK_Harry.Lee 插入主表 import_list 原 upload
    def import_list(self, new_tip_no, filename, old_filename, data_create_by, data_create_name, error_status,
                    check_status, status):

        add_import_list = import_list(tip_no=new_tip_no,
                                      file_name=filename,
                                      old_file_name=old_filename,
                                      create_by=data_create_by,
                                      create_name=data_create_name,
                                      error_status=error_status,
                                      check_status=check_status,
                                      status=status,
                                      create_date=getDateStr(),
                                      create_time=getMilliSecond())

        add_import_list.save()

        return ()

    def import_data_temp(self, u_name, data_id, data_tip_no, data_sheet_name, data_column_name,
                    data_import_data, data_import_data_status, data_data_key):

        add_import_data_temp = import_data_temp(tip_no=data_tip_no,
                                      sheet_name=data_sheet_name,
                                      column_name=data_column_name,
                                      import_data=data_import_data,
                                      import_data_status=int(data_import_data_status),
                                      create_by=u_name,
                                      create_date=getDateStr(),
                                      create_time=getMilliSecond())
        if data_id:
            add_import_data_temp.id = data_id

        if data_data_key:
            add_import_data_temp.data_key = data_data_key

        add_import_data_temp.save()

        return add_import_data_temp.id

    def pre_import_error_list(self, data_error_code, data_error_description,
                                     s, data_create_by):

        _o = import_error_list()

        _o.import_data_id = 0
        _o.tip_no = ''
        # _o.data_sheet_name = data_sheet_name
        # _o.data_column_name = data_column_name
        _o.import_data = ''
        _o.error_code = data_error_code
        _o.error_description = data_error_description
        _o.error_type = 1
        _o.is_delete = s
        _o.create_by = data_create_by
        _o.create_date = getDateStr()
        _o.create_time = getMilliSecond()

        _o.save()

    def import_error_list(self, data_import_id, import_data_id, data_tip_no, data_import_data, required_field_value,
                          data_sheet_name, data_column_name, parent_id_value, data_regex_no, data_error_code,
                          data_error_description, data_error_type, data_error_status, data_create_by
                          , validate_value):
        # regex python 2 js
        if data_regex_no and data_regex_no > 0:
            validate_value = Constant.TOOLING_FORM_REGEX_PYTHON2JS[validate_value]

        # replace {} to '',',' to ' or '
        if data_error_description:
            data_error_description = data_error_description.replace('{', '').replace('}', '').replace("', '", "' or '")
            # if validate_value:
        #    validate_value = validate_value.replace("'","\\'")
        ins_error_log = import_error_list(import_id=data_import_id,
                                          import_data_id=import_data_id,
                                          tip_no=data_tip_no,
                                          sheet_name=data_sheet_name,
                                          column_name=data_column_name,
                                          import_data=data_import_data,
                                          required_field=required_field_value,
                                          parent_id=parent_id_value,
                                          regex_no=data_regex_no,
                                          error_code=data_error_code,
                                          error_description=data_error_description,
                                          error_type=data_error_type,
                                          is_delete=data_error_status,
                                          validate_value=validate_value,
                                          create_by=data_create_by,
                                          create_date=getDateStr(),
                                          create_time=getMilliSecond())

        ins_error_log.save()

    # EK_harry.Lee
    def import_error_list_is_delete(self, u_name):

        import_error_list.objects.filter(create_by=u_name,
                                                error_type=1,
                                                import_data_id=0).update(is_delete=1)

        return ()

    def import_error_list_is_delete_import_data(self, req_tip_no, u_name):

        import_error_list.objects.filter(tip_no=req_tip_no, create_by=u_name).update(update_by=u_name,
                                                                          update_date=getDateStr(),
                                                                          update_time=getMilliSecond(),
                                                                          is_delete=1)
        return ()

    def import_check_list_is_delete_import_data(self, req_tip_no, u_name):

        import_check_list.objects.filter(tip_no=req_tip_no, create_by=u_name).update(update_by=u_name,
                                                                          update_date=getDateStr(),
                                                                          update_time=getMilliSecond(),
                                                                          is_delete=1)
        return ()

    # EK_harry.Lee
    def pre_import_list_is_delete(self, u_name):
        import_list.objects.filter(create_by=u_name,
                              tip_no='').update(update_by=u_name,
                                                update_date=getDateStr(),
                                                update_time=getMilliSecond(),
                                                is_delete=1)

    def import_list_is_delete(self, tip_no, u_name):
        import_list.objects.filter(tip_no=tip_no, create_by=u_name).update(update_by=u_name,
                                                    update_date=getDateStr(),
                                                    update_time=getMilliSecond(),
                                                    is_delete=1)

    def import_list_check_status(self, new_tip_no, error_status, check_status, status):

        import_list.objects.filter(tip_no=new_tip_no).update(error_status=error_status, check_status=check_status,
                                                             status=status)

        return ()

    def check_regex(self, regex_no_value, regex_str):
        s = 0
        global regex_error_code, error_message, regex
        print(switch(str(regex_no_value)))
        print(type(switch(str(regex_no_value))))
        for case in switch(str(regex_no_value)):
            # Product_Info Tooling_Version
            if case('1'):
                regex = "(?!000)\d{3}"
                pattern = re.compile(regex)
                m = pattern.fullmatch(regex_str)
                if (m is not None) and (len(regex_str) == 3) and (regex_str != '000'):
                    s = 1
                else:
                    s = 0
                    regex_error_code = 'ERROR_REGEX_001'
                    error_message = str(Constant.ERROR_REGEX_001 % regex_str)
                break
            # Tapeout_Info Grade
            if case('2'):
                regex = "[A-Z]{1}"
                pattern = re.compile(regex)
                m = pattern.fullmatch(regex_str)
                if (m is not None) and (len(regex_str) == 1):
                    s = 1
                else:
                    s = 0
                    regex_error_code = 'ERROR_REGEX_002'
                    error_message = str(Constant.ERROR_REGEX_002 % regex_str)
                break
            # Device_Info Source_DB
            # Boolean_Info Source_DB
            if case('3'):
                regex = "DB[1-9]\d{0,4}"
                pattern = re.compile(regex)
                m = pattern.fullmatch(regex_str)
                if (m is not None) and (len(regex_str) <= 7):
                    s = 1
                else:
                    s = 0
                    regex_error_code = 'ERROR_REGEX_003'
                    error_message = str(Constant.ERROR_REGEX_003 % regex_str)
                break
            # Device_Info Boolean_Index
            if case('4'):
                regex = "Boolean(?!000)\d{3}"
                pattern = re.compile(regex)
                m = pattern.fullmatch(regex_str)
                if (m is not None) and (len(regex_str) == 10):
                    s = 1
                else:
                    s = 0
                    regex_error_code = 'ERROR_REGEX_004'
                    error_message = str(Constant.ERROR_REGEX_004 % regex_str)
                break
            # Device_Info Shrink
            if case('5'):
                regex = "([1-9]\d{0,1}|100)"
                pattern = re.compile(regex)
                m = pattern.fullmatch(regex_str)
                if (m is not None) and (len(regex_str) <= 3) and (int(regex_str) <= 100):
                    s = 1
                else:
                    s = 0
                    regex_error_code = 'ERROR_REGEX_005'
                    error_message = str(Constant.ERROR_REGEX_005 % regex_str)
                break
            # MLM_Info_Field_Name
            if case('6'):
                regex = "E[1-9]{1}"
                pattern = re.compile(regex)
                m = pattern.fullmatch(regex_str)
                if (m is not None) and (len(regex_str) == 2):
                    s = 1
                else:
                    s = 0
                    regex_error_code = 'ERROR_REGEX_006'
                    error_message = str(Constant.ERROR_REGEX_006 % regex_str)
                break

            # Tapeout_Info_Version
            if case('7'):
                regex = "[A-Z]{1}[1-9A-Z]{1}"
                pattern = re.compile(regex)
                m = pattern.fullmatch(regex_str)
                if (m is not None) and (len(regex_str) == 2):
                    s = 1
                else:
                    s = 0
                    regex_error_code = 'ERROR_REGEX_007'
                    error_message = str(Constant.ERROR_REGEX_007 % regex_str)
                break
            # if case('0'):
            #
            #     break

        if s == 1:
            return s
        else:
            return s, regex_error_code, error_message, regex

    def data_key(self, df, sheet_name_value, k):
        for case in switch(sheet_name_value):
            if case('Product_Info'):
                data_data_key = str_strip(df.iloc[k, 2])
                break
            if case('Tapeout_Info'):
                data_data_key = str_strip(df.iloc[k, 3])
                break
            if case('Device_Info'):
                data_data_key = str_strip(df.iloc[k, 0]) + "_" + str_strip(df.iloc[k, 3]) + "_" + \
                                str_strip(df.iloc[k, 4]) + "_" + str_strip(df.iloc[k, 1])
                break
            if case('CCD_Table'):
                data_data_key = str_strip(df.iloc[k, 0])
                break
            if case('Boolean_Info'):
                data_data_key = str_strip(df.iloc[k, 2]) + "_" + str_strip(df.iloc[k, 0]) + "_" + \
                                str_strip(df.iloc[k, 1])
                break
            if case('Layout_Info'):
                data_data_key = str_strip(df.iloc[k, 0]) + "_" + str_strip(df.iloc[k, 1])
                break
            # if case('MLR_Info'):
            if case('MLM_Info'):
                data_data_key = str_strip(df.iloc[k, 0])
                break

        return data_data_key

    def check_sheet_column_name(self, upload_path):
        import_set_all = setting.objects.filter(enable=1).order_by('sheet_no', 'column_no')
        set_sheet_name = setting.objects.filter(enable=1).order_by('sheet_no', 'column_no').values('sheet_name')
        set_column_name = setting.objects.filter(enable=1).order_by('sheet_no', 'column_no').values('column_name')
        set_row = setting.objects.filter(enable=1).order_by('sheet_no', 'column_no').values('row')
        set_column = setting.objects.filter(enable=1).order_by('sheet_no', 'column_no').values('column')

        i = import_set_all.count()

        x = 0
        while x < i:
            sheet_name_value = set_sheet_name[x]['sheet_name']
            column_name_value = set_column_name[x]['column_name']
            row_value = set_row[x]['row']
            column_value = set_column[x]['column']

            df = pd.read_excel(upload_path, sheet_name=sheet_name_value)
            data_column_name = str_strip(df.iloc[row_value, column_value])
            print(x, column_name_value, data_column_name)
            if column_name_value == data_column_name:
                s = True
            else:
                s = False
                return s
            x += 1
        return s

    # 括號匹配
    def check_valid(self, s):
        pars = [None]
        # 使用dict来存放括号的匹配关系
        parmap = {')': '(', ']': '['}
        for c in s:
            if c in parmap:
                # 如果正要入栈的是右括号，而栈顶元素不是能与之消去的相应左括号，该输入字符串一定是无效的
                if parmap[c] != pars.pop():
                    return False
            else:
                pars.append(c)
        return len(pars) == 1

    # operation 字串重組
    def reorganization(self, s):
        i = 0
        valid_list = []  # valid list
        valid_site_list = []  # valid site
        op_str_list = []  # operation_str list
        valid = ['(', ')']

        # 將括號從字串取出,並取得括號位置
        for c in s:
            op_str_list.append(c)
            i += 1
            if c in valid:
                valid_list.append(c)
                valid_site_list.append(i - 1)

        # 將括號組成字串
        valid_str = ''  # 括號字串
        for h in valid_list:
            valid_str += h

        return valid_site_list, valid_str

    # 取第一組括號
    def mid_valid(self, op_s):
        length = len(op_s)
        mid_value = int(length / 2)
        mid_start = op_s[mid_value - 1]
        mid_end = op_s[mid_value]

        return mid_start, mid_end

    # 正則
    def operation_str_regex(self, slice_s):
        op_regex = "[A-Z]{1}[0-9]{1,3}[;][0-9]{1,3}"
        op_regex_2 = "[\[]DB[1-9]{1}[]][A-Z]{1}[0-9]{1,3}[;][0-9]{1,3}"

        if slice_s.find('DB') == -1:
            pattern = re.compile(op_regex)
        else:
            pattern = re.compile(op_regex_2)

        m = pattern.fullmatch(slice_s)
        # print(slice_s, m, m is not None)
        return m is not None

    def check_operation(self, operation_str):

        op_val = operation_str
        reo_result = self.reorganization(op_val)[1]
        c = int(len(reo_result)) / 2

        if not self.check_valid(reo_result):
            s = 0
            operation_error_code = 'ERROR_OPERATION_001'
            error_message = str(Constant.ERROR_OPERATION_001 % operation_str)
            return s, operation_error_code, error_message

        i = 0
        while i < c:
            # 打印驗證字串
            print(op_val)
            # print('valid_check =', valid_check(test(operation_str)[1]))

            # 使用mid()取得start, end
            rr = self.reorganization(op_val)[0]
            # print('rr type = ', type(rr))
            # print(mid(rr))

            mid_val = self.mid_valid(rr)
            # print('100', test(operation_str)[0], test(operation_str)[1])
            # print(mid_val)
            # print(mid_val[0], mid_val[1])

            op_str_slice = op_val[mid_val[0]: mid_val[1] + 1]
            # print(op_str_slice, op_str_slice.find('+'), op_str_slice.count('+'))

            # 切片後正則
            if op_str_slice.count('+') == 0:
                regex_start = 0
                regex_end = len(op_str_slice) - 1
                slice_str = op_str_slice[regex_start + 1:regex_end]
                self.operation_str_regex(slice_str)

                if self.operation_str_regex(slice_str):
                    print(i, True)
                    s = 1
                    return s
                else:
                    print(False)
                    break

            elif op_str_slice.count('+') == 1:
                regex_start = 0
                regex_mid = op_str_slice.find('+')
                regex_end = len(op_str_slice) - 1

                slice_1 = op_str_slice[regex_start + 1:regex_mid]
                slice_2 = op_str_slice[regex_mid + 1:regex_end]
                # print(slice_1, slice_2, slice_1.find('DB'))
                slice_1.find('DB')

                if self.operation_str_regex(slice_1) and self.operation_str_regex(slice_2):
                    op_s_rep = 'L0;0'
                    op_val = op_val.replace(op_str_slice, op_s_rep)
                    i += 1
                else:
                    s = 0
                    operation_error_code = 'ERROR_OPERATION_001'
                    error_message = str(Constant.ERROR_OPERATION_001 % operation_str)
                    return s, operation_error_code, error_message
            else:
                s = 0
                operation_error_code = 'ERROR_OPERATION_001'
                error_message = str(Constant.ERROR_OPERATION_001 % operation_str)
                return s, operation_error_code, error_message
        s = 1
        return s

    @transaction.atomic
    def  update_import_data(self, req_id, import_data_id, req_tip_no, req_parent_id, req_regex_no, req_import_data):

        print('para =', req_id, import_data_id, req_tip_no, req_parent_id, req_regex_no, req_import_data)
        set_regex_no = req_regex_no
        regex_str = req_import_data

        # 判斷字典或正則
        if req_parent_id == 0 or req_parent_id == '0' or req_parent_id == '':
            check_regex_result = self.check_regex(set_regex_no, regex_str)
            print('check_regex_result =', check_regex_result)
            if check_regex_result == 1:
                data_import_data_status = 1
        else:
            parent = dict.objects.filter(parent_id=req_parent_id).values('value')
            parent_c = parent.count()
            j = 0
            parent_set = set()
            while j < parent_c:
                parent_set.add(parent[j]['value'])
                j += 1
            df_set = set()
            df_set.add(req_import_data)
            isdisjoint_result = parent_set.isdisjoint(df_set)

            if str(not isdisjoint_result) == 'True':
                data_import_data_status = 1
            else:
                data_import_data_status = 0

        # update import data table
        _o = import_data_temp.objects.get(id=import_data_id)
        data_key = _o.data_key
        column_name = _o.column_name.lower()
        sheet = _o.sheet_name.lower()

        data_key_list = data_key.split('_')
        if _o:
            _o.import_data = req_import_data
            _s = tooling_models()
            _s.upd_import_data(_o)

        # update error message table
        print('error', req_id, req_import_data, data_import_data_status)
        import_error_list.objects.filter(id=req_id).update(
            import_data=req_import_data,
            is_delete=data_import_data_status,
            update_date=getDateStr(),
            update_time=getMilliSecond())

        # update boolean_info table
        if sheet == 'product_info':
            table = product_info_temp.objects.filter(tip_no=req_tip_no,
                                             product=data_key_list[0])
            table.update(**{column_name: req_import_data})

        if sheet == 'tapeout_info':
            table = tapeout_info_temp.objects.filter(tip_no=req_tip_no,
                                             mask_name=data_key_list[0])
            table.update(**{column_name: req_import_data})

        if sheet == 'device_info':
            table = device_info_temp.objects.filter(tip_no=req_tip_no,
                                               psm=data_key_list[0],
                                               device_name=data_key_list[1],
                                               boolean_index=data_key_list[2],
                                               source_db=data_key_list[3])
            table.update(**{column_name: req_import_data})

        if sheet == 'ccd_table':
            table = ccd_table_temp.objects.filter(tip_no=req_tip_no,
                                          no=data_key_list[0])
            table.update(**{column_name: req_import_data})

        if sheet == 'boolean_info':
            table = boolean_info_temp.objects.filter(tip_no=req_tip_no,
                                             mask_name=data_key_list[0],
                                             boolean_index=data_key_list[1],
                                             source_db=data_key_list[2])
            table.update(**{column_name: req_import_data})

        if sheet == 'layout_info':
            table = layout_info_temp.objects.filter(tip_no=req_tip_no,
                                            psm=data_key_list[0],
                                            device_name=data_key_list[1])
            table.update(**{column_name: req_import_data})

        if sheet == 'mlm_info':
            table = mlm_info_temp.objects.filter(tip_no=req_tip_no,
                                         no=data_key_list[0])
            table.update(**{column_name: req_import_data})

        return 1

    def update_import_error_message_log_status(self, req_tip_no):

        import_data_all = import_error_list.objects.filter(tip_no=req_tip_no, is_delete=0).order_by('id')
        status_c = import_data_all.count()
        print('status_c =', status_c, req_tip_no)

        if status_c == 0:
            error_status = 0
            check_status = 0
            status = 2
            self.import_list_check_status(req_tip_no, error_status, check_status, status)

        return 1

    @transaction.atomic
    def update_import_data_operation(self, req_id, import_data_id, req_tip_no, req_import_data):

        # update import data table
        _o = import_data_temp.objects.get(id=import_data_id)
        data_key = _o.data_key
        data_key_list = data_key.split('_')

        if _o:
            _o.import_data = req_import_data
            _s = tooling_models()
            _s.upd_import_data(_o)

        # update error message table
        import_error_list.objects.filter(id=req_id).update(
            import_data=req_import_data,
            is_delete=1,
            update_date=getDateStr(),
            update_time=getMilliSecond())

        # update boolean_info table
        boolean = boolean_info_temp.objects.get(tip_no=req_tip_no,
                                           mask_name=data_key_list[0],
                                           boolean_index=data_key_list[1],
                                           source_db=data_key_list[2])
        boolean.operation = req_import_data
        boolean.save()

        return 1

    #@catch_exception
    def check_ACK(self, upload_path, u_id):

        df = pd.read_excel(upload_path, sheet_name=Tooling_Form_Sheet['Sheet_01'])
        P_Product_r = setting.objects.filter(sheet_name=Tooling_Form_Sheet['Sheet_01'],
                                             column_name='Product').values('row')[0]['row'] + 1
        P_Product_l = setting.objects.filter(sheet_name=Tooling_Form_Sheet['Sheet_01'],
                                             column_name='Product').values('column')[0]['column']

        P_Product = str_strip(df.iloc[P_Product_r, P_Product_l])

        P_Tooling_Version_r = setting.objects.filter(sheet_name=Tooling_Form_Sheet['Sheet_01'],
                                                     column_name='Tooling_Version').values('row')[0]['row'] + 1
        P_Tooling_Version_l = setting.objects.filter(sheet_name=Tooling_Form_Sheet['Sheet_01'],
                                                     column_name='Tooling_Version').values('column')[0]['column']

        P_Tooling_Version = str_strip(df.iloc[P_Tooling_Version_r, P_Tooling_Version_l])

        P_Customer_r = setting.objects.filter(sheet_name=Tooling_Form_Sheet['Sheet_01'],
                                                     column_name='Customer').values('row')[0]['row'] + 1
        P_Customer_l = setting.objects.filter(sheet_name=Tooling_Form_Sheet['Sheet_01'],
                                                     column_name='Customer').values('column')[0]['column']

        P_Customer = str_strip(df.iloc[P_Customer_r, P_Customer_l])

        status = 0
        tip_no = ''
        product_info_list = product_info.objects.filter(customer=P_Customer, tooling_version=P_Tooling_Version,
                                                        product=P_Product, is_delete='0')

        if product_info_list:
            status = 2
            tip_no = product_info_list[0].tip_no

        else:

            product_info_temp_list = product_info_temp.objects.filter(customer=P_Customer,
                                                                      tooling_version=P_Tooling_Version,
                                                                      product=P_Product, is_delete='0')

            if product_info_temp_list:
                status = 1
                tip_no = product_info_temp_list[0].tip_no

        return status, tip_no






class switch(object):

    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args:  # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False


@ProxyFactory(InvocationHandler)
class tooling_models(BaseService):

    def add_tip_no(self, add_tip_no):
        add_tip_no.save()

    def add_upload(self, add_upload):
        add_upload.save()

    def save_import_data(self, add_import_data):
        add_import_data.save()

    # insert data
    def add_tooling(self, tooling):
        pass

    # update data
    def upd_import_data(self, import_data):
        import_data.save()


def upd_tip_no_status(tip_no, status: int):
    """更新tooling_upload的status"""
    if tip_no:
        import_list.objects.filter(tip_no=tip_no, is_delete=0, status__lt=status).update(status=status)
        return True
    else:
        return False


def str_strip(data):
    data = str(data).strip()
    return data


def float_strip(data):
    data = float(str(data).strip())
    return data


def int_strip(data):
    data = int(str(data).strip())
    return data
