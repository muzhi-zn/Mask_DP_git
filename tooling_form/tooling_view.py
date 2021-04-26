# coding:utf-8
import os, datetime, pandas as pd

from system.websocket_view import send_msg
from tooling_form.models import setting, upload_error_msg, product_info_temp, tapeout_info_temp, device_info_temp, \
    ccd_table_temp, boolean_info_temp, layout_info_temp, mlm_info_temp
from django.http.response import JsonResponse
from django.db import transaction
from system.models import dict
# from unittest import case
from tooling_form.service.tooling_check_data_service import tooling_check_data_service
from tooling_form.service.save_excel_data_service import save_excel_data
from utilslibrary.system_constant import Constant
from tooling_form.service.create_folder_service import local_create_folder
from django.views.decorators.csrf import csrf_exempt
from utilslibrary.utils.date_utils import getDateStr, getMilliSecond
from tooling_form.service.tooling_service import PRE_CONDITION_SERVICE, ToolService
from utilslibrary.utils.common_utils import getCurrentSessionID, getCurrentSessionName
# from pip._internal.cli import status_codes
from utilslibrary.decorators.catch_exception_decorators import catch_exception
from Mask_DP.settings import Tooling_Form_Sheet
from tooling_form.service.tooling_service import str_strip
from tooling_form.models import import_data_temp, product_info, import_list

state_dict = {}

uploading_product = []


