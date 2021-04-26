import os
import traceback

from Mask_DP.settings import CATALOG_LOCAL_PATH
from tooling_form.service.show_tip_no_service import del_fracture_file
from utilslibrary.mes_webservice.mes_demo.MES_TxOpeLocateReq import ope_locate
from utilslibrary.mes_webservice.mes_webservice import mes_op_locate
from utilslibrary.system_constant import Constant
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from catalog.models import tool_maintain
from jdv.models import lot_info
from making.models import convert_status
from system.websocket_view import send_msg
from tooling_form.models import import_check_list, tapeout_info_temp, tapeout_info, boolean_info_temp, boolean_info, \
    layout_info_temp, layout_info, ccd_table_temp, ccd_table, mlm_info_temp, mlm_info, device_info, device_info_temp, \
    import_list

from utilslibrary.decorators.catch_exception_decorators import catch_exception
from utilslibrary.utils.date_utils import getDateStr, getMilliSecond
from utilslibrary.utils.file_utils import del_file
from utilslibrary.utils.iems_utils import pause_job
from utilslibrary.utils.ssh_utils import SSHManager

'''
    1.同步数据：
        1.1.根据mask_name判断是否锁定
            1.1.1。如果锁定，则不进行同步数据
            1.1.2。如果未锁定，则将正式表数据删除，将临时表数据同步到正式表，并将临时表数据删除
            1.1.3.如果是同步device_info表，
                1.则需要判断该mask_name使用的device_info数据是否被其他mask_name同时使用
                2.如果被同时使用，则判断其他mask_name是否被锁定
                3.如果有一个被锁定，则mask_name所有sheet的数据不同步
'''


