# coding:utf-8
import random
import re
import string
import traceback
from datetime import datetime

from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse

from catalog.models import tool_name_route, tool_maintain
from jdv.models import lot_info, lot_trail, mes_blank_code
from jdv.service.create_jb_file_service import create_jb_file
from machine.models import writer_mapping
from maintain.models import pellicle_mapping
from making.models import convert_status_stage, convert_status
from tooling_form.service.tooling_service import upd_tip_no_status
from utilslibrary.base.base import BaseService
from tooling_form.models import file_analysis_info, boolean_info, tapeout_info, product_info, import_list, device_info
from django.core.files.storage import default_storage
from django.shortcuts import render_to_response
from django.core.files.base import ContentFile
import hashlib
import json
from tooling_form.service.check_files_service import CheckFileService
import uuid
from machine.models import machine_basic
from utilslibrary.decorators.catch_exception_decorators import catch_exception
from utilslibrary.mes_webservice.mes_webservice import gen_lots
from utilslibrary.utils.date_utils import getMilliSecond, getDateStr
from utilslibrary.utils.file_utils import *
from utilslibrary.utils.ini_mds_utils import mds, ini


class FtpService(BaseService):

    @catch_exception
    def file_upload_check(self, request):
        """判断文件是否允许上传"""
        if request.method == 'POST':
            tip_no = request.POST.get('tip_no')
            file_name = request.POST.get('file_name')
            count = device_info.objects.filter(tip_no=tip_no, file_name=file_name, is_delete=0).count()
            if count > 0:
                c = file_analysis_info.objects.filter(tip_no=tip_no, file_name=file_name, analysis_status=3,
                                                      analysis_check_status=1, bbox_check_status=1,
                                                      layers_check_status=1, precision_check_status=1,
                                                      topcell_check_status=1).count()
                if c > 0:
                    return JsonResponse({'isAllow': False, 'isSuccess': True}, safe=False)
                else:
                    return JsonResponse({'isAllow': True, 'isSuccess': False}, safe=False)
            return JsonResponse({'isAllow': False, 'isSuccess': False}, safe=False)

    @catch_exception
    def file_upload(self, request):
        """文件分片上传"""
        if request.method == 'POST':
            upload_file = request.FILES.get('file')
            file_name = upload_file.name
            tip_no = request.POST.get('tip_no')
            product = product_info.objects.get(tip_no=tip_no, is_delete=0).product
            device = device_info.objects.filter(tip_no=tip_no, file_name=file_name, is_delete=0).first().device_name
            task = request.POST.get('task_id')  # 获取文件唯一标识符
            chunk = request.POST.get('chunk', 0)  # 获取该分片在所有分片中的序号
            filename = '%s%s' % (task, chunk)  # 构成该分片唯一标识符
            # default_storage.save((self.file_path + '%s/Device/%s/DB/%s') % (product, device, filename),
            #                       ContentFile(upload_file.read()))  # 保存分片到本地
            default_storage.save(join_path(get_db_path(get_work_path(product=product, device=device)), filename),
                                 ContentFile(upload_file.read()))  # 保存分片到本地
            # 更新upload表中的check_status状态
            upd_tip_no_status(tip_no, Constant.CHECK_STATUS_UPLOADING_3)
        return render_to_response('ftp_service.html', locals())

    @catch_exception
    def file_check(self, request):
        """检查文件是否已经上传过"""
        if request.method == 'POST':
            tip_no = request.POST.get('tip_no')
            task_id = request.POST.get('task_id')
            chunk = request.POST.get('chunk', 0)
            chunkSize = request.POST.get('chunkSize')
            file_name = request.POST.get('file_name')
            product = product_info.objects.get(tip_no=tip_no, is_delete=0).product
            device = device_info.objects.filter(tip_no=tip_no, file_name=file_name, is_delete=0).first().device_name
            filename = '%s%s' % (task_id, chunk)  # 构成该分片唯一标识符
            # f_path = (self.file_path + '%s/Device/%s/DB/%s') % (product, device, filename)
            f_path = join_path(get_db_path(get_work_path(product=product, device=device)), filename)
            if os.path.exists(f_path):
                if os.path.getsize(f_path) == int(chunkSize):
                    return {'isExist': True}
            return {'isExist': False}

    @catch_exception
    def file_merge(self, request):
        """文件分片合并方法"""
        tip_no = request.POST.get('tip_no')
        task = request.POST.get('task_id')
        ext = request.POST.get('filename', '')
        upload_type = request.POST.get('type')
        product = product_info.objects.get(tip_no=tip_no, is_delete=0).product
        device = device_info.objects.filter(tip_no=tip_no, file_name=ext, is_delete=0).first().device_name
        if len(ext) == 0 and upload_type:
            ext = upload_type.split('/')[1]
        ext = '' if len(ext) == 0 else '%s' % ext  # 构建文件后缀名
        chunk = 0
        md5Str = hashlib.md5()  # 文件md5值
        sha512Str = hashlib.sha512()
        file_size = 0
        with open(join_path(get_db_path(get_work_path(product=product, device=device)), ext), 'wb') as target_file:  # 创建新文件
            while True:
                try:
                    filename = (get_db_path(get_work_path(product=product, device=device))+'/%s%d') % (task, chunk)
                    source_file = open(filename, 'rb')  # 按序打开每个分片
                    data = source_file.read()
                    md5Str.update(data)  # 分批获取md5值
                    sha512Str.update(data)  # 分批获取sha512的值
                    file_size += os.path.getsize(filename)
                    target_file.write(data)  # 读取分片内容写入新文件
                    source_file.close()
                except IOError:
                    break
                chunk += 1
                os.remove(filename)  # 删除该分片，节约空间
        old_obj = file_analysis_info.objects.filter(tip_no=tip_no, file_name=ext, is_delete=0)
        if old_obj:
            old_obj.delete()
        obj = file_analysis_info.objects.create(tip_no=tip_no, file_name=ext)  # 保存文件信息
        obj.upload_status = 1
        obj.file_md5 = md5Str.hexdigest()
        obj.file_sha512 = sha512Str.hexdigest()
        obj.file_size = file_size
        uid = str(uuid.uuid4())
        suid = ''.join(uid.split('-'))
        obj.result_file_name = suid + '.txt'
        obj.save()
        # 判断是否完成上传
        fis_count = device_info.objects.values('file_name').filter(tip_no=tip_no, is_delete=0).distinct().count()
        fai_count = file_analysis_info.objects.values('file_name').filter(tip_no=tip_no, upload_status=1, is_delete=0).count()
        if fis_count == fai_count:
            upd_tip_no_status(tip_no, Constant.CHECK_STATUS_UPLOADED_4)  # 更新上传完成状态
        return render_to_response('ftp_service.html', locals())

    @catch_exception
    def get_files_list(self, request):
        """获取用户需要上传的文件树"""
        if request.method == 'POST':
            tip_no = request.POST.get('tip_no')
            product = product_info.objects.get(tip_no=tip_no, is_delete=0).product
            fis = device_info.objects.values('file_name').filter(tip_no=tip_no, is_delete=0).distinct()
            fais = file_analysis_info.objects.values('file_name').filter(tip_no=tip_no, upload_status=1, is_delete=0)
            fai_list = list()
            for fai in fais:
                device = device_info.objects.filter(tip_no=tip_no, file_name=fai['file_name'], is_delete=0).first().device_name
                if os.path.exists(join_path(get_db_path(get_work_path(product=product, device=device)), fai['file_name'])):
                    fai_list.append(fai['file_name'])
            lots = tapeout_info.objects.values('mask_name').filter(tip_no=tip_no, is_delete=0)
            d = {'file_list': list(fis), 'finished_file_list': fai_list, 'lot_list': list(lots)}
            return json.dumps(d)

    # @catch_exception
    def check_files_list(self, request):
        """检查文件是否都上传完成"""
        if request.method == 'POST':
            tip_no = request.POST.get('tip_no')
            product = product_info.objects.get(tip_no=tip_no, is_delete=0).product
