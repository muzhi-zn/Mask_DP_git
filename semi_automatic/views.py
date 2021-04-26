import ftplib
import logging
import os
import time
import traceback

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from Mask_DP.settings import MES_USER
from catalog.alta_catalog import create_wr, get_local_path_list
from utilslibrary.mes_webservice.mes_base_webservice import MES_TxExTIPLayerDataParmInqForLotID
from utilslibrary.system_constant import Constant
# Create your views here.
from catalog.alta_catalog import create_wr, get_local_path_list
from catalog.models import tool_maintain
from maintain.models import customer_code
from semi_automatic.models import lot_record, writer_ftp_record, catalog_record
from semi_automatic.services import query_mes_lot
from utilslibrary.base.base import BaseView
from utilslibrary.utils.sftp_utils import sftp_upload
from utilslibrary.utils.ssh_utils import SSHManager

log = logging.getLogger('log')


class LotRecordList(BaseView):

    def get(self, request):
        return render(request, "semi_automatic/lot_record_list.html")

    def post(self, request):
        """获取lot的记录"""
        super().post(request)
        q = Q()
        q.connector = "and"
        q.children.append(('is_delete', 0))
        tip_no = request.POST.get("tip_no")
        if tip_no:
            q.children.append(("tip_no", tip_no))
        mask_name = request.POST.get("mask_name")
        if mask_name:
            q.children.append(("mask_name", mask_name))
        lot_id = request.POST.get("lot_id")
        if lot_id:
            q.children.append(("lot_id", lot_id))
        customer_code = request.POST.get("customer_code")
        if customer_code:
            q.children.append(("customer_code", customer_code))
        lot_record_list = lot_record.objects.filter(q).values()
        count = lot_record_list.count()
        data = {'total': count, 'rows': list(lot_record_list)[self.startIndex: self.endIndex]}
        return JsonResponse(data)


class LotRecordAdd(BaseView):

    def get(self, request):
        return render(request, "semi_automatic/lot_record_add.html")

    def post(self, request):
        tip_no = request.POST.get("tip_no")
        mask_name = request.POST.get("mask_name")
        if not tip_no or not mask_name:
            return JsonResponse({"success": False, "message": "tip_no和mask_name不能为空"})
        layer = request.POST.get("layer")
        tone = request.POST.get("tone")
        grade = request.POST.get("grade")
        tip_tech = request.POST.get("tip_tech")
        product_type = request.POST.get("product_type")
        customer_code = request.POST.get("customer_code")
        purpose = request.POST.get("purpose")
        order_type = request.POST.get("order_type")
        exp_tool = request.POST.get("exp_tool")
        blank_code = request.POST.get("blank_code")
        pellicle_code = request.POST.get("pellicle_code")
        design_rule = request.POST.get("design_rule")
        delivery_fab = request.POST.get("delivery_fab")
        wavelength = request.POST.get("wavelength")
        l_r = lot_record()
        l_r.tip_no = tip_no
        l_r.mask_name = mask_name
        l_r.layer = layer
        l_r.tone = tone
        l_r.grade = grade
        l_r.tip_tech = tip_tech
        l_r.product_type = product_type
        l_r.customer_code = customer_code
        l_r.purpose = purpose
        l_r.order_type = order_type
        l_r.exp_tool = exp_tool
        l_r.blank_code = blank_code
        l_r.pellicle_code = pellicle_code
        l_r.design_rule = design_rule
        l_r.delivery_fab = delivery_fab
        l_r.wave_length = wavelength
        query_flag = query_mes_lot(l_r)  # 调用MES接口查询lot相关信息
        if query_flag:
            return JsonResponse({'success': True, 'message': '成功获取到对应的Lot ID'})
        else:
            return JsonResponse({'success': False, 'message': '查询失败，未获取到对应的Lot ID'})