# @transaction.atomic
@csrf_exempt
# @catch_exception
def toolingSheetContrast(tip_no, mask_name, u_id):
    data = {}
    with transaction.atomic():
        s1 = transaction.savepoint()
        try:

            # 根据mask_name和tip_no查询check_list表获取check_code并去重
            check_one = import_check_list.objects.filter(tip_no=tip_no, mask_name=mask_name, is_delete=0,
                                                         status=0).order_by("-check_code")

            # 如果存在，则获取check_code最大的一条
            if check_one.exists():
                check_code = check_one[0].check_code
            # 不存在，则直接返回并提示数据不存在
            else:
                data["success"] = False
                data["msg"] = "data not exist sync failed"

                return JsonResponse(data, safe=False)

            create_date = getDateStr()
            create_time = getMilliSecond()
            update_date = getDateStr()
            update_time = getMilliSecond()

            # 根据传入mask_name和sheet_name查询正式表和临时表数据
            if mask_name:

                # 判断该mask_name是否被锁定，如果被锁定，则不进行任何操作，如果未被锁定，则进行所有资料的覆盖
                lot_list = lot_info.objects.filter(mask_name=mask_name, tip_no=tip_no, writer_op_status='3', is_delete=0)

                # 如果有值，则代表改mask_name被锁定，则不进行任何操作
                if lot_list.exists():

                    data["success"] = False
                    data["msg"] = "mask_name be locked sync failed"

                    return JsonResponse(data, safe=False)
                else:

                    # 将check_list表status改为同步中(2)
                    import_check_list.objects.filter(tip_no=tip_no, mask_name=mask_name, is_delete=0, status=0) \
                        .update(status=2, update_date=update_date, update_time=update_time, update_by=u_id)

                    # 1 操作device_info===========================================================================================================start
                    # send_msg(u_id, {'is_tooling_from_msg': True, 'msg': 'Start device_info sync'})

                    # device_info_temp临时表的id的集合
                    device_id_temp_list = []

                    print("开始同步device_info中的数据")

                    # 获取boolean_info表中数据
                    boolean_info_list = boolean_info_temp.objects.filter(mask_name=mask_name, tip_no=tip_no, is_delete=0)

                    if boolean_info_list.exists():

                        for boolean_info_one in boolean_info_list:

                            # 获得boolean_info中的boolean_index,source_db
                            booleanIndex = boolean_info_one.boolean_index
                            sourceDb = boolean_info_one.source_db

                            # 查询device_info_temp里的对应数据，存储其ID
                            info_temp_id_list = device_info_temp.objects.filter(
                                boolean_index=booleanIndex,
                                source_db=sourceDb, is_delete=0)

                            if info_temp_id_list.exists():

                                for info_temp_id_one in info_temp_id_list:
                                    device_id_temp_list.append(info_temp_id_one.id)

                    # 判断device_id_temp_list长度，如果都有数据，则将正式表数据删除，将临时表数据插入正式表，并删除临时表数据
                    if len(device_id_temp_list) > 0:

                        # 将正式表数据删除
                        device_info.objects.filter(mask_name=mask_name, tip_no=tip_no, is_delete=0) \
                            .update(is_delete=1, update_date=update_date, update_time=update_time, update_by=u_id)

                        # 查询出测试表数据，将其放到正式表
                        device_list = device_info_temp.objects.filter(id__in=device_id_temp_list, is_delete=0).distinct()

                        for device_one in device_list:
                            _dev = device_info()

                            _dev.tip_no = device_one.tip_no
                            _dev.mask_name = mask_name
                            _dev.psm = device_one.psm
                            _dev.source_db = device_one.source_db
                            _dev.device_type = device_one.device_type
                            _dev.device_name = device_one.device_name
                            _dev.boolean_index = device_one.boolean_index
                            _dev.bias_sequence = device_one.bias_sequence
                            _dev.rotate = device_one.rotate
                            _dev.file_name = device_one.file_name
                            _dev.top_structure = device_one.top_structure
                            _dev.source_mag = device_one.source_mag
                            _dev.shrink = device_one.shrink
                            _dev.lb_x = device_one.lb_x
                            _dev.lb_y = device_one.lb_y
                            _dev.rt_x = device_one.rt_x
                            _dev.rt_y = device_one.rt_y
                            _dev.check_method = device_one.check_method
                            _dev.value = device_one.value
                            _dev.file_size = device_one.file_size
                            _dev.is_delete = 0
                            _dev.create_by = u_id
                            _dev.create_date = create_date
                            _dev.create_time = create_time

                            _dev.save()

                        # 将测试表数据删除
                        device_info_temp.objects.filter(id__in=device_id_temp_list, is_delete=0) \
                            .update(is_delete=1, update_date=update_date, update_time=update_time, update_by=u_id)

                        print("device_info中的数据同步完成")
                    else:
                        print("device_info中无需要同步的数据")

                    # send_msg(u_id, {'is_tooling_from_msg': True, 'msg': 'device_info sync success'})
                    # 1 操作device_info===========================================================================================================end

                    # 2 操作tapeout_info=========================================================================================================start
                    # 获取临时表数据
                    # send_msg(u_id, {'is_tooling_from_msg': True, 'msg': 'Start tapeout_info sync'})
                    print("开始同步tapeout_info中的数据")
                    tapeout_list = tapeout_info_temp.objects.filter(mask_name=mask_name, tip_no=tip_no, is_delete=0)

                    if tapeout_list.exists():

                        # 删除对应正式表数据
                        old_tapeout_info = tapeout_info.objects.get(mask_name=mask_name, tip_no=tip_no, is_delete=0)
                        old_tapeout_info.is_delete = 1
                        old_tapeout_info.update_date = update_date
                        old_tapeout_info.update_time = update_time
                        old_tapeout_info.update_by = u_id
                        old_tapeout_info.save()

                        for tapeout_one in tapeout_list:
                            # 将临时表数据插入正式表
                            _tape = tapeout_info()

                            _tape.mask_name = tapeout_one.mask_name
                            _tape.tip_no = tapeout_one.tip_no
                            _tape.t_o = tapeout_one.t_o
                            _tape.layer_name = tapeout_one.layer_name
                            _tape.grade = tapeout_one.grade
                            _tape.mask_mag = tapeout_one.mask_mag
                            _tape.mask_type = tapeout_one.mask_type
                            _tape.alignment = tapeout_one.alignment
                            _tape.pellicle = tapeout_one.pellicle
                            _tape.light_sourse = tapeout_one.light_sourse
                            _tape.rotation = tapeout_one.rotation
                            _tape.barcode = tapeout_one.barcode
                            _tape.inspection = tapeout_one.inspection
                            _tape.version = tapeout_one.version
                            _tape.is_delete = 0
                            _tape.create_by = u_id
                            _tape.create_date = create_date
                            _tape.create_time = create_time

                            # 改变不影convert is_done 沿用老数据
                            if check_code == 'CHECK_TIP_004':
                                _tape.is_done = 0
                            else:
                                _tape.is_done = old_tapeout_info.is_done
                            _tape.save()

                        # 将临时表数据删除
                        tapeout_info_temp.objects.filter(mask_name=mask_name, tip_no=tip_no, is_delete=0) \
                            .update(is_delete=1, update_date=update_date, update_time=update_time, update_by=u_id)

                        print("tapeout_info表数据同步完成")
                    else:

                        print("tapeout_info无需要同步的数据")

                    # send_msg(u_id, {'is_tooling_from_msg': True, 'msg': 'tapeout_info sync success'})
                    # 2 操作tapeout_info===========================================================================================================end

                    # 3 操作boolean_info===========================================================================================================start
                    # send_msg(u_id, {'is_tooling_from_msg': True, 'msg': 'Start boolean_info sync'})
                    print("开始同步boolean_info中的数据")
                    # 获取临时表数据
                    boolean_list = boolean_info_temp.objects.filter(mask_name=mask_name, tip_no=tip_no, is_delete=0)

                    if boolean_list.exists():

                        # 删除对应正式表数据
                        boolean_info.objects.filter(mask_name=mask_name, tip_no=tip_no, is_delete=0) \
                            .update(is_delete=1, update_date=update_date, update_time=update_time, update_by=u_id)

                        for boolean_one in boolean_list:
                            # 将临时表数据插入正式表
                            _bool = boolean_info()

                            _bool.tip_no = boolean_one.tip_no
                            _bool.boolean_index = boolean_one.boolean_index
                            _bool.source_db = boolean_one.source_db
                            _bool.mask_name = boolean_one.mask_name
                            _bool.grid = boolean_one.grid
                            _bool.operation = boolean_one.operation
                            _bool.total_bias = boolean_one.total_bias
                            _bool.tone = boolean_one.tone
                            _bool.is_delete = 0
                            _bool.create_by = u_id
                            _bool.create_date = create_date
                            _bool.create_time = create_time
                            _bool.save()

                        # 将临时表数据删除
                        boolean_info_temp.objects.filter(mask_name=mask_name, tip_no=tip_no, is_delete=0) \
                            .update(is_delete=1, update_date=update_date, update_time=update_time, update_by=u_id)

                        print("boolean_info中的数据同步完成")
                    else:
                        print("boolean_info中无需要同步的数据")

                    # send_msg(u_id, {'is_tooling_from_msg': True, 'msg': 'boolean_info sync success'})
                    # 3 操作boolean_info=========================================================================================================end

                    # 4 操作layout_info=========================================================================================================start
                    # send_msg(u_id, {'is_tooling_from_msg': True, 'msg': 'Start layout_info sync'})
                    print("开始同步layout_info中的数据")
                    # 获取临时表数据
                    layout_list = layout_info_temp.objects.filter(mask_name=mask_name, tip_no=tip_no, is_delete=0)

                    if layout_list.exists():

                        # 删除对应正式表数据
                        layout_info.objects.filter(mask_name=mask_name, tip_no=tip_no, is_delete=0) \
                            .update(is_delete=1, update_date=update_date, update_time=update_time, update_by=u_id)

                        for layout_one in layout_list:
                            # 将临时表数据插入正式表
                            _lay = layout_info()

                            _lay.tip_no = layout_one.tip_no
                            _lay.psm = layout_one.psm
                            _lay.device_name = layout_one.device_name
                            _lay.mask_mag = layout_one.mask_mag
                            _lay.mask_name = layout_one.mask_name
                            _lay.source_mag = layout_one.source_mag
                            _lay.original = layout_one.original
                            _lay.x1 = layout_one.x1
                            _lay.y1 = layout_one.y1
                            _lay.pitch_x = layout_one.pitch_x
                            _lay.pitch_y = layout_one.pitch_y
                            _lay.array_x = layout_one.array_x
                            _lay.array_y = layout_one.array_y
                            _lay.is_delete = 0
                            _lay.create_by = u_id
                            _lay.create_date = create_date
                            _lay.create_time = create_time

                            _lay.save()

                        # 将临时表数据删除
                        layout_info_temp.objects.filter(mask_name=mask_name, tip_no=tip_no, is_delete=0) \
                            .update(is_delete=1, update_date=update_date, update_time=update_time, update_by=u_id)

                        print("layout_info中的数据同步完成")
                    else:
                        print("layout_info中无需要同步的数据")

                    # send_msg(u_id, {'is_tooling_from_msg': True, 'msg': 'layout_info sync success'})
                    # 4 操作layout_info========================================================================================================end

                    # 5 操作ccd_table========================================================================================================start
                    # send_msg(u_id, {'is_tooling_from_msg': True, 'msg': 'Start ccd_table sync'})
                    print("开始同步ccd_table中的数据")
                    # 获取临时表数据
                    ccd_list = ccd_table_temp.objects.filter(mask_name=mask_name, tip_no=tip_no, is_delete=0)

                    if ccd_list.exists():

                        # 删除对应正式表数据
                        ccd_table.objects.filter(mask_name=mask_name, tip_no=tip_no, is_delete=0) \
                            .update(is_delete=1, update_date=update_date, update_time=update_time, update_by=u_id)
                        c_list = []
                        for ccd_one in ccd_list:
                            # 将临时表数据插入正式表
                            _ccd = ccd_table()

                            _ccd.tip_no = ccd_one.tip_no
                            _ccd.no = ccd_one.no
                            _ccd.type = ccd_one.type
                            _ccd.coor_x = ccd_one.coor_x
                            _ccd.coor_y = ccd_one.coor_y
                            _ccd.item = ccd_one.item
                            _ccd.tone = ccd_one.tone
                            _ccd.direction = ccd_one.direction
                            _ccd.cd_4x_nm = ccd_one.cd_4x_nm
                            _ccd.mask_name = ccd_one.mask_name
                            _ccd.is_delete = 0
                            _ccd.create_by = u_id
                            _ccd.create_date = create_date
                            _ccd.create_time = create_time
                            c_list.append(_ccd)
                            # _ccd.save()
                        ccd_table.objects.bulk_create(c_list)
                        # 将临时表数据删除
                        ccd_table_temp.objects.filter(mask_name=mask_name, tip_no=tip_no, is_delete=0) \
                            .update(is_delete=1, update_date=update_date, update_time=update_time, update_by=u_id)

                        print("ccd_table中的数据同步完成")
                    else:
                        print("ccd_table中无需要同步的数据")

                    # send_msg(u_id, {'is_tooling_from_msg': True, 'msg': 'ccd_table sync success'})
                    # 5 操作ccd_table===========================================================================================================end

                    # 6 操作mlm_info===========================================================================================================start
                    # send_msg(u_id, {'is_tooling_from_msg': True, 'msg': 'Start mlm_info sync'})
                    print("开始同步mlm_info中的数据")
                    # 获取临时表数据
                    mlm_list = mlm_info_temp.objects.filter(mask_name=mask_name, tip_no=tip_no, is_delete=0)

                    if mlm_list.exists():

                        # 删除对应正式表数据
                        mlm_info.objects.filter(mask_name=mask_name, tip_no=tip_no, is_delete=0) \
                            .update(is_delete=1, update_date=update_date, update_time=update_time, update_by=u_id)

                        for mlm_one in mlm_list:
                            # 将临时表数据插入正式表
                            _mlm = mlm_info()

                            _mlm.tip_no = mlm_one.tip_no
                            _mlm.mlm_mask_id = mlm_one.mlm_mask_id
                            _mlm.mask_name = mlm_one.mask_name
                            _mlm.field_name = mlm_one.field_name
                            _mlm.shift_x = mlm_one.shift_x
                            _mlm.shift_y = mlm_one.shift_y
                            _mlm.is_delete = 0
                            _mlm.create_by = u_id
                            _mlm.create_date = create_date
                            _mlm.create_time = create_time

                            _mlm.save()

                        # 将临时表数据删除
                        mlm_info_temp.objects.filter(mask_name=mask_name, tip_no=tip_no, is_delete=0) \
                            .update(is_delete=1, update_date=update_date, update_time=update_time, update_by=u_id)

                        print("mlm_info中的数据同步完成")
                    else:
                        print("mlm_info中无需要同步的数据")

                    # send_msg(u_id, {'is_tooling_from_msg': True, 'msg': 'mlm_info sync success'})
                    # 6 操作mlm_info===========================================================================================================end

                    # TODO
                    # 7 判断数据改变，convert有无影响，并决定是否重跑convert=========================================================================start

                    # 如果对conver有影响
                    if check_code == 'CHECK_TIP_004':

                        # 调用重跑convert方法
                        device_set = convert_status.objects.values('device_name').distinct().filter(
                            mask_name=mask_name, tip_no=tip_no)
                        device_name_list = []
                        for device in device_set:
                            device_name_list.append(device['device_name'])
                        convert_query_set = convert_status.objects.filter(mask_name=mask_name, tip_no=tip_no)
                        if convert_query_set:
                            flag = convert_rerun(mask_name=mask_name, tip_no=tip_no, device_list=device_name_list)
                            if flag == 1:
                                data["success"] = False
                                data["msg"] = "convert file del failed"
                                return JsonResponse(data, safe=False)
                            elif flag == 2:
                                data["success"] = False
                                data["msg"] = "catalog file del failed"
                                return JsonResponse(data, safe=False)
                            elif flag == 3:
                                data["success"] = False
                                data["msg"] = "lot ID move back failed"
                                return JsonResponse(data, safe=False)
                            elif flag == 5:
                                data["success"] = False
                                data["msg"] = "lot locate failed"
                                return JsonResponse(data, safe=False)
                    # 如果对conver无影响
                    elif check_code == 'CHECK_TIP_003':

                        # 调用不重跑convert方法
                        pass

                    # 7 判断数据改变，convert有无影响，并决定是否重跑convert=========================================================================end

                    # 将check_list表status由同步中改为同步完成2-->1
                    import_check_list.objects.filter(tip_no=tip_no, mask_name=mask_name, is_delete=0, status=2) \
                        .update(status=1, update_date=update_date, update_time=update_time, update_by=u_id)

                    # 查询该top_no在check_list中是否有未同步完成的数据
                    import_one = import_check_list.objects.filter(~Q(sheet_name=""), tip_no=tip_no, is_delete=0,
                                                                  status__in=[0, 2])

                    # 如果都同步完成
                    if not import_one:
                        # 将import_list中check_status改为0
                        import_list.objects.filter(tip_no=tip_no, is_delete=0) \
                            .update(check_status=0, update_date=update_date, update_time=update_time, update_by=u_id)
                    transaction.savepoint_commit(s1)
                    data["success"] = True
                    data["msg"] = "sync success"
        except Exception as e:
            transaction.savepoint_rollback(s1)
            traceback.print_exc()
            print(e)
            data["success"] = False
            data["msg"] = "sync failed"

    return JsonResponse(data, safe=False)


