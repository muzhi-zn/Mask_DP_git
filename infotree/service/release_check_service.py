# coding:utf-8
import traceback

from utilslibrary.proxy.log_db_proxy import ProxyFactory, InvocationHandler
from django.http.response import JsonResponse
from django.db import transaction
from utilslibrary.base.base import BaseService
from infotree.models import unreleased_info, unreleased_info_alta, release_check, released_info, released_info_alta, \
    unreleased_mdt, released_mdt
from utilslibrary.utils.date_utils import getDateStr, getMilliSecond
from utilslibrary.utils.common_utils import getCurrentSessionID, getCurrentSessionName


@ProxyFactory(InvocationHandler)
class release_check_service(BaseService):

    def upd_release_check(self, release_check_data):
        data = {}
        try:
            with transaction.atomic():
                check_status_val = release_check_data.check_status
                group_val = release_check_data.group
                # 判斷是否為 Reject
                if check_status_val == '2' or check_status_val == 2:
                    # unreleased
                    unre_mdt_id = unreleased_info.objects.filter(group=group_val, cs_command='MDT', lock=1,
                                                                 is_delete=0).values('id').order_by('-id')[0]['id']
                    unreleased_info.objects.filter(group=group_val, lock=1, is_delete=0).update(lock=0)
                    unreleased_mdt.objects.filter(unreleased_id=unre_mdt_id, lock=1, is_delete=0).update(lock=0)
                    # released
                    query_set = released_info.objects.filter(group=group_val, cs_command='MDT', lock=1,
                                                             is_delete=0).values('id').order_by('-id')
                    if query_set:
                        re_mdt_id = query_set[0]['id']
                        released_info.objects.filter(group=group_val, lock=1, is_delete=0).update(lock=0)
                        released_mdt.objects.filter(released_id=re_mdt_id, lock=1, is_delete=0).update(lock=0)

                    release_check_data.save()

                    data["success"] = True
                    data["msg"] = "Success"
                    return JsonResponse(data, safe=False)

                group = release_check_data.group

                unreleased_info_list = unreleased_info.objects.filter(group=group, lock=1, is_delete=0)
                released_info_old_list = released_info.objects.filter(group=group).order_by('-id')

                if released_info_old_list.count() == 0:
                    released_info_version = 1
                else:
                    released_info_version = int(released_info_old_list[0].version) + 1

                data_list = []
                for i in range(0, unreleased_info_list.count()):
                    _o = released_info()
                    _o.group = group
                    _o.customer = unreleased_info_list[i].customer
                    _o.tool = unreleased_info_list[i].tool
                    _o.node = unreleased_info_list[i].node
                    _o.tone = unreleased_info_list[i].tone
                    _o.blank = unreleased_info_list[i].blank
                    _o.grade = unreleased_info_list[i].grade
                    _o.pattern_density = unreleased_info_list[i].pattern_density
                    _o.layer = unreleased_info_list[i].layer
                    _o.type = unreleased_info_list[i].type
                    _o.cs_command = unreleased_info_list[i].cs_command
                    _o.value = unreleased_info_list[i].value
                    _o.version = released_info_version
                    _o.cd_map_id = unreleased_info_list[i].cd_map_id
                    _o.cec_id = unreleased_info_list[i].cec_id
                    data_list.append(_o)

                released_info_old_list.update(lock=0, is_delete=1)
                released_info.objects.bulk_create(data_list)

                new_released_info_id = released_info.objects.filter(cs_command='MDT', is_delete=0).values(
                    'id').order_by('-id')[0]['id']

                print("new_released_info_id", new_released_info_id)
                # mdt
                unreleased_info_id = unreleased_info.objects.filter(group=group, lock=1, is_delete=0,
                                                                    cs_command='MDT').values('id')[0]['id']

                unreleased_mdt_list = unreleased_mdt.objects.filter(unreleased_id=unreleased_info_id,
                                                                    lock=1, is_delete=0)
                release_mdt_old_list = released_mdt.objects.filter(
                    released_id=unreleased_info_id).order_by('-id')

                if release_mdt_old_list.count() == 0:
                    mdt_version = 1
                else:
                    mdt_version = int(release_mdt_old_list[0].version) + 1

                print(unreleased_mdt_list.count())
                mdt_data_list = []
                for i in range(0, unreleased_mdt_list.count()):
                    _o = released_mdt()
                    _o.type = int(unreleased_mdt_list[i].type)
                    _o.released_id = int(new_released_info_id)
                    _o.cad_layer = unreleased_mdt_list[i].cad_layer
                    _o.data_type = unreleased_mdt_list[i].data_type
                    _o.writer_mdt = unreleased_mdt_list[i].writer_mdt
                    _o.writer_dose = unreleased_mdt_list[i].writer_dose
                    _o.version = mdt_version

                    mdt_data_list.append(_o)

                unreleased_info_list.update(lock=0)
                unreleased_mdt_list.update(lock=0)
                released_mdt.objects.bulk_create(mdt_data_list)
                release_check_data.version = mdt_version

                re_check_data = release_check.objects.get(id=release_check_data.id)
                re_check_data.check_user_id = release_check_data.check_user_id
                re_check_data.check_user_name = release_check_data.check_user_name
                re_check_data.check_status = release_check_data.check_status
                re_check_data.check_time = release_check_data.check_time
                re_check_data.version = released_info_version
                re_check_data.save()

                data["success"] = True
                data["msg"] = "Success"
        except Exception as e:
            traceback.print_exc()
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    def upd_release_check_alta(self, release_check_data):
        data = {}
        try:
            with transaction.atomic():
                check_status_val = release_check_data.check_status
                group_val = release_check_data.group
                # 判斷是否為 Reject
                if check_status_val == '2' or check_status_val == 2:
                    unre_mdt_id = unreleased_info_alta.objects.filter(group=group_val, item='MDT', lock=1,
                                                                      is_delete=0).values('id').order_by('-id')[0]['id']
                    unreleased_info_alta.objects.filter(group=group_val, lock=1, is_delete=0).update(lock=0)
                    unreleased_mdt.objects.filter(unreleased_id=unre_mdt_id, lock=1, is_delete=0).update(lock=0)

                    # released
                    re_mdt_id = unreleased_info_alta.objects.filter(group=group_val, item='MDT', lock=1,
                                                                    is_delete=0).values('id').order_by('-id')[0]['id']
                    released_info_alta.objects.filter(group=group_val, lock=1, is_delete=0).update(lock=0)
                    released_mdt.objects.filter(unreleased_id=re_mdt_id, lock=1, is_delete=0).update(lock=0)

                    release_check_data.save()

                    data["success"] = True
                    data["msg"] = "Success"
                    return JsonResponse(data, safe=False)

                group = release_check_data.group
                unreleased_info_alta_list = unreleased_info_alta.objects.filter(group=group, lock=1, is_delete=0)
                released_info_alta_old_list = released_info_alta.objects.filter(group=group).order_by('-id')
                if released_info_alta_old_list.count() == 0:
                    released_info_alta_version = 1
                else:
                    released_info_alta_version = int(released_info_alta_old_list[0].version) + 1

                data_list = []
                for i in range(0, unreleased_info_alta_list.count()):
                    _o = released_info_alta()
                    _o.group = group
                    _o.customer = unreleased_info_alta_list[i].customer
                    _o.tool = unreleased_info_alta_list[i].tool
                    _o.node = unreleased_info_alta_list[i].node
                    _o.tone = unreleased_info_alta_list[i].tone
                    _o.blank = unreleased_info_alta_list[i].blank
                    _o.grade = unreleased_info_alta_list[i].grade
                    _o.pattern_density = unreleased_info_alta_list[i].pattern_density
                    _o.layer = unreleased_info_alta_list[i].layer
                    _o.level = unreleased_info_alta_list[i].level
                    _o.type = unreleased_info_alta_list[i].type
                    _o.item = unreleased_info_alta_list[i].item
                    _o.value = unreleased_info_alta_list[i].value
                    _o.version = released_info_alta_version
                    data_list.append(_o)

                released_info_alta_old_list.update(lock=0, is_delete=1)
                released_info_alta.objects.bulk_create(data_list)

                re_check_data = release_check.objects.get(id=release_check_data.id)
                re_check_data.check_user_id = release_check_data.check_user_id
                re_check_data.check_user_name = release_check_data.check_user_name
                re_check_data.check_status = release_check_data.check_status
                re_check_data.check_time = release_check_data.check_time
                re_check_data.version = released_info_alta_version
                re_check_data.save()

                data["success"] = True
                data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)
