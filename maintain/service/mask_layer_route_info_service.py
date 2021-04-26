import logging
import traceback

import pandas as pd
import xlrd
from django.db import transaction
from django.db.models import Q
from django.http.response import JsonResponse
from maintain.models import mask_layer_route_info, maintain_change_log
from utilslibrary.base.base import BaseService
from utilslibrary.proxy.log_db_proxy import ProxyFactory, InvocationHandler
from system.models import dict
from utilslibrary.utils.common_utils import getCurrentSessionName

log = logging.getLogger('log')


@ProxyFactory(InvocationHandler)
class SettingsService(BaseService):

    def add_settings(self, settings, new_data, request):
        data = {}
        try:
            settings.save()
            c_l = maintain_change_log()
            c_l.data_id = settings.id
            c_l.table = 'mask_layer'
            c_l.change_user = getCurrentSessionName(request)
            c_l.operation = 'Add'
            c_l.new_data = new_data
            c_l.old_data = ' '
            c_l.save()
            data['success'] = True
            data['msg'] = 'Success'
        except Exception as e:
            log.error(e)
            data['success'] = False
            data['msg'] = str(e)
        return JsonResponse(data=data, safe=False)

    def edit_settings(self, settings, new_data, old_data, request):

        data = {}
        try:
            settings.save()
            c_l = maintain_change_log()
            c_l.data_id = settings.id
            c_l.table = 'mask_layer'
            c_l.change_user = getCurrentSessionName(request)
            c_l.operation = 'Add'
            c_l.new_data = new_data
            c_l.old_data = old_data
            c_l.save()
            data['success'] = True
            data['msg'] = 'Success'
        except Exception as e:
            log.error(e)
            data['success'] = False
            data['msg'] = str(e)
        return JsonResponse(data=data, safe=False)

    def del_settings(self, settings):
        data = {}
        old_data = {}
        try:
            ids = settings.id
            id_list = ids.split(',')
            with transaction.atomic():
                for id in id_list:
                    settings = mask_layer_route_info.objects.get(id=id)
                    old_data['metal_scheme'] = settings.metal_scheme
                    old_data['mask_name'] = settings.mask_name
                    old_data['must'] = settings.must
                    old_data['mask_id'] = settings.mask_id
                    old_data['process'] = settings.process
                    old_data['digitized_area'] = settings.digitized_area
                    old_data['mask_tone'] = settings.mask_tone
                    old_data['node'] = settings.node
                    old_data['opc_tag'] = settings.opc_tag
                    old_data['product_type'] = settings.product_type
                    old_data['mask_type'] = settings.mask_type
                    old_data['group'] = settings.group
                    settings.is_delete = 1
                    settings.save()
            data['success'] = True
            data['msg'] = 'Delete Success'
            return JsonResponse(data, safe=False)
        except Exception as e:
            data['success'] = False
            data['msg'] = 'Delete Failed'
            print(e)
            return JsonResponse(data, safe=True)