def convert_rerun(mask_name, tip_no, device_list):
    print(mask_name)
    print(tip_no)
    print(device_list)
    for device in device_list:
        convert_set = convert_status.objects.filter(mask_name=mask_name, tip_no=tip_no, device_name=device)
        print(convert_set.values())
        for convert in convert_set:
            print('=========================' + convert.mask_name)
            if convert.record_no:
                print(convert_status.record_no)
                pause_job(convert.record_no)
            if convert.stage != 'DB':
                print(convert.stage)
                convert.status = 0
                convert.progress = '0.00%'
                convert.save()
                try:
                    if os.path.exists(convert.location):
                        del_file(convert.location)
                except:
                    print(convert.mask_name + device + '文件删除出错')
                    return 1
            print(convert.mask_name + device + '重置成功')
        # TODO catalog文件删除，lotID的move_back
    catalog_file_path = os.path.join(CATALOG_LOCAL_PATH, mask_name)
    lot_set = lot_info.objects.filter(tip_no=tip_no)
    for lot in lot_set:
        lot.writer_create_file_status = 0
        lot.ftp_upload_status = 0
        lot.catalog_status = 0
        lot.register_status = 0
        lot.register_del_status = 0
        lot.change_status = 0
        lot.writer_op_status = 0
        lot.move_back_status = 0
        lot.save()
    try:
        del_file(catalog_file_path)
    except:
        traceback.print_exc()
        return 2
    try:
        lot = lot_info.objects.get(tip_no=tip_no, mask_name=mask_name, is_delete=0)
        lot.payment_status = 0
        lot.payment_user_id = ''
        lot.payment_user_name = ''
        lot.payment_check_date = None
        lot.dispatch_flag = 0
        lot.release_status = 0
        lot.save()
    except:
        pass
    try:
        if lot.register_status == 3:
            data = move_back_lotID(lot.id)
            if not data['success']:
                return 3
    except:
        traceback.print_exc()
        return 3
    try:
        flag, message = mes_op_locate(lot.lot_id, 'MCDTPC.1', '100.100', 'Affect convert, pull the site back')
        if not flag:
            print(message)
            return 6
    except:
        traceback.print_exc()
        return 5
    return 4



