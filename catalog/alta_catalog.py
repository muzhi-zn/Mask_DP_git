import ftplib
import logging
import os
import traceback
from urllib import request

from django.http import JsonResponse
from django.shortcuts import render

from catalog.models import tool_maintain
from infotree.models import released_info_alta
from maintain.models import customer_code
from semi_automatic.models import lot_record, catalog_record, writer_ftp_record
from utilslibrary.base.base import BaseView
from utilslibrary.system_constant import Constant
from utilslibrary.utils.ssh_utils import SSHManager

log = logging.getLogger('log')


def get_local_path_list(path_list):
    file_list = []
    log.info(path_list)
    for local_path in path_list:
        # for fpathe, dirs, fs in os.walk(local_path):
        #     for f in fs:
        #         file_list.append(f)
        for item in os.listdir(local_path):
            if os.path.isfile(os.path.join(local_path, item)):
                file_list.append(os.path.join(local_path, item))
    log.info(file_list)
    return file_list


# class alta_ftp_add(BaseView):
#     def get(self, request):
#         return render(request, '')
#
#     def post(self, request):
#         lot_id = request.POST.get('lot_id')
#         lot_id_list = lot_id.split(',')
#         level = request.POST.get('level')
#         data_list = []
#         exist_list = []
#         for lot in lot_id_list:
#             query_set = alta_catalog_queue.objects.filter(lot_id=lot, level=level)
#             if query_set.count() == 0:
#                 _o = alta_catalog_queue()
#                 _o.lot_id = lot
#                 _o.level = level
#                 data_list.append(_o)
#             else:
#                 exist_list.append(lot)
#                 continue
#         try:
#             alta_catalog_queue.objects.bulk_create(data_list)
#             if len(exist_list) != 0:
#                 msg = '{} already exists, cannot be added repeatedly, others have been added to the upload queue'.format(
#                     exist_list)
#             else:
#                 msg = 'The operation is successful, please wait'
#             data = {'success': True, 'msg': msg}
#             return JsonResponse(data=data, safe=False)
#         except:
#             traceback.print_exc()
#             data = {'success': True, 'msg': 'Failed'}
#             return JsonResponse(data=data, safe=False)


def alta_ftp_job(request):
    lot_id = request.POST.get('lot_id')
    level = request.POST.get('level')
    path = request.POST.get('path')
    # query_set = alta_catalog_queue.objects.filter(is_delete=0, ftp_status=0)
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
    # for query in query_set:
    #     lot_dict[query.lot_id] = query.level
    #     query.ftp_status = 1
    #     query.save()
    query = lot_record.objects.get(lot_id=lot_id)
    query_ftp = writer_ftp_record.objects.get(lot_id=lot_id, level=level)
    query.save()
    query = lot_record.objects.get(lot_id=lot_id)
    product_name = query.mask_name.split('-')[0]
    layer_name = query.mask_name.split('-')[-1]
    code = customer_code.objects.get(customer=query.customer_id)
    local_path = query.writer_local_path
    if level == 1 or level == 0:
        writer_name = 'Writerjob'
    else:
        writer_name = '2ndjob'
    ftp_remote_path = '/DTS/PRODUCT/{}/{}/{}/{}/'.format(code, product_name, writer_name, layer_name)
    log.info('ftp_remote_path=' + ftp_remote_path)
    machine_remote_path = os.path.join(machine_path,
                                       '{}/{}/{}/{}/'.format(code, product_name, writer_name, layer_name))
    log.info('machine_remote_path=' + machine_remote_path)
    flag = create_wr(local_path, query.mask_name, query, level, ftp_remote_path)
    f_2 = SSHManager(machine_host, machine_username, machine_password)
    if flag:
        try:
            file_list = get_local_path_list(local_path)
            # for dir in dir_list:
            #     f.mkd(os.path.join(ftp_remote_path, dir))
            #     f_2._mkdir(dir)
            for file in file_list:
                fp = open(file, 'rb')
                ftp_file_path = os.path.join(ftp_remote_path, os.path.basename(file))
                f.storbinary('STOR ' + ftp_file_path, fp, bufsize)
                fp.close()
                try:
                    f_2._upload_file(file, machine_remote_path)
                    f_2.__del__()
                except Exception as e:
                    traceback.print_exc()
                    query_ftp.ftp_status = 3
                    query_ftp.error_msg = str(e)
                    query_ftp.save()
            query_ftp.ftp_status = 2
            query_ftp.save()
        except Exception as e:
            traceback.print_exc()
            query_ftp.ftp_status = 3
            query_ftp.error_msg = str(e)
            query_ftp.save()
        else:
            query_ftp.ftp_status = 3
            query_ftp.error_msg = 'create file failed or jb file not found'
            query_ftp.save()