@transaction.atomic
@csrf_exempt
@catch_exception
def import_main(request):
    # with transaction.atomic():
        # 创建事务保存点
        # s1 = transaction.savepoint()
    # get user_id from session
    u_id = getCurrentSessionID(request)
    u_name = getCurrentSessionName(request)
    new_tip_no = ''

    # Upload ==================================================================================================== start
    send_msg(u_id, {'is_tooling_msg': True, 'msg': 'Start upload'})

    # upload Tooling Form
    obj = request.FILES.get('file')
    upload_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    old_filename = obj.name

    # user_id + datetime +
    filename = str(u_id) + '_' + upload_time + '.' + obj.name.split('.')[-1]

    # Create folder
    cur_path = os.path.abspath(os.path.dirname(__file__)).split('Mask_DP')[0]
    upl_path = os.path.join(os.path.dirname(cur_path), 'Mask_DP_upload')
    if not os.path.exists(upl_path):
        os.mkdir(upl_path)

    file_path = os.path.join(upl_path, filename)

    # open file
    # wb : 以二进制格式打开一个文件只用于写入。如果该文件已存在则打开文件，并从开头开始编辑，
    #      即原有内容会被删除。如果该文件不存在，创建新文件。一般用于非文本文件如图片等。
    with open(file_path, 'wb') as f:
        for chunk in obj.chunks():
            f.write(chunk)
            f.close()

    upload_path = file_path

    # update last error_status & upload
    ToolService().import_error_list_is_delete(u_id)
    ToolService().pre_import_list_is_delete(u_id)

    send_msg(u_id, {'is_tooling_msg': True, 'msg': 'Upload success'})
    # Upload ====================================================================================================== end

    # Check tooling form sheet & column name ==================================================================== start
    send_msg(u_id, {'is_tooling_msg': True, 'msg': 'Start check tooling form format'})

    try:
        check_result = ToolService().check_sheet_column_name(upload_path)
        if not check_result:
            #transaction.savepoint_rollback(s1)
            return JsonResponse({'success': 'false', 'flag': '0', 'msg': Constant.ERROR_TIP_200}, safe=False)
    except Exception as e:
        #transaction.savepoint_rollback(s1)
        print(e)
        return JsonResponse({'success': 'false', 'flag': '0', 'msg': Constant.ERROR_TIP_200}, safe=False)

    send_msg(u_id, {'is_tooling_msg': True, 'msg': 'Check tooling form format success'})
    # Check tooling form sheet & column name ====================================================================== end

    # Check data ================================================================================================ start
    send_msg(u_id, {'is_tooling_msg': True, 'msg': 'Start check data'})

    status = ToolService().check_data_exist(u_id, upload_path)
    if not status:

        # EK_Harry.Lee 插入主表 import_list 原 upload
        # ToolService().upload(new_tip_no, filename, old_filename, u_id, u_name, check_data)
        ToolService().import_list(new_tip_no, filename, old_filename, u_id, u_name, '1', '0', status)
        #transaction.savepoint_rollback(s1)
        return JsonResponse({'success': 'false', 'tip_no': new_tip_no, 'flag': '1', 'msg': Constant.ERROR_TIP_400}, safe=False)

    send_msg(u_id, {'is_tooling_msg': True, 'msg': 'Check data success'})
    # Check data ================================================================================================== end

    # Precondition ============================================================================================== start
    send_msg(u_id, {'is_tooling_msg': True, 'msg': 'Start check precondition'})
    # Pre_condition check
    try:
        pre_con_101_s, product_name = PRE_CONDITION_SERVICE(Tooling_Form_Sheet, upload_path,
                                                            u_id).precondition_check_101()
        if product_name in uploading_product:  # 该产品正在上传
            #transaction.savepoint_rollback(s1)
            return JsonResponse(
                {'success': 'false', 'tip_no': new_tip_no, 'flag': '2', 'msg': "This Product is Uploading"},
                safe=False)
        else:
            uploading_product.append(product_name)
        pre_con_s = PRE_CONDITION_SERVICE(Tooling_Form_Sheet, upload_path, u_id).precondition_check_main()
        pre_con_s = pre_con_101_s and pre_con_s

        status = pre_con_s
        if not pre_con_s:
            # if pre_condition check  error tip_no = null

            # EK_Harry.Lee 插入主表 import_list 原 upload
            # ToolService().upload(new_tip_no, filename, old_filename, u_id, u_name, check_status)
            ToolService().import_list(new_tip_no, filename, old_filename, u_id, u_name, '1', '0', status)
            uploading_product.remove(product_name)
            #transaction.savepoint_rollback(s1)
            return JsonResponse({'success': 'false', 'tip_no': new_tip_no, 'flag': '1', 'msg': Constant.ERROR_TIP_400}, safe=False)
    except Exception as e:
        uploading_product.remove(product_name)
        #transaction.savepoint_rollback(s1)
        return JsonResponse({'success': 'false', 'flag': '0', 'msg': Constant.ERROR_TIP_300}, safe=False)

    send_msg(u_id, {'is_tooling_msg': True, 'msg': 'Check precondition success'})
    # Precondition ================================================================================================ end

    # Create tip_no ============================================================================================= start
    send_msg(u_id, {'is_tooling_msg': True, 'msg': 'Start create tip_no'})

    # Create TIP No
    req_tip_no = request.POST.get('tip_no')

    tip_no_status, old_tip_no = ToolService().check_ACK(upload_path, u_id)
    upload_type = 0

    if not req_tip_no and tip_no_status == 0:
        # 不带 tip_no 且 ACK 无数据 原新增流程
        upload_type = 0
        new_tip_no = ToolService().create_tip_no(u_id)
    elif not req_tip_no and tip_no_status == 1:
        # 不带 tip_no 且 ACK 只有临时数据 原新增流程
        upload_type = 1
        new_tip_no = old_tip_no
    elif not req_tip_no and tip_no_status == 2:
        # 不带 tip_no 且 ACK 有正式数据 数据校验后走check流程
        upload_type = 2
        new_tip_no = old_tip_no
    elif req_tip_no == old_tip_no and tip_no_status == 1:
        # 带 tip_no 且 ACK 只有测试数据 原新增流程
        upload_type = 3
        new_tip_no = old_tip_no
    elif req_tip_no == old_tip_no and tip_no_status == 2:
        # 带 tip_no 且 ACK 有正式数据 数据校验后走check流程
        upload_type = 4
        new_tip_no = old_tip_no
    else:
        # 提示上传的文件有问题
        uploading_product.remove(product_name)
        #transaction.savepoint_rollback(s1)
        return JsonResponse({'success': 'false', 'flag': '', 'msg': Constant.ERROR_TIP_100}, safe=False)

    if upload_type in [1, 2, 3, 4]:
        product_info_temp.objects.filter(tip_no=new_tip_no, create_by=u_id).delete()
        tapeout_info_temp.objects.filter(tip_no=new_tip_no, create_by=u_id).delete()
        device_info_temp.objects.filter(tip_no=new_tip_no, create_by=u_id).delete()
        ccd_table_temp.objects.filter(tip_no=new_tip_no, create_by=u_id).delete()
        boolean_info_temp.objects.filter(tip_no=new_tip_no, create_by=u_id).delete()
        layout_info_temp.objects.filter(tip_no=new_tip_no, create_by=u_id).delete()
        mlm_info_temp.objects.filter(tip_no=new_tip_no, create_by=u_id).delete()
        import_data_temp.objects.filter(tip_no=new_tip_no, create_by=u_id).delete()

        ToolService().import_error_list_is_delete_import_data(new_tip_no, u_id)
        ToolService().import_check_list_is_delete_import_data(new_tip_no, u_id)

        old_import_item = import_list.objects.get(tip_no=new_tip_no, is_delete='0')
        old_status = old_import_item.status
        ToolService().import_list_is_delete(new_tip_no, u_id)

        # EK_Harry.Lee 原逻辑删除 原数据表
        # import_data.objects.filter(tip_no=req_tip_no).delete()

        # EK_Harry.Lee 原逻辑删除 文件分析表
        # file_analysis_info.objects.filter(tip_no=req_tip_no).delete()

        # EK_Harry.Lee 原逻辑删除 关于lot convert
        #  删除lot_info
        # lot_info_list = lot_info.objects.filter(tip_no=req_tip_no)
        # print("--------------------------")
        # print(lot_info_list.count())
        # print("--------------------------")
        # if lot_info_list.count() > 0:
        #     lot_info_list.delete()
        #     for l_i in lot_info_list:
        #         delete_lot(req_tip_no, l_i.mask_name)
         # c_s_list = convert_status.objects.filter(tip_no=req_tip_no)
        # if c_s_list.count() > 0:
        #     c_s_list.delete()

    # Insert new_tip_no to upload
    # ToolService().upload(new_tip_no, filename, old_filename, u_id, u_name, check_status)
    # 修改代码，防止user_id出现异常
    upload_import_list = import_list.objects.create(tip_no=new_tip_no, file_name=filename, old_file_name=old_filename,
                                                    create_by=u_id, create_name=u_name, error_status='0',
                                                    check_status='0', status=status, create_date=getDateStr(),
                                                    create_time=getMilliSecond())

    send_msg(u_id, {'is_tooling_msg': True, 'msg': 'Create tip_no success'})
    # Create tip_no =============================================================================================== end

    # Check tooling form data =================================================================================== start
    send_msg(u_id, {'is_tooling_msg': True, 'msg': 'Start check tooling form data'})

    # get_setting
    setting_all = setting.objects.filter(enable=1).order_by('id')

    set_id = setting.objects.all().values('id')
    set_sheet_name = setting.objects.all().values('sheet_name')
    set_column_name = setting.objects.all().values('column_name')
    set_required_field = setting.objects.all().values('required_field')
    set_row = setting.objects.all().values('row')
    set_column = setting.objects.all().values('column')
    set_parent_id = setting.objects.all().values('parent_id')
    set_regex = setting.objects.all().values('regex')
    set_regex_no = setting.objects.all().values('regex_no')

    i = setting_all.count()
    flag = True
    flag_upload_check_status = True
    x = 0
    while x < i:

        id_value = set_id[x]['id']
        sheet_name_value = set_sheet_name[x]['sheet_name']
        column_name_value = set_column_name[x]['column_name']
        required_field_value = set_required_field[x]['required_field']
        row_value = set_row[x]['row']
        column_value = set_column[x]['column']
        parent_id_value = set_parent_id[x]['parent_id']
        regex_value = set_regex[x]['regex']
        regex_no_value = set_regex_no[x]['regex_no']

        df = pd.read_excel(upload_path, sheet_name=sheet_name_value)
        k = row_value + 1
        while k < len(df):

            # tip_no
            data_tip_no = new_tip_no
            # sheet_name
            data_sheet_name = sheet_name_value
            # column_name
            data_column_name = column_name_value
            # import_data
            data_import_data = str_strip(df.iloc[k, column_value])
            # data_key
            data_data_key = ToolService().data_key(df, sheet_name_value, k)
            # data_regex_no
            data_regex_no = regex_no_value

            # import_data_status
            data_id = ""
            error_message = ""
            data_error_code = ""
            validate_value = ""
            regex = ""

            # # check null
            data_import_data_status = 1
            if (required_field_value == 1) and (parent_id_value == 0) and (regex_value == 0):
                if data_import_data == 'nan' or data_import_data == '':
                    data_import_data_status = 0
                    data_error_code = 'ERROR_NULL_001'
                    error_message = str(Constant.ERROR_NULL_001)
                else:
                    data_import_data_status = 1

            # check regex
            if (required_field_value == 1) and (parent_id_value == 0) and (regex_value == 1):
                regex_str = data_import_data
                check_regex_result = ToolService().check_regex(regex_no_value, regex_str)

                if check_regex_result == 1:
                    data_import_data_status = 1
                else:
                    data_import_data_status = 0
                    data_error_code = check_regex_result[1]
                    error_message = check_regex_result[2]
                    validate_value = check_regex_result[3]

            # check dict
            if (required_field_value == 1) and (parent_id_value != 0) and (regex_value == 0):
                parent = dict.objects.filter(parent_id=parent_id_value).values('value')
                parent_c = parent.count()
                j = 0
                parent_set = set()
                while j < parent_c:
                    parent_set.add(parent[j]['value'])
                    j += 1
                df_set = set()
                df_set.add(data_import_data)
                isdisjoint_result = parent_set.isdisjoint(df_set)
                if not isdisjoint_result:
                    data_import_data_status = 1
                else:
                    data_import_data_status = 0
                    data_error_code = 'ERROR_DICT_001'

                    error_list = upload_error_msg.objects.filter(set_id=id_value).all().values('message')
                    error_len = error_list.count()

                    if error_len == 0:
                        error_message = str(Constant.ERROR_DICT_001 % (df_set, parent_set))
                    else:
                        error_value = error_list[0]['message']
                        error_message = error_value

                    validate_value = str('''"%s"''' % (list(parent_set)))

            # check operation
            if data_column_name == 'Operation':
                operation_str = data_import_data
                check_operation_result = ToolService().check_operation(operation_str)
                if check_operation_result == 1:
                    data_import_data_status = 1
                else:
                    data_import_data_status = 0
                    data_error_code = check_operation_result[1]
                    error_message = check_operation_result[2]

            # insert import_data
            # EK_Harry.Lee  原逻辑中循环插入 import_data表 弃用
            import_data_temp_id = ToolService().import_data_temp(u_id, data_id, data_tip_no, data_sheet_name,
                                                                 data_column_name, data_import_data,
                                                                 data_import_data_status, data_data_key)

            # insert import_error_message_log
            if data_import_data_status == 0:
                import_list_id = upload_import_list.id
                import_data_temp_id = import_data_temp_id
                data_error_code = data_error_code
                data_error_description = error_message
                data_error_type = 2
                data_error_status = data_import_data_status
                data_create_by = u_id
                # replace {}

                # EK_Harry.Lee 原逻辑错误信息表改用 import_error_list
                # ToolService().import_error_message_log(data_import_data_id, data_tip_no, data_import_data,
                #                                        required_field_value, data_sheet_name, data_column_name,
                #                                        parent_id_value, data_regex_no, data_error_code,
                #                                        data_error_description,
                #                                        data_error_type, data_error_status, data_create_by,
                #                                        validate_value)
                ToolService().import_error_list(import_list_id, import_data_temp_id, data_tip_no, data_import_data,
                                                required_field_value, data_sheet_name, data_column_name,
                                                parent_id_value, data_regex_no, data_error_code,
                                                data_error_description,
                                                data_error_type, data_error_status, data_create_by,
                                                validate_value)
                flag = False
                flag_upload_check_status = False

            k += 1

        x += 1

    send_msg(u_id, {'is_tooling_msg': True, 'msg': 'Check tooling form data success'})
    # Check tooling form data ===================================================================================== end

    # save_excel_data().save_data(upload_path, new_tip_no)  # 数据插入冗余

    if flag_upload_check_status:
        status = 2
        # ToolService().upload_check_status(new_tip_no, check_status)
        ToolService().import_list_check_status(new_tip_no, '0', '0', status)

        if upload_type in [0, 1, 3]:
            save_excel_data().save_data(upload_path, new_tip_no, u_id)
            ToolService().import_list_check_status(new_tip_no, '0', '0', status)
        else:
            save_excel_data().save_data_temp(upload_path, new_tip_no, upload_import_list.id, u_id)
            check_flag, change_flag = tooling_check_data_service().check_data_main(new_tip_no, upload_import_list.id,
                                                                                   u_id)
            check_status = '0'
            if not check_flag:
                check_status = '1'

            # 如果没有改动status 沿用上个版本中的状态
            if change_flag:
                ToolService().import_list_check_status(new_tip_no, '0', check_status, status)
            else:
                ToolService().import_list_check_status(new_tip_no, '0', check_status, old_status)

            if not check_flag:
                uploading_product.remove(product_name)
                #transaction.savepoint_commit(s1)
                return JsonResponse({'success': 'false', 'flag': '2', 'tip_no': new_tip_no,
                                     'msg': Constant.CHECK_TIP_000}, safe=False)


    else:
        status = 1
        # ToolService().upload_check_status(new_tip_no, check_status)
        ToolService().import_list_check_status(new_tip_no, '1', '0', status)
        save_excel_data().save_data_temp(upload_path, new_tip_no, upload_import_list.id, u_id)
    local_create_folder(new_tip_no)
    if flag:
        uploading_product.remove(product_name)
        #transaction.savepoint_commit(s1)
        return JsonResponse({'success': 'true', 'tip_no': new_tip_no}, safe=False)
    else:
        uploading_product.remove(product_name)
        #transaction.savepoint_rollback(s1)
        return JsonResponse({'success': 'false', 'tip_no': new_tip_no, 'flag': '1', 'msg': Constant.ERROR_TIP_400}, safe=False)