class InsertLot(BaseView):

    def get(self, request):
        return render(request, "semi_automatic/lot_record_insert_lot.html")

    def post(self, request):
        """根据lotID插入数据"""
        flag = False
        lot_id = request.POST.get("lot_id")
        l_r = lot_record()
        result = MES_TxExTIPLayerDataParmInqForLotID(MES_USER, lot_id)
        if result:
            message = result.strResult.messageText
            if result.strResult.returnCode == '0':  # 请求成功
                for layerData in result.strExTIPLayerData.item:
                    tip_no = layerData.tipNO
                    for layerDataInfo in layerData.strExTIPLayerDataInfoSequence.item:
                        lot_created_status = layerDataInfo.lotCreatedStatus
                        res = layerDataInfo.result
                        lot_id = layerDataInfo.lotID
                        mask_name = layerDataInfo.partName
                        tone = layerDataInfo.tone
                        tip_tech = layerDataInfo.tipTech
                        grade = layerDataInfo.grade
                        product_type = layerDataInfo.productType
                        customer_id = layerDataInfo.customerID
                        if lot_created_status == 'Pass':
                            if lot_id:
                                # 获取UDATA数据
                                for udata in layerDataInfo.strExTIPLayerData_ParamSequence.item:
                                    if udata.name == "DP_DESIGN_RULE":
                                        l_r.design_rule = udata.value
                                    if udata.name == "DP_EXPTOOL":
                                        l_r.exp_tool = udata.value
                                    if udata.name == "DP_DELIVERY_FAB":
                                        l_r.delivery_fab = udata.value
                                    if udata.name == "DP_BLANK_CODE":
                                        l_r.blank_code = udata.value
                                    if udata.name == "DP_PELLICLE_CODE":
                                        l_r.pellicle_code = udata.value
                                    if udata.name == "DP_WAVELENGTH":
                                        l_r.wave_length = udata.value
                                l_r.lot_id = lot_id
                                l_r.lot_result = res
                                l_r.tip_no = tip_no
                                l_r.mask_name = mask_name
                                l_r.customer_code = customer_id
                                l_r.tip_tech = tip_tech
                                l_r.tone = tone
                                l_r.grade = grade
                                l_r.product_type = product_type
                                l_r.save()
                                flag = True
                        #     else:
                        #         pass
                        # elif 'ERR' in lot_created_status:
                        #     l_r.lot_id = lot_id
                        #     pass
                        # else:  # 其余状态先更新数据库
                        #     pass
        if flag:
            return JsonResponse({'success': True, 'message': 'insert success'})
        else:
            return JsonResponse({'success': False, 'message': '未查询到对应的lotID'})


class LotRecordFtp(BaseView):

    def get(self, request):
        id = request.GET.get("id")
        return render(request, "semi_automatic/lot_record_ftp_form.html", {'id': id})

    def post(self, request):
        """执行FTP操作"""
        id = request.POST.get('id')
        l_r = lot_record.objects.get(pk=id)
        layer = request.POST.get('layer')
        local_path = request.POST.get('path')
        level = request.POST.get('level')
        patten = request.POST.get('patten')
        l_r.layer = layer
        l_r.writer_local_path = local_path
        l_r.level = level
        l_r.save()
        # 执行上传操作
        query_set = writer_ftp_record.objects.filter(lot_record_id=id, is_delete=0, level=level)
        if query_set:
            for query in query_set:
                query.is_delete = 1
                query.save()
        w_f_r = writer_ftp_record()
        w_f_r.lot_id = l_r.lot_id
        w_f_r.lot_record_id = id
        w_f_r.level = level
        w_f_r.writer_ftp_status = 1
        w_f_r.writer_local_path = local_path
        w_f_r.writer_ftp_start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        w_f_r.save()
        ftp = ftplib.FTP
        host = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_HOST']
        ftp_port = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_PORT']
        username = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_ACCOUNT']
        password = Constant.CATALOG_FTP_SERVER_CONN_CONFIG['CATALOG_FTP_PASSWORD']
        machine_query = tool_maintain.objects.get(tool_id='MWLBA01')
        machine_host = machine_query.ip
        machine_username = machine_query.account
        machine_password = machine_query.password
        machine_path = machine_query.path
        print(host, ftp_port, username, password)

        f = ftp()
        f.encoding = "utf-8"
        f.connect(host, ftp_port)
        f.login(username, password)
        f.set_pasv(0)
        bufsize = 1024
        query = lot_record.objects.get(id=id)
        query_ftp = writer_ftp_record.objects.get(lot_record_id=l_r.id, is_delete=0, level=level)
        product_name = l_r.mask_name.split('-')[0]
        code = l_r.customer_code
        if level == '1' or level == '0':
            writer_name = 'Writerjob'
        else:
            writer_name = '2ndjob'
        ftp_remote_path = '/DTS/PRODUCT/{}/{}/{}/{}/'.format(code, product_name, writer_name, layer)
        log.info('ftp_remote_path=' + ftp_remote_path)
        machine_remote_path = os.path.join(machine_path,
                                           '{}/{}/{}/{}/'.format(code, product_name, writer_name, layer))
        log.info('machine_remote_path=' + machine_remote_path)
        flag = create_wr(local_path, query.mask_name, query, level, ftp_remote_path, patten)
        log.info(str(flag))
        if flag:
            try:
                f_1 = SSHManager(host, username, password, True)
                log.info('f_1')
                f_2 = SSHManager(machine_host, machine_username, machine_password)
                log.info('f_2')
                f_2.ftp_rmd_file(machine_remote_path)
                log.info('f_2 rmd')
                try:
                    f_1.ftp_rmd_file(ftp_remote_path)
                    log.info('f_1 rmd')
                except:
                    log.info('f_1 file not exist')
                f_1.__del__()
                log.info(local_path)
                f_2._mkdirs(machine_remote_path)
                file_list = get_local_path_list([local_path])
                try:
                    f.cwd(ftp_remote_path)  # 切换工作路径
                except Exception as e:
                    f.cwd('/')  # 切换到远程根目录下(不一定时盘符, 服务器)
                    base_dir, part_path = f.pwd(), ftp_remote_path.split('/')  # 分割目录名
                    for p in part_path[1:-1]:  # 根据实际target_dir决定切片位置, 如果是目录, 使用[1:], 文件绝对路径使用[1:-1], 列表第0个切割之后为空串
                        base_dir = os.path.join(base_dir, p)  # 拼接子目录
                        try:
                            f.cwd(base_dir)  # 切换到子目录, 不存在则异常
                        except Exception as e:
                            print('INFO:', e)
                            f.mkd(base_dir)
                log.info(str(file_list))
                for file in file_list:
                    fp = open(file, 'rb')
                    log.info(ftp_remote_path)
                    ftp_file_path = os.path.join(ftp_remote_path, os.path.basename(file))
                    log.info(ftp_file_path)
                    f.storbinary('STOR ' + ftp_file_path, fp, bufsize)
                    log.info('ftp file' + os.path.join(ftp_remote_path, os.path.basename(file)))
                    fp.close()
                    try:
                        f_2._upload_file(file, os.path.join(machine_remote_path, os.path.basename(file)))
                        log.info('ftp file to machine' + machine_remote_path)
                    except Exception as e:
                        traceback.print_exc()
                        query_ftp.ftp_status = 3
                        query_ftp.error_msg = str(e)
                        query_ftp.save()
                f_2.__del__()
                query_ftp.ftp_status = 2
                query_ftp.writer_ftp_end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                query_ftp.save()
                return JsonResponse({'success': True, 'message': 'Ftp success'})
            except Exception as e:
                traceback.print_exc()
                query_ftp.ftp_status = 3
                query_ftp.error_msg = str(e)
                query_ftp.save()
                return JsonResponse({'success': False, 'message': str(e)})
        else:
            query_ftp.ftp_status = 3
            query_ftp.error_msg = 'create file failed or jb file not found'
            query_ftp.save()
            return JsonResponse({"success": False, 'message': 'create file failed or jb file not found'})


