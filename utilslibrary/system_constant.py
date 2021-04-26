# -*- coding: utf-8 -*-
"""存放系统常量
"""
from Mask_DP.settings import GLOBAL_PARAM


class Constant():
    # current user flag in session
    SESSION_CURRENT_USER = 'MASK_DP_SESSION_CURRENT_USER'
    SESSION_CURRENT_USER_LOGINNAME = 'MASK_DP_SESSION_CURRENT_USER_LOGINNAME'
    SESSION_CURRENT_USER_ID = 'MASK_DP_SESSION_CURRENT_USER_ID'
    SESSION_CURRENT_USER_PERMISSION_LIST = 'MASK_DP_SESSION_CURRENT_USER_PERMISSION_LIST'
    SESSION_CURRENT_USER_PERMISSION_MENU_ID_LIST = 'MASK_DP_SESSION_CURRENT_USER_PERMISSION_MENU_ID_LIST'
    SESSION_CURRENT_USER_PERMISSION_DICT_DATARULE_ID_LIST = 'MASK_DP_SESSION_CURRENT_USER_DICT_PERMISSION_DATARULE_ID_LIST'

    # would insert into db of operations
    LOG_DB_OPERATIONS_METHOD = ['add_', 'upd_', 'del_']

    # Pre-condition error message
    ERROR_TIP_NO_DATA = '%s no data !'
    ERROR_TIP_NULL = '[%s].[%s] is required field, Please provide data'

    # Product_Info
    ERROR_TIP_1011 = 'Product_Info.Product must be less than 6 bits'
    ERROR_TIP_1012 = 'The Version of Product already exists'
    ERROR_TIP_1021 = 'Product_Info.Tech_Process must be the same as Product_Info.Design_Rule'

    # Tapeout_Info
    ERROR_TIP_2011 = 'Tapeout_Info.Mask_Name must be less than 12 bits'
    ERROR_TIP_2021 = 'Tapeout_Info.barcode must be the same as Tapeout_Info.mask_name'
    ERROR_TIP_2031 = 'Tapeout_Info.Mask_Name format error'
    ERROR_TIP_2041 = 'Filename Extension error. Correct should be oas or gds'

    # Device_Info
    ERROR_TIP_3011 = 'Device_Info.Device_Name do not repeat in the same DB and vice versa'
    ERROR_TIP_3021 = 'IF Device_Info.Device_Type is Frame. Device_Name Correct should be FRAME'
    ERROR_TIP_3022 = 'IF Device_Info.Device_Type is Main. Device_Name Correct should be MP001~MP999'
    ERROR_TIP_3031 = '[RT_X - LB_X <= 26000] or [RT_Y - LB_Y <= 33000] out of range'
    ERROR_TIP_3041 = 'Incorrect PSM value at row %s in %s. You provide data is %s'
    ERROR_TIP_3051 = 'Device_Info.value length error'

    # CCD_Table
    ERROR_TIP_4011 = '[0 <= Coor_X <= 152400] or [0 <= Coor_Y <= 152400] out of range'
    ERROR_TIP_4021 = 'CCD_Table.Item must be less than 120 bits'
    ERROR_TIP_4031 = '[0 <= CD_4X_nm <= 2000] out of range'

    # Boolean_Info
    ERROR_TIP_5011 = 'total bias = %s, max setting is 500'
    ERROR_TIP_5021 = 'Tapeout_Info.Mask_Name and Boolean.Mask_Name need to correspond'
    ERROR_TIP_5031 = 'Same Mask_name but different tone at row %s'
    ERROR_TIP_5041 = 'Boolean_Info.(Source_DB+Boolean_Index) and Device_Info.(Source_DB+Boolean_Index) need to \
                    correspond'

    # Layout_Info
    ERROR_TIP_6011 = 'Layout_Info.Device_Name, X1, Y1 number of rows must be greater than or equal to the maximum \
                    number of DB rows in Device_Info,PSM(N,Y) culated separately'
    ERROR_TIP_6021 = '[13000 > X1 > -13000] or [16500 > Y1 > -16500] out of range'
    ERROR_TIP_6031 = '[13000 > Layout_Info.Pitch_X > -13000] or [16500 > Layout_Info.Pitch_Y > -16500] out of range'
    ERROR_TIP_6032 = 'Layout_Info.Pitch_X,Pitch_Y must be positive integer，Array_X、Array_Y must be integer'
    ERROR_TIP_6033 = 'Layout_Info.Array_X,Array_Y,Pitch_X,Pitch_Y Incomplete data provided'
    ERROR_TIP_6041 = 'X1 or Y1 out of boundary at row %s'
    ERROR_TIP_6051 = 'The device %s in Device info does not match in Layout info and Device info'

    # MLR_Info
    # MLM_Info
    # ERROR_TIP_005 = 'Device_Info.Boolean_Index and Boolean_Info.Boolean_Index need to correspond'
    # ERROR_TIP_009 = 'Boolean_Info.Source_DB and Device_Info.Source_DB need to correspond'
    # ERROR_TIP_021 = 'Device_Info.Device_Name and Layout_Info.Device_Name need to correspond'
    # ERROR_TIP_023 = 'There can be only one frame per DB'
    # ERROR_TIP_027 = 'Tapeout_Info.Mask_Name not define'
    # ERROR_TIP_028 = 'Boolean_Info.Mask_Name not define'
    # ERROR_TIP_029 = ''

    ERROR_OPERATION_001 = '%s format not match'

    ERROR_TIP_100 = 'The product in the uploaded file is different from the product or version of tip_no, please re-upload!'
    ERROR_TIP_200 = 'The file structure is wrong,please download the template again!'
    ERROR_TIP_300 = 'Pre-condition failed, please check tooling form'
    ERROR_TIP_301 = 'Data type error'
    ERROR_TIP_400 = 'File verification failed,Please check the file error information'
    CHECK_TIP_000 = 'File data comparison finished, please check the data comparison results'

    # Check null
    ERROR_NULL_001 = 'This is required field, Please provide data'

    # Check dict error
    ERROR_DICT_001 = 'The value you provided is : %s, Correct should be : %s'

    # Check regex error
    ERROR_REGEX_001 = 'The value you provided is : %s, Correct should be : 001 ~ 999'
    ERROR_REGEX_002 = 'The value you provided is : %s, Correct should be : A~Z'
    ERROR_REGEX_003 = 'The value you provided is : %s, Correct should be : DB1~DB99999'
    ERROR_REGEX_004 = 'The value you provided is : %s, Correct should be : Boolean001~Boolean999'
    ERROR_REGEX_005 = 'The value you provided is : %s, Correct should be : 1~100'
    ERROR_REGEX_006 = 'The value you provided is : %s, Correct should be : E1~E9'
    ERROR_REGEX_007 = 'The value you provided is : %s, Correct should be : A1~Z1'

    ERROR_RE_001 = 'The value you provided is : %s, Correct should be : %s'

    # fracture error
    FRACTURE_CONNOT_RE_GENERATE_FILE = "Fracture complete,cannot regerate file"
    FRACTURE_SOURCE_DB_ERROR = "source db error!"
    FRACTURE_SOURCE_DB_COUNT_ERROR = "source db count error!"
    FRACTURE_TOTAL_BIAS_ERROR_IN_MDT_TABLE = "total bias error in mdt table"
    FRACTURE_CAD_LAYER_NOT_DEFINE_IN_TOOLING_FORM = "cad layer [{}] not define in tooling form!"
    FRACTURE_WRITER_ERROR = "writer type error!"

    # Tip No prefix
    TIP_NO_PREFIX = 'TP'

    # tooling form download dir
    TOOLING_FORM_DOWNLOAD_DIR = 'Mask_DP_download/'
    # linux download path
    # TOOLING_FORM_DOWNLOAD_DIR = '/usr/Mask_DP_download/'

    # tooling form SOP template
    TOOLING_FORM_SOP_TEMPLATE = 'Mask_DP_SOP.pdf'
    # tooling form template
    TOOLING_FORM_TEMPLATE = 'Mask_DP_Tooling_Form_Template.xlsx'

    # regex python to javascript
    TOOLING_FORM_REGEX_PYTHON2JS = {"(?!000)\d{3}": "/^(?!000)\d{3}$/",
                                    "([1-9]\d{0,1}|100)": "/^([1-9]\d{0,1}|100)$/",
                                    "Boolean(?!000)\d{3}": "/^Boolean(?!000)\d{3}$/",
                                    "[A-Z]{1}[1-9A-Z]{1}": "/^[A-Z]{1}[1-9A-Z]{1}$/",
                                    "DB[1-9]\d{0,4}": "/^DB[1-9]\d{0,4}$/",
                                    "E[1-9]{1}": "/^E[1-9]{1}$/",
                                    "[A-Z]{1}": "/^[A-Z]{1}$/"}

    JDV_LOT_LIST_SOP_TEMPLATE = 'Jdv_Lot_List_Sop_Template.pdf'
    JDV_JB_TEMPLATE_TYPE = 'Frame Fracture Fiducial JB'

    # INFO_TREE Dictionary type
    INFO_TREE_DICT_TYPE_NAME = "Info_Tree"
    # FLOOR PLAN Dictionary type
    FLOOR_PLAN_DICT_TYPE_NAME = "Floor_Plan"
    # Script_Template_File
    SCRIPT_TEMPLATE_FILE_DICT_TYPE = "Script_Template_File"
    SCRIPT_TEMPLATE_VSB12i_DB1_FILE_TYPE = "Fracture_VSB12i_DB1"
    SCRIPT_TEMPLATE_VSB12i_DB1_DB2_FILE_TYPE = "Fracture_VSB12i_DB1_DB2"
    SCRIPT_TEMPLATE_VSB12_DB1_FILE_TYPE = "Fracture_VSB12_DB1"
    SCRIPT_TEMPLATE_VSB12_DB1_DB2_FILE_TYPE = "Fracture_VSB12_DB1_DB2"
    SCRIPT_TEMPLATE_MODE5_DB1_FILE_TYPE = "Fracture_Mode5_DB1"
    SCRIPT_TEMPLATE_MODE5_DB1_DB2_FILE_TYPE = "Fracture_Mode5_DB1_DB2"

    # VSB12i Dictionary type
    FRACTURE_VSB12I_DICT_TYPE_NAME = "Fracture_VSB12i"
    FRACTURE_VSB12_DICT_TYPE_NAME = "Fracture_VSB12"
    # VSB12i XOR Dictionary type
    FRACTURE_VSB12I_XOR_DICT_TYPE_NAME = "Fracture_VSB12i_XOR"

    # host_file dict type
    FRACTURE_HOST_FILE_DICT_TYPE_NAME = "FRACTURE_HOST_FILE"
    FRACTURE_MRCEXE_LSF_SH_DICT_TYPE_NAME = "FRACTURE_MRCEXE_LSF.SH"

    # template file generate path,dev
    TEMPLATE_FILE_GENERATE_PATH = GLOBAL_PARAM['TEMPLATE_FILE_GENERATE_PATH']

    # fracture file path
    FILE_PATH_DB = "DB"
    FILE_PATH_LAYER = "layer"
    FILE_PATH_FRACTURE = "fracture"
    FILE_PATH_MEBES = "MEBES"
    FILE_PATH_DEVICE = "Device"
    FILE_PATH_FRACTURE_XOR = "fracture_XOR"

    # vsb12i fracture host_file file name
    FRACTURE_VSB12I_HOST_FILE_NAME = "host_file"
    FRACTURE_VSB12I_XOR_MRCEXE_LSF_SH_FILE_NAME = "mrcexe_lsf.sh"

    # sheet Product_Info
    TOOLING_FORM_EXCEL_SHEET_PRODUCT_INFO = 'Product_Info'
    TOOLING_FORM_EXCEL_SHEET_PRODUCT_INFO_PRODUCT = 'Product'
    TOOLING_FORM_EXCEL_SHEET_PRODUCT_INFO_DESIGN_RULE = 'Design_Rule'

    # sheet Tapeout_Info
    TOOLING_FORM_EXCEL_SHEET_TAPEOUT_INFO = 'Tapeout_Info'
    TOOLING_FORM_EXCEL_SHEET_TAPEOUT_INFO_MASK_MAG = 'Mask_Mag'
    TOOLING_FORM_EXCEL_SHEET_TAPEOUT_INFO_MASK_NAME = 'Mask_Name'
    TOOLING_FORM_EXCEL_SHEET_TAPEOUT_INFO_LAYER_NAME = 'Layer_Name'
    TOOLING_FORM_EXCEL_SHEET_TAPEOUT_INFO_GRADE = 'Grade'
    TOOLING_FORM_EXCEL_SHEET_TAPEOUT_INFO_MASK_TYPE = 'Mask_Type'
    TOOLING_FORM_EXCEL_SHEET_TAPEOUT_INFO_MASK_TYPE_PSM = 'PSM'
    TOOLING_FORM_EXCEL_SHEET_TAPEOUT_INFO_MASK_TYPE_OMOG = 'OMOG'

    # sheet Device_Info
    TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO = 'Device_Info'
    TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO_DEVICE_NAME = 'Device_Name'
    TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO_TOP_STRUCTURE = 'Top_Structure'
    TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO_SOURCE_MAG = 'Source_Mag'
    TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO_FILE_NAME = 'File_Name'
    TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO_LB_X = 'LB_X'
    TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO_LB_Y = 'LB_Y'
    TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO_RT_X = 'RT_X'
    TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO_RT_Y = 'RT_Y'
    TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO_BOOLEAN_INDEX = 'Boolean_Index'
    TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO_SOURCE_DB = 'Source_DB'
    TOOLING_FORM_EXCEL_SHEET_DEVICE_INFO_ROTATE = 'Rotate'

    # sheet Boolean_Info
    TOOLING_FORM_EXCEL_SHEET_BOOLEAN_INFO = 'Boolean_Info'
    TOOLING_FORM_EXCEL_SHEET_BOOLEAN_INFO_GRID = 'GRID'
    TOOLING_FORM_EXCEL_SHEET_BOOLEAN_INFO_OPERATION = 'Operation'
    TOOLING_FORM_EXCEL_SHEET_BOOLEAN_INFO_MASK_NAME = 'Mask_Name'
    TOOLING_FORM_EXCEL_SHEET_BOOLEAN_INFO_TOTAL_BIAS = 'Total_Bias'
    TOOLING_FORM_EXCEL_SHEET_BOOLEAN_INFO_TONE = 'Tone'

    # sheet Layout_Info
    TOOLING_FORM_EXCEL_SHEET_LAYOUT_INFO = 'Layout_Info'
    TOOLING_FORM_EXCEL_SHEET_LAYOUT_INFO_MASK_MAG = 'Mask_Mag'

    # sheet ccd_table
    TOOLING_FORM_EXCEL_SHEET_CCD_TABLE = 'CCD_Table'

    # sheet mlm_info
    TOOLING_FORM_EXCEL_SHEET_MLM_INFO = 'MLM_Info'

    # the constant of tooling form
    TOOLING_FORM_DEVICE_INFO_SOURCE_DB1 = 'DB1'
    TOOLING_FORM_DEVICE_INFO_SOURCE_DB2 = 'DB2'
    TOOLING_FORM_DEVICE_INFO_SOURCE_DB3 = 'DB3'

    # tooling form
    DICTIONARY_PREFIX_TF = 'TF'
    # constant
    DICTIONARY_PREFIX_CO = 'CO'
    # var
    DICTIONARY_PREFIX_VA = 'TF'

    # upload check_status
    CHECK_STATUS_UPLOADING_3 = 3
    CHECK_STATUS_UPLOADED_4 = 4
    CHECK_STATUS_FTP_CHECK_FAIL_5 = 5
    CHECK_STATUS_FTP_CHECK_SUCCESS_6 = 6
    CHECK_STATUS_FTP_DONE_7 = 7

    # Notice Type
    NOTICE_TYPE_DEFAULT = 'default'
    NOTICE_TYPE_PRIMARY = 'primary'
    NOTICE_TYPE_SUCCESS = 'success'
    NOTICE_TYPE_INFO = 'info'
    NOTICE_TYPE_WARNING = 'warning'
    NOTICE_TYPE_DANGER = 'danger'

    # lot convert status
    ##convert status: 0:默认状态，未生成脚本 10：已提交生成脚本，11：脚本生成失败 12：脚本生成成功，未fracture,
    # 20:已提交fracture 21:fracutre 失败 22:fracture 成功
    # 30:XOR已提交 31：xor失败 32:xor成功
    # !fracture成功后不允许再重新生成文件
    LOT_STAGE_DEFAULT = 0
    LOT_STAGE_GEN_FILE_SUBMITTED = 10
    LOT_STAGE_GEN_FILE_ERROR = 11
    LOT_STAGE_GEN_FILE_SUCCESS = 12
    LOT_STAGE_FRACTURE_SUBMITTED = 20
    LOT_STAGE_FRACTURE_ERROR = 21
    LOT_STAGE_FRACTURE_SUCCESS = 22
    LOT_STAGE_XOR_SUBMITED = 30
    LOT_STAGE_XOR_ERROR = 31
    LOT_STAGE_XOR_SUCCESS = 32

    # lot状态，是否为错误信息，错误信息可在timeline中删除
    LOT_STAGE_IS_ERROR_NO = 0
    LOT_STAGE_IS_ERROR_YES = 1

    # 40：writer 文件生成已提交 41：文件生成失败 42：文件生成成功
    # 50:writer ftp已提交 51:ftp 失败 52:ftp完成
    # 60：ftp校验 已提交 61：校验失败 62：校验成功

    # convert-status
    CONVERT_STATUS_WAIT = 0
    CONVERT_STATUS_ON_GOING = 1
    CONVERT_STATUS_DONE = 2
    CONVERT_STATUS_JOB_FAIL = 3
    CONVERT_STATUS_NO_CLEAN = 4
    CONVERT_OPERATION_RELEASE = 0
    CONVERT_OPERATION_SKIP = 1
    CONVERT_OPERATION_HOLD = 2
    CONVERT_OPERATION_REDECK = 3
    CONVERT_OPERATION_REDO = 4
    CONVERT_OPERATION_REDECKANDDO = 5
    CONVERT_OPERATION_AUTO_DECKANDDO = 6

    # full_convert-status
    FULL_CONVERT_STATUS_WAIT = 0
    FULL_CONVERT_STATUS_ON_GOING = 1
    FULL_CONVERT_STATUS_JOB_FAIL = 2
    FULL_CONVERT_STATUS_DONE = 3
    FULL_CONVERT_STATUS_NO_CLEAN = 4
    FULL_CONVERT_STATUS_RUN_FAIL = 5
    FULL_CONVERT_STATUS_NO_LICENSE = 6

    # layout.mds and layout.ini
    LAY_OUT_MDS_FILE_NAME = 'Layout.mds'
    LAY_OUT_INI_FILE_NAME = 'Layout.ini'
    LAY_OUT_MASK_NAME = '{{TF:Tapeput_Info:Mask_name}}'
    LAY_OUT_LOT_ID = '{{LotID}}'
    LAY_OUT_X_Y_NUM = '{{TF:Layout_Info:x_y}}'
    LAY_OUT_FILE_PATH = '/{}/Device/{}/layer/{}'
    # test path
    # LAY_OUT_FILE_PATH_TEST = r'C:\Users\Bard.Zhang\Documents\Engineering\{}\device\{}\layer\{}'

    # making convert status stage name
    MAKING_CONVERT_STATUS_STAGE_NAME_DB = 'DB'
    MAKING_CONVERT_STATUS_STAGE_NAME_FRACTURE = 'Fracture'
    MAKING_CONVERT_STATUS_STAGE_NAME_XOR = 'XOR'
    MAKING_CONVERT_STATUS_STAGE_NAME_MTFORM = 'MT-form'
    MAKING_CONVERT_STATUS_STAGE_NAME_WRITER = 'Writer'
    MAKING_CONVERT_STATUS_STAGE_NAME_JDV = 'JDV'
    MAKING_CONVERT_STATUS_STAGE_NAME_CCD = 'CCD'

    # IEMS server setting in dictionary label
    # IEMS_SERVER_EXECUTE_CMD_URL = "http://172.16.20.226:8089/api/execute_cmd/"
    IEMS_SERVER_EXECUTE_CMD_URL = "IEMS_SERVER_EXECUTE_CMD_URL"
    IEMS_FRACTURE_TEMPLATE_ID = "IEMS_FRACTURE_TEMPLATE_ID"
    IEMS_FRACTURE_XOR_TEMPLATE_ID = "IEMS_FRACTURE_XOR_TEMPLATE_ID"

    # fracture callback url
    FRACTURE_CALLBACK_URL = "FRACTURE_CALLBACK_URL"
    FRACTURE_XOR_CALLBACK_URL = "FRACTURE_XOR_CALLBACK_URL"

    # common method return flag
    COMMON_METHOD_RETURN_FLAG_ERROR = -1
    COMMON_METHOD_RETURN_FLAG_SUCCESS = 200
    COMMON_METHOD_RETURN_FLAG_MSG = "msg"

    # writer type
    WRITER_TYPE_MODE5 = "MODE5"
    WRITER_TYPE_VSB = "VSB"

    MES_OPERATION_NUM_DIS = '100.700'

    MES_OPERATION_ID_TPC = "MCDTPC.1"
    MES_OPERATION_ID_RFL = "MCDRFL.1"
    MES_OPERATION_ID_DVC = "MCDDVC.1"
    MES_OPERATION_ID_JVW = "MCDJVW.1"
    MES_OPERATION_ID_QAC = "MCDQAC.1"
    MES_OPERATION_ID_ODR = "MCDODR.1"
    MES_OPERATION_ID_DIS = "MCDDIS.1"
    MES_OPERATION_ID_FTP = "MCDFTP.1"

    COVER_PAGE_REAL_TIP = 'tp'
    COVER_PAGE_DRY_TIP = 'dr'

    RECIPE_TEMP_PATH = "/qxic/qxic/MaskData/.STD/Recipe_temp/"
    RECIPE_RELEASE_PATH = '/qxic/qxic/MaskData/.STD/Recipe_release/'

    STD_PATTERN_TEMP_PATH = "/qxic/qxic/MaskData/.STD/STDpattern_temp/"
    # STD_PATTERN_TEMP_PATH = "D:/project/svn/Mask_DP_STD_Upload/"
    STD_PATTERN_RELEASE_PATH = "/qxic/qxic/MaskData/.STD/STDpattern_release/"

    CD_MAP_PATH = "/qxic/qxic/MaskData/.STD/NFT_CDMAP/"
    CEC_PATH = "/qxic/qxic/MaskData/.STD/NFT_CEC/"

    # stage name
    STAGE_PRETREATMENT = "Pretreatment"
    STAGE_PRETREATMENT_QC = "Pretreatment Check"
    STAGE_MANDREL = "Mandrel"
    STAGE_CUT_UTILITY = "Cut-AA"
    STAGE_CUT_UTILITY_CHECK = "Cut-AA check"
    STAGE_OD_CHECK = "OD check"
    STAGE_DPT = "DPT"
    STAGE_DPT_CHECK = "DPT Check"
    STAGE_REPLACEMENT = "Replacement"
    STAGE_REPLACEMENT_CHECK = "Replacement Check"
    STAGE_BOOLEAN = "Boolean"
    STAGE_BOOLEAN_CHECK = "Boolean Check"
    STAGE_SHRINKAGE = "Shrink"
    STAGE_SHRINK_QC = "Shrink Check"
    STAGE_T_RULE = "T-rule"
    STAGE_VIA_SHIFT = "Via_shift"
    STAGE_VIA_SHIFT_CHECK = "Via_shift Check"
    STAGE_MOPC = "MOPC"
    STAGE_BOPC = "BOPC"
    STAGE_OPCV = "OPCV"
    STAGE_LMC = "LMC"
    STAGE_MRC = "MRC"
    STAGE_4TYPE_QA = "4type QA"
    STAGE_FRACTURE = "fracture"
    STAGE_FRACTURE_XOR = "fractureXOR"

    DEVICE_INFO_FILE_BASE_PATH = GLOBAL_PARAM['DEVICE_INFO_FILE_BASE_PATH']

    # recipe file back up
    RECIPE_FILE_BACK_UP_PATH = '/qxic/mdproot/Mask_DP_recipe_file_back_up/'

    # Catalog
    CATALOG_LOCAL_PATH = GLOBAL_PARAM['CATALOG_LOCAL_PATH']
    CATALOG_FTP_SERVER_SSH_PATH = GLOBAL_PARAM['CATALOG_FTP_SERVER_SSH_PATH']
    CATALOG_FTP_SERVER_PATH = GLOBAL_PARAM['CATALOG_FTP_SERVER_PATH']
    CATALOG_FTP_SERVER_CONN_CONFIG = GLOBAL_PARAM['CATALOG_FTP_SERVER_CONN_CONFIG']

    NEW_CATALOG_MACHINE_DICT = {"MS03": "MS03_ALTA_4700DP",
                                "MS06": "ebm9500/QYIC/MS06_EBM_9500P",
                                "MS18": "ebm9500/QYIC/MS18_EBM_9500P"}

    CATALOG_MACHINE_DICT = {"MS03": "MS03_ALTA_4700DP",
                            "MS06": "MS06_EBM_9500P",
                            "MS18": "MS18_EBM_9500P"}
    SPONSOR_USER_AUDIT_PRIORITY = 0

    # Catalog FTP Status
    CATALOG_FTP_WAITING = 0
    CATALOG_FTP_UPLOADING = 1
    CATALOG_FTP_FAILED = 2
    CATALOG_FTP_SUCCESS = 3

    # Catalog Writer File Status
    CATALOG_WRITER_FILE_DEFAULT = 0
    CATALOG_WRITER_FILE_CREATING = 1
    CATALOG_WRITER_FILE_FAILED = 2
    CATALOG_WRITER_FILE_SUCCESS = 3

    #Catalog Status
    CATALOG_DEFAULT = 0
    CATALOG_CREATING = 1
    CATALOG_CAN_CATALOG = 2
    CATALOG_REG_CHECKING = 3
    CATALOG_FAILED = 4
    CATALOG_SUCCESS = 5

    # SGD Config
    SGD_SERVER_IP = "172.16.50.243"
    SGD_SERVER_ROOT_ACCOUNT = "root"
    SGD_SERVER_ROOT_PASSWORD = "MKeda@2020"