def create_wr(local_path, mask_name, query, level, remote_path, patten):
    try:
        customer = query.customer_code
        tool = 'MS03'
        node = query.tip_tech
        grade = query.grade
        tone = query.tone
        blank = query.blank_code
        # patten = '0-100'
        layer = query.layer
        # local_job_path = '/DATA/MaskDP/Product/AMEC/{}/Writer/{}_Writerjob'.format(mask_name, mask_name)
        log.info('local_job_path=' + local_path)
        jb_name = ''
        if os.path.exists(local_path):
            for fpathe, dirs, fs in os.walk(local_path):
                for f in fs:
                    if '.jb' in f:
                        jb_name = f
            if jb_name:
                if level == '0' or level == '1':
                    log.info(customer)
                    log.info(tool)
                    log.info(node)
                    log.info(grade)
                    log.info(blank)
                    log.info(tone)
                    log.info(layer)
                    log.info(level)
                    log.info(patten)
                    i_f_set = released_info_alta.objects.filter(customer=customer, tool=tool, node=node, grade=grade,
                                                                blank=blank,
                                                                tone=tone, layer=layer, level=level,
                                                                pattern_density=patten,
                                                                type='Create file', is_delete=0)

                    dose = i_f_set.get(item='dose')
                    offset = i_f_set.get(item='PrintFocusOffset')
                    bias = i_f_set.get(item='XYBias')
                    mode = i_f_set.get(item='PrintMode')
                    template = 'name:{}\n'.format(mask_name) + 'level:{}\n'.format(level) + 'jobdeck:{}\n'.format(
                        jb_name) + 'pathset:”qxic” “{}”\n'.format(
                        remote_path)
                    # template.replace('AAA', mask_name).replace('BBB', level).replace('CCC', jb_name).replace('DDD',
                    #                                                                                          remote_path)
                    log.info('22222222222222')
                    if dose.value != 'NA':
                        template = template + 'dose:{}\n'.format(dose.value)
                    if offset.value != 'NA':
                        template = template + 'PrintFocusOffset:{}\n'.format(offset.value)
                    if bias.value != 'NA':
                        template = template + 'XYBias:{}\n'.format(bias.value)
                    if mode.value != 'NA':
                        template = template + 'PrintMode:{}\n'.format(mode.value)
                else:
                    i_f_set = released_info_alta.objects.filter(customer=customer, tool=tool, node=node, grade=grade,
                                                                blank=blank,
                                                                tone=tone, layer=layer, level=level,
                                                                pattern_density=patten,
                                                                type='Create file', is_delete=0)
                    dose = i_f_set.get(item='dose')
                    offset = i_f_set.get(item='PrintFocusOffset')
                    bias = i_f_set.get(item='XYBias')
                    mode = i_f_set.get(item='PrintMode')
                    acyion = i_f_set.get(item='ManualAlignAction')
                    template = 'name:{}\n level:2\n jobdeck:{}\n pathset:”qxic” “{}”\n'.format(mask_name,
                                                                                                           jb_name,
                                                                                                           remote_path)
                    # template.replace('AAA', mask_name).replace('CCC', jb_name).replace('DDD', remote_path)
                    if dose.value != 'NA':
                        template = template + 'dose:{}\n'.format(dose.value)
                    if offset.value != 'NA':
                        template = template + 'PrintFocusOffset:{}\n'.format(offset.value)
                    if bias.value != 'NA':
                        template = template + 'XYBias:{}\n'.format(bias.value)
                    if mode.value != 'NA':
                        template = template + 'PrintMode:{}\n'.format(mode.value)
                    if acyion.value != 'NA':
                        template = template + 'ManualAlignAcyion:{}\n'.format(acyion.value)
                template = template + 'NoDelete'
                log.info('template=' + template)
                create_file_path = os.path.join(local_path, '{}_{}_WR'.format(mask_name, level))
                if os.path.exists(create_file_path):
                    os.remove(create_file_path)
                f = open(create_file_path, 'x')
                f.write(template)
                f.close()
                flag = True
            else:
                flag = False
        else:
            log.info('job name not found')
            flag = False
    except Exception as e:
        traceback.print_exc()
        print(e)
        flag = False
    return flag


def alta_catalog(request):
    lot_id = request.POST.get('lot_id')