#             toolingFormName = request.POST.get("toolingFormName")
#             fis = import_data_temp.objects.values('tip_no','import_data').filter(tip_no=tip_no,sheet_name='Device_Info',
            #             column_name='File_Name').distinct()
            mask_list = tapeout_info.objects.filter(tip_no=tip_no, is_delete=0, t_o='Y')
            fis = device_info.objects.values('tip_no', 'file_name').filter(tip_no=tip_no, is_delete=0,
                                                                           mask_name__in=[x.mask_name for x in mask_list]).distinct()
            liList = []
            check_status_flag = True
            for fi in list(fis):
                device = device_info.objects.filter(tip_no=tip_no, file_name=fi['file_name'], is_delete=0).first().device_name
                flag, msg, color = CheckFileService().check_file(join_path(get_db_path(get_work_path(product=product,
                                                                                                     device=device)),
                                                                           fi['file_name']), fi['tip_no'],
                                                                 fi['file_name'])
                check_status_flag = check_status_flag & flag
                liList.append({'li': '<li check_flag = "%d' % flag + '" style="font-weight:bold">' + fi['file_name'] +
                                     '&nbsp;&nbsp;<label style="color:' + color+'">' + msg + '</label></li>'})
            # 判断是否文件都校验成功
            fis_count = device_info.objects.values('file_name').filter(tip_no=tip_no, is_delete=0).distinct().count()
            fai_count = file_analysis_info.objects.values('file_name').filter(tip_no=tip_no, upload_status=1, is_delete=0).count()
            if fis_count == fai_count:
                if check_status_flag:
                    upd_tip_no_status(tip_no, Constant.CHECK_STATUS_FTP_CHECK_SUCCESS_6)  # 更新校验成功状态
                else:
                    upd_tip_no_status(tip_no, Constant.CHECK_STATUS_FTP_CHECK_FAIL_5)  # 更新校验失败状态
            return json.dumps(liList)

    def done(self, request):
        """判断文件是否都校验通过"""
        need_done_tapeout_num = 0
        try:
            tip_no = request.POST.get('tip_no')
            t_list = tapeout_info.objects.filter(tip_no=tip_no, t_o='Y', is_delete=0, is_done=0)
            m_n_list = []
            for t in t_list:
                m_n_list.append(t.mask_name)
            dis_list = device_info.objects.values("file_name").filter(tip_no=tip_no, mask_name__in=m_n_list, is_delete=0).distinct()
            dis_count = dis_list.count()
            d_f_list = []
            for d in dis_list:
                d_f_list.append(d['file_name'])
            fais_count = file_analysis_info.objects.filter(tip_no=tip_no, analysis_status=3, analysis_check_status=1,
                                                           bbox_check_status=1, layers_check_status=1,
                                                           precision_check_status=1, topcell_check_status=1,
                                                           is_delete=0, file_name__in=d_f_list).count()
            u = import_list.objects.filter(tip_no=tip_no, is_delete=0).first()
            if u.status >= 7:
                return JsonResponse({'success': False, 'message': 'Already done'}, safe=False)
            if dis_count != fais_count:
                return JsonResponse({'success': False, 'message': 'file check failed, please check first'}, safe=False)
            else:
                with transaction.atomic():
                    save_id = transaction.savepoint()
                    p_info = product_info.objects.get(tip_no=tip_no, is_delete=0)
                    user_id = request.session.get(Constant.SESSION_CURRENT_USER_ID)
                    user_name = request.session.get(Constant.SESSION_CURRENT_USER_LOGINNAME)
                    # t_list = tapeout_info.objects.filter(tip_no=tip_no, t_o='Y', is_delete=0, is_done=0)
                    need_done_tapeout_num = len(t_list)
                    lot_list = list()
                    for t in t_list:
                        light_sourse = t.light_sourse
                        wave_length = re.search(r'\d+', light_sourse).group()
                        _layer_name = t.mask_name[-5:]
                        b_info = boolean_info.objects.filter(tip_no=tip_no,
                                                             mask_name=t.mask_name, is_delete=0).first()  # 每个mask_name的tone是固定的
                        lot_info.objects.filter(tip_no=tip_no, mask_name=t.mask_name).delete()
                        lot = lot_info(tip_no=tip_no, product_name=p_info.product, mask_name=t.mask_name,
                                       ready_date=datetime.now(), expire_date=datetime.now(),
                                       lot_owner_id=user_id, lot_owner_name=user_name,
                                       customer=p_info.customer, rule=p_info.design_rule, type=t.mask_type,
                                       clip=t.layer_name, tone=b_info.tone, grade=t.grade)
                        w_m, t_m = mapping_dispatch(lot, p_info.product_type)  # 匹配EXPTOOL值
                        if w_m:
                            lot.exp_tool_id = w_m.id
                            lot.exp_tool = t_m.exptool
                            lot.machine_id = t_m.id
                            lot.info_tree_tool_id = w_m.info_tree_tool_id
                        else:
                            transaction.savepoint_rollback(save_id)  # 回滚事务
                            return JsonResponse({'success': False, 'message': '未匹配到exptool'},
                                                safe=False)
                        b_c = mapping_blank_code(lot)  # 匹配Blank_Code值
                        if b_c:
                            lot.blank_code = b_c.blank_code
                            lot.wavelength = wave_length
                        else:
                            transaction.savepoint_rollback(save_id)  # 回滚事务
                            return JsonResponse({'success': False, 'message': '未匹配到blankcode'},
                                                safe=False)
                        if not t.pellicle:  # 判断pellicle值是否存在
                            transaction.savepoint_rollback(save_id)  # 回滚事务
                            return JsonResponse({'success': False, 'message': '未找到到Pellicle_Code参数'},
                                                safe=False)
                        else:
                            p_m_list = pellicle_mapping.objects.filter(mt_form_pellicle=t.pellicle, is_delete=0)
                            if len(p_m_list) == 1:
                                pellicle_code = p_m_list.first().mes_pellicle_code
                                lot.pellicle_code = pellicle_code
                            else:
                                transaction.savepoint_rollback(save_id)
                                return JsonResponse({'success': False, 'message': 'pellicle match failed'}, safe=False)
                        lot_list.append(lot)
                        # 删除convert_status
                        convert_status.objects.filter(tip_no=tip_no, mask_name=t.mask_name).delete()
                        # 生成convert_status相关信息
                        device_list = device_info.objects.values("device_type", "file_name",
                                                                 "device_name").filter(tip_no=tip_no,
                                                                                       mask_name=t.mask_name,
                                                                                       is_delete=0).distinct()
                        for device in device_list:
                            if device['device_type'] == 'Frame' or device['device_type'] == 'F+M':
                                stage_list = convert_status_stage.objects.filter(type=1)
                            else:
                                stage_list = convert_status_stage.objects.filter(device_type=device['device_type'], type=1)
                            for stage in stage_list:
                                if stage.stage_name == Constant.MAKING_CONVERT_STATUS_STAGE_NAME_DB:
                                    status = 2
                                    file_name = device['file_name']
                                    location = get_db_path(
                                        get_work_path(product=p_info.product, device=device['device_name'], mak=1), mak=1)
                                elif stage.stage_name == Constant.MAKING_CONVERT_STATUS_STAGE_NAME_FRACTURE:
                                    status = 0
                                    #query machine type
                                    _machine = tool_name_route.objects.get(id=lot.machine_id)
                                    file_name = get_fracture_file_name(p_info.product, _layer_name,
                                                                       device['device_name'], _machine.machine_type)
                                    location = get_fracture_path(
                                        get_work_path(product=p_info.product, device=device['device_name'],
                                                      layer=_layer_name, mak=1), mak=1)
                                elif stage.stage_name == Constant.MAKING_CONVERT_STATUS_STAGE_NAME_XOR:
                                    status = 0
                                    file_name = get_fracture_xor_file_name(p_info.product, _layer_name,
                                                                           device['device_name'])
                                    location = get_fracture_XOR_path(
                                        get_fracture_path(
                                            get_work_path(product=p_info.product, device=device['device_name'],
                                                          layer=_layer_name,
                                                          mak=1), mak=1), mak=1)
                                elif stage.stage_name == Constant.MAKING_CONVERT_STATUS_STAGE_NAME_WRITER:
                                    status = 0
                                    file_name = ''
                                    location = ''

                                convert_status.objects.create(tip_no=tip_no, mask_name=t.mask_name,
                                                              device_name=device['device_name'],
                                                              stage_id=stage.id, stage=stage.stage_name,
                                                              status=status, operation_status=0,
                                                              file_name=file_name, location=location)
                                # 更新tapeout_info的done状态
                                tapeout_info.objects.filter(tip_no=tip_no, mask_name=t.mask_name,
                                                            t_o='Y', is_delete=0, is_done=0).update(is_done=1)
                    lot_info.objects.bulk_create(lot_list)
                    transaction.savepoint_commit(save_id)  # 提交事务
                if need_done_tapeout_num > 0:
                    lot_flag, lot_message = gen_lots(tip_no)   # 提交mes生成lot请求
                    if lot_flag:
                        lot_info.objects.filter(tip_no=tip_no, status=0, is_delete=0).update(status=1,
                                                                                             status_dec=lot_message)
                    else:  # 访问MES失败
                        lot_info.objects.filter(tip_no=tip_no, status=0, is_delete=0).update(status=2,
                                                                                             status_dec=lot_message)
                        return JsonResponse({'success': False, 'message': 'MES Error:' + lot_message}, safe=False)
                upd_tip_no_status(tip_no, Constant.CHECK_STATUS_FTP_DONE_7)  # 更新upload表done状态
                # ini(tip_no)  # 生成ini文件
                # mds(tip_no)  # 生成mds文件
                # create_jb_file(tip_no)  # 生成jb文件
                return JsonResponse({'success': True, 'message': 'Lot_id gen success'}, safe=False)
        except Exception as e:
            transaction.savepoint_rollback(save_id)
            traceback.print_exc()
            return JsonResponse({"success": True, 'message': str(e)}, safe=False)

    def create_lot_id(self, request):
        """判断文件是否都校验通过"""
        tip_no = request.POST.get('tip_no')
        lot_list = gen_lot_id(tip_no)
        # lot_flag, lot_message = gen_lots(tip_no)
        p_info = product_info.objects.get(tip_no=tip_no, is_delete=0)
        user_id = request.session.get(Constant.SESSION_CURRENT_USER_ID)
        user_name = request.session.get(Constant.SESSION_CURRENT_USER_LOGINNAME)
        create_jb_file(tip_no)  # 生成jb文件
        for lot in lot_list:
            _layer_name = lot['mask_name'][-5:]
            l = lot_info.objects.create(tip_no=tip_no, product_name=p_info.product, lot_id=lot['lot_id'],
                                        mask_name=lot['mask_name'], ready_date=datetime.now(),
                                        expire_date=datetime.now(), lot_owner_id=user_id,
                                        lot_owner_name=user_name, customer=p_info.customer, rule=p_info.design_rule,
                                        type=lot['mask_type'], clip=lot['layer_name'], tone=lot['tone'],
                                        grade=lot['grade'])
            w_m, t_m = mapping_dispatch(l, p_info.product_type)
            if w_m:
                l.exp_tool_id = w_m.id
                l.exp_tool = t_m.exptool
                l.machine_id = t_m.id
                lot.info_tree_tool_id = w_m.info_tree_tool_id
                l.save()
            # 生成lot轨迹
            lot_trail.objects.create(lot_id=l.id, stage='Gen LotID', stage_desc="生成LotID",
                                     stage_start_date=datetime.now(), stage_end_date=datetime.now(),
                                     operator_id=user_id, operator_name=user_name, operate_date=datetime.now(),
                                     remark='', create_time=getMilliSecond(), create_date=getDateStr())
            # 生成convert_status相关信息
            device_list = device_info.objects.values("device_type", "file_name",
                                                     "device_name").filter(tip_no=tip_no,
                                                                           is_delete=0).distinct()
            for device in device_list:
                if device['device_type'] == 'Frame' or device['device_type'] == 'F+M':
                    stage_list = convert_status_stage.objects.filter(type=1)
                else:
                    stage_list = convert_status_stage.objects.filter(device_type=device['device_type'], type=1)
                for stage in stage_list:
                    if stage.stage_name == Constant.MAKING_CONVERT_STATUS_STAGE_NAME_DB:
                        status = Constant.CONVERT_STATUS_DONE
                        file_name = device['file_name']
                        location = get_db_path(
                            get_work_path(product=p_info.product, device=device['device_name'], mak=1), mak=1)
                    elif stage.stage_name == Constant.MAKING_CONVERT_STATUS_STAGE_NAME_FRACTURE:
                        status = Constant.CONVERT_STATUS_WAIT
                        # query machine type
                        _machine = tool_name_route.objects.get(id=w_m.machine_id)
                        file_name = get_fracture_file_name(p_info.product, _layer_name, device['device_name'],
                                                           _machine.machine_type)

                        location = get_fracture_path(
                            get_work_path(product=p_info.product, device=device['device_name'], layer=_layer_name,
                                          mak=1), mak=1)
                    elif stage.stage_name == Constant.MAKING_CONVERT_STATUS_STAGE_NAME_XOR:
                        status = Constant.CONVERT_STATUS_WAIT
                        file_name = get_fracture_xor_file_name(p_info.product, _layer_name, device['device_name'])
                        location = get_fracture_XOR_path(
                            get_fracture_path(
                                get_work_path(product=p_info.product, device=device['device_name'], layer=_layer_name,
                                              mak=1), mak=1), mak=1)
                    elif stage.stage_name == Constant.MAKING_CONVERT_STATUS_STAGE_NAME_WRITER:
                        status = Constant.CONVERT_STATUS_WAIT
                        file_name = ''
                        location = ''

                    convert_status.objects.create(tip_no=tip_no, mask_name=lot['mask_name'], lot_id=lot['lot_id'],
                                                  device_name=device['device_name'], stage_id=stage.id,
                                                  stage=stage.stage_name, status=status,
                                                  operation_status=Constant.CONVERT_OPERATION_RELEASE, file_name=
                                                  file_name, location=location.replace('\\', '/'))

        return JsonResponse({'success': True, 'message': 'Lot_id gen success'}, safe=False)