def move_back_lotID(lot_info_id):
    try:
        _lot_info = lot_info.objects.get(id=lot_info_id)

        exp_tool = _lot_info.exp_tool
        tool = _lot_info.info_tree_tool_id

        _tool_maintain = tool_maintain.objects.get(exptool=exp_tool)
        tool_maintain_path = _tool_maintain.path
        catalog_machine_path = tool_maintain_path + '/'
        # catalog_machine_path = os.path.join(tool_maintain_path, Constant.CATALOG_MACHINE_DICT[tool]) + '/'
        print(tool_maintain_path, catalog_machine_path)

        machine_server_path = os.path.join(tool_maintain_path, _lot_info.mask_name)
        print("machine_server_path =", machine_server_path)

        host = _tool_maintain.ip
        username = _tool_maintain.account
        password = _tool_maintain.password

        _o = SSHManager(host, username, password)

        # 　注册指令
        chk_path = os.path.join(machine_server_path, "chk.txt")
        del_path = os.path.join(machine_server_path, "reg_del.txt")
        cmd_data = "Esp_DataDelete -ln " + \
                   _lot_info.mask_name + "-" + _lot_info.mes_lot_family_id + " -yes > " + del_path
        print(cmd_data)
        _o.ssh_exec_cmd(cmd_data)

        if _o.ssh_exec_cmd("find " + machine_server_path + " -name reg_del.txt"):
            cat_file = _o.ssh_exec_cmd("cat " + del_path)
            result = cat_file.split("\n")
            if "Error Detail" in result[0]:
                print("  ", _lot_info.mask_name, "Reg_del fail", cat_file)
                data = {'success': False, 'message': 'move back failed\n' + str(cat_file)}
            else:
                print("  ", _lot_info.mask_name, "Reg_del success")
                _lot_info.catalog_status = 0
                _o.ssh_exec_cmd("rm " + chk_path)
                _o.ssh_exec_cmd("rm " + del_path)
                data = {'success': True, 'message': 'Success'}
        else:
            data = {'success': True, 'message': 'Success but reg_del not find'}

        _o.__del__()
        _lot_info.save()

        return data

    except Exception as e:
        print(e)
        data = {'success': False, 'message': str(e)}
        return data