class LotRecordCatalog(BaseView):

    def get(self, request):
        id = request.GET.get("id")
        return render(request, "semi_automatic/lot_record_catalog_form.html", {'id': id})

    def post(self, request):
        """执行编锅操作"""
        try:
            id = request.POST.get('id')
            l_r = lot_record.objects.get(pk=id)
            level = request.POST.get('level')
            product_name = l_r.mask_name.split('-')[0]
            layer_name = l_r.mask_name.split('-')[-1]
            code = l_r.customer_code
            c_c_r = catalog_record.objects.filter(lot_record_id=id, is_delete=0, catalog_status=3, level=level)
            if c_c_r:
                return JsonResponse({"success": False,
                                     'msg': '{} has been compiled successfully, please do not repeat the operation'.format(
                                         l_r.lot_id)})
            c_r = catalog_record.objects.filter(lot_record_id=id, level=level, is_delete=0)
            if c_r:
                for query in c_r:
                    query.is_delete = 1
                    query.save()
            machine_query = tool_maintain.objects.get(tool_id='MWLBA01')
            machine_host = machine_query.ip
            machine_username = machine_query.account
            machine_password = machine_query.password
            machine_path = machine_query.path
            if level == '1' or level == '0':
                writer_name = 'Writerjob'
            else:
                writer_name = '2ndjob'
            machine_remote_path = os.path.join(machine_path,
                                               '{}/{}/{}/{}/'.format(code, product_name, writer_name, layer_name))
            f_2 = SSHManager(machine_host, machine_username, machine_password)
            f_2.ssh_exec_cmd('wmgr -command -c {}_{}_WR'.format(l_r.mask_name, level), machine_remote_path)
            f_2.__del__()
            return JsonResponse({'success': True, 'msg': 'Catalog Success'}, safe=False)
        except:
            traceback.print_exc()
            return JsonResponse({"success": False, 'msg': 'Catalog Failed'}, safe=False)


@csrf_exempt
def get_ftp_record_list(request):
    """获取ftp记录"""
    lot_record_id = request.POST.get("lot_record_id")
    f_r_list = writer_ftp_record.objects.filter(is_delete=0, lot_record_id=lot_record_id).values()
    return JsonResponse({'data': list(f_r_list)})


@csrf_exempt
def get_catalog_record_list(request):
    """获取catalog的操作记录"""
    lot_record_id = request.POST.get("lot_record_id")
    c_r_list = catalog_record.objects.filter(is_delete=0, lot_record_id=lot_record_id)
    return JsonResponse({'data': list(c_r_list)})