def gen_lot_id(tip_no):
    """生成LOTID"""
    l = []
    t_list = tapeout_info.objects.filter(tip_no=tip_no, t_o='Y', is_delete=0)
    for t in t_list:
        b_info = boolean_info.objects.filter(tip_no=tip_no, mask_name=t.mask_name, is_delete=0).first()  # 每个mask_name的tone是固定的
        l.append({'lot_id': ''.join(random.sample(string.ascii_letters + string.digits, 6)), 'mask_name': t.mask_name,
                  'grade': t.grade, 'mask_type': t.mask_type, 'layer_name': t.layer_name, 'tone': b_info.tone})
    return l


def mapping_dispatch(l, product_type):
    """匹配lot对应的writer信息"""
    w_m = writer_mapping.objects.order_by('seq').filter(Q(customer=l.customer) | Q(customer='*'),
                                                        Q(design_rule=l.rule) | Q(design_rule='*'),
                                                        Q(product=l.product_name) | Q(product='*'),
                                                        Q(layer_name=l.clip.split('.')[0]) | Q(layer_name='*'),
                                                        Q(product_type=product_type) | Q(product_type='*'),
                                                        Q(mask_type=l.type) | Q(mask_type='*'),
                                                        Q(tone=l.tone) | Q(tone='*'),
                                                        grade_from__lte=l.grade,
                                                        grade_to__gte=l.grade,
                                                        is_delete=0
                                                        # grade_from__in=[chr(x) for x in range(65, 91)],
                                                        )
    print(l.customer, l.rule, l.product_name, l.clip.split('.')[0], product_type, l.type, l.tone, l.grade)
    t_m = tool_maintain.objects.get(tool_id=w_m.first().catalog_tool_id)
    return w_m.first(), t_m


def mapping_blank_code(l):
    b_c = mes_blank_code.objects.order_by('seq').filter(Q(customer=l.customer) | Q(customer='*'),
                                                        Q(design_rule=l.rule) | Q(design_rule='*'),
                                                        Q(layer_name=l.clip) | Q(layer_name='*'),
                                                        Q(mask_type=l.type) | Q(mask_type='*'),
                                                        Q(tone=l.tone) | Q(tone='*'),
                                                        grade_from__lte=l.grade,
                                                        grade_to__gte=l.grade,
                                                        is_delete=0
                                                        )
    return b_c.first()


def get_inspection_type():
    """获取inspection_type"""
    pass
