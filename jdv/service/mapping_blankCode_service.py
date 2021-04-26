from django.db import transaction
from django.http.response import HttpResponseRedirect, JsonResponse

from jdv.models import mes_blank_code
from maintain.models import maintain_change_log
from utilslibrary.base.base import BaseService
from utilslibrary.utils.common_utils import getCurrentSessionName


class MappingBlankCodeService(BaseService):

    def add_mapping_blank_code(self, mes_blank_code, c_l):
        data = {}
        try:
            mes_blank_code.save()
            c_l.data_id = mes_blank_code.id
            c_l.save()
            data['success'] = True
            data['msg'] = 'Success'
        except Exception as e:
            print(e)
            data['success'] = False
            data['msg'] = 'Failed'

        return JsonResponse(data, safe=False)


    def del_mapping_blank_code(self, bc, request):
        data = {}
        try:
            ids = bc.id
            id_list = ids.split(',')
            with transaction.atomic():
                for id in id_list:
                    bc = mes_blank_code.objects.get(id=id)
                    old_data = {}
                    old_data['seq'] = bc.seq
                    old_data['customer'] = bc.customer
                    old_data['design_rule'] = bc.design_rule
                    old_data['layer_name'] = bc.layer_name
                    old_data['grade_from'] = bc.grade_from
                    old_data['grade_to'] = bc.grade_to
                    old_data['mask_type'] = bc.mask_type
                    old_data['tone'] = bc.tone
                    old_data['wave_lenght'] = bc.wave_lenght
                    old_data['blank_code'] = bc.blank_code
                    old_data['part_no'] = bc.part_no
                    old_data['blank'] = bc.blank
                    c_l = maintain_change_log()
                    c_l.operation = 'Delete'
                    c_l.change_user = getCurrentSessionName(request)
                    c_l.table = 'Blank Code'
                    c_l.data_id = id
                    c_l.old_data = old_data
                    c_l.save()
                    bc.is_delete = 1
                    bc.save()
            data['success'] = True
            data['msg'] = 'Delete Success'
            return JsonResponse(data, safe=False)
        except Exception as e:
            data['success'] = False
            data['msg'] = e
            print(e)
            return JsonResponse(data, safe=True)