@ProxyFactory(InvocationHandler)
class SettingsUploadService(BaseService):

    def __init__(self, file_path, version, data):
        self.file_path = file_path
        self.version = version
        self.data = eval(data)

    def check_file_format(self):
        try:
            df = pd.read_excel(self.file_path, sheet_name='mask_layer')
            # Check excel fist row name
            if df.iloc[0, 0] == 'Metal_Schema' and \
                    df.iloc[0, 1] == 'Must' and \
                    df.iloc[0, 2] == 'Process' and \
                    df.iloc[0, 3] == 'Mask_name' and \
                    df.iloc[0, 4] == 'Mask_ID' and \
                    df.iloc[0, 5] == 'Digitized_Area' and \
                    df.iloc[0, 6] == 'Mask_tone' and \
                    df.iloc[0, 7] == 'Node' and \
                    df.iloc[0, 8] == 'OPC_TAG' and \
                    df.iloc[0, 9] == 'Product_type' and \
                    df.iloc[0, 10] == 'Group' and \
                    df.iloc[0, 11] == 'Mask_type':

                # Get dict value (cad_layer_setting)
                parent_id = dict.objects.filter(description='mask_layer_setting').values()
                result_dict = {}
                for child_id in parent_id:
                    labels = dict.objects.filter(parent_id=child_id['id']).order_by('sort').values('value')
                    label_list = []
                    for label in labels:
                        label_list.append(label['value'])
                    result_dict[child_id['type']] = label_list

                workbook = xlrd.open_workbook(self.file_path)
                sheet = workbook.sheet_by_name('mask_layer')
                row_num = sheet.nrows
                for i in range(2, row_num):
                    row = sheet.row_values(i)
                    row_metal_scheme = str(row[0]).strip()
                    row_must = str(row[1]).strip()
                    row_process = str(row[2]).strip()
                    row_digitized_area = str(row[5]).strip()
                    row_mask_tone = str(row[6]).strip()
                    row_node = str(row[7]).strip()
                    row_opc_tag = str(row[8]).strip()
                    row_product_type = str(row[9]).strip()
                    row_group = str(row[10]).strip()
                    row_mask_type = str(row[11]).strip()

                    if (row_metal_scheme in result_dict['Metal_Scheme']) and (row_process != 'BEOL'):
                        print(i, 1, row_metal_scheme)
                        return False

                    if not (row_must in result_dict['Must_mask_layer_setting']):
                        print(i, 2, row_must)
                        return False

                    if not (row_process in result_dict['Process_mask_layer_setting']):
                        print(i, 3, row_process)
                        return False

                    if not (row_digitized_area in result_dict['Digitized_Area']):
                        print(i, 4, row_digitized_area)
                        return False

                    if not (row_mask_tone in result_dict['Mask_tone']):
                        print(i, 5, row_mask_tone)
                        return False

                    if not (row_node in result_dict['Node']):
                        print(i, 6, row_node)
                        return False

                    if not (row_opc_tag in result_dict['OPC_TAG']):
                        print(i, 7, row_opc_tag)
                        return False

                    if not (row_product_type in result_dict['Product_type']):
                        print(i, 8, row_product_type)
                        return False

                    if not (row_group in result_dict['Group']):
                        print(i, 9, row_group)
                        return False
                    if not (row_mask_type in result_dict['Mask_type']):
                        print(i, 10, row_mask_type)
                        return False
                # Batch insert data
                ins_res = self.add_mask_layer_setting()
                if not ins_res[0]:
                    return False, ins_res[1]

                return True, 'Update cad layer setting success'
            else:
                return False, 'Excel first row name error.'
        except Exception as e:
            traceback.print_exc()
            return False, str(e)

    @transaction.atomic()
    def add_mask_layer_setting(self):
        try:
            workbook = xlrd.open_workbook(self.file_path)
            sheet = workbook.sheet_by_name('mask_layer')
            row_num = sheet.nrows
            mask_layer_setting_list = list()
            for i in range(2, row_num):
                row = sheet.row_values(i)
                _o = mask_layer_route_info()
                _o.metal_scheme = row[0]
                _o.must = row[1]
                _o.process = row[2]
                _o.mask_name = row[3]
                _o.mask_id = str(row[4]).split('.')[0]
                _o.digitized_area = row[5]
                _o.mask_tone = row[6]
                _o.node = row[7]
                _o.opc_tag = row[8]
                _o.product_type = row[9]
                _o.group = row[10]
                _o.mask_type = row[11]
                _o.version = int(self.version) + 1
                _o.release = 1
                mask_layer_setting_list.append(_o)

            q = Q()
            q.connector = 'and'
            q.children.append(('is_delete', 0))
            q.children.append(('release', 1))

            if self.data['node']:
                q.children.append(('node__contains', self.data['node']))

            if self.data['opc_tag']:
                q.children.append(('opc_tag', self.data['opc_tag']))

            if self.data['product_type']:
                q.children.append(('product_type', self.data['product_type']))

            if self.data['process'] == 'FEOL' or self.data['process'] == 'MEOL':
                q.children.append(('process', self.data['process']))
            elif self.data['process'] == 'FEOL&MEOL':
                q.children.append(('process__in', ['MEOL', 'FEOL']))

            if self.data['metal_scheme']:
                q.children.append(('metal_scheme__contains', self.data['metal_scheme']))

            # mask_layer_route_info.objects.all().update(release=0)
            _o = mask_layer_route_info.objects.filter(q).update(release=0)
            mask_layer_route_info.objects.bulk_create(mask_layer_setting_list)

            return True, 'success'
        except Exception as e:
            traceback.print_exc()
            return False, str(e)
