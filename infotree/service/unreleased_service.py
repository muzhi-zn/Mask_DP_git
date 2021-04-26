# coding:utf-8
import traceback

from utilslibrary.proxy.log_db_proxy import ProxyFactory, InvocationHandler
from django.http.response import JsonResponse
from django.db import transaction
from utilslibrary.base.base import BaseService
from infotree.models import unreleased_info, info_tree_template, maintain_table, maintain_table_mdt, released_info, \
    unreleased_mdt
from utilslibrary.utils.date_utils import getDateStr, getMilliSecond


@ProxyFactory(InvocationHandler)
class unreleased_service(BaseService):

    def add_info_tree_data(self, tree_data):
        data = {}
        try:
            with transaction.atomic():
                customer = tree_data.customer
                tool = tree_data.tool
                node = tree_data.node
                tone = tree_data.tone
                blank = tree_data.blank
                grade = tree_data.grade
                pattern_density = tree_data.pattern_density
                layer = tree_data.layer
                create_by = tree_data.create_by

                _unrelease_data = unreleased_info.objects.all()
                if _unrelease_data.count() == 0:
                    group = 0
                else:
                    group = int(_unrelease_data.values('group').distinct().order_by('-group')[0]['group']) + 1

                temp_list = info_tree_template.objects.filter(is_delete=0, machine_type__contains=tool).values()

                data_list = list()
                for i in range(0, temp_list.count()):
                    _o = unreleased_info()
                    _o.group = group
                    _o.customer = customer
                    _o.tool = tool
                    _o.node = node
                    _o.tone = tone
                    _o.blank = blank
                    _o.grade = grade
                    _o.pattern_density = pattern_density
                    _o.layer = layer
                    _o.type = temp_list[i]['type']
                    _o.cs_command = temp_list[i]['cs_command']
                    _o.value = ''
                    _o.limit_type = _o.limit = temp_list[i]['limit_type']
                    _o.limit = temp_list[i]['limit']
                    _o.version = 1
                    _o.status = 1
                    _o.create_by = create_by
                    _o.create_date = getDateStr()
                    _o.create_time = getMilliSecond()
                    data_list.append(_o)

                unreleased_info.objects.bulk_create(data_list)

                _m = maintain_table()
                _m.customer = customer
                _m.tool = tool
                _m.node = node
                _m.tone = tone
                _m.blank = blank
                _m.grade = grade
                _m.pattern_density = pattern_density
                _m.layer = layer
                _m.create_by = create_by
                _m.create_date = getDateStr()
                _m.create_time = getMilliSecond()
                _m.save()

                data["success"] = True
                data["msg"] = "Success"

        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    def add_copy_info_tree_data(self, tree_data, mdt_list):
        data = {}
        try:
            with transaction.atomic():

                s_list = tree_data.id
                customer = tree_data.customer
                tool = tree_data.tool
                node = tree_data.node
                tone = tree_data.tone
                blank = tree_data.blank
                grade = tree_data.grade
                pattern_density = tree_data.pattern_density
                layer = tree_data.layer
                create_by = tree_data.create_by

                group = int(unreleased_info.objects.all().values('group').distinct().order_by('-group')[0]['group']) + 1

                itd_list = unreleased_info.objects.filter(customer=s_list[0], tool=s_list[1], node=s_list[2],
                                                          tone=s_list[3],
                                                          blank=s_list[4],
                                                          grade=s_list[5], pattern_density=s_list[6], layer=s_list[7],
                                                          is_delete=0)

                data_list = list()
                for itd in itd_list:
                    print(itd.type, itd.cs_command, itd.value, itd.limit_type, itd.limit)

                    _o = unreleased_info()
                    _o.group = group
                    _o.cd_map_id = itd.cd_map_id
                    _o.cec_id = itd.cec_id
                    _o.customer = customer
                    _o.tool = tool
                    _o.node = node
                    _o.tone = tone
                    _o.blank = blank
                    _o.grade = grade
                    _o.pattern_density = pattern_density
                    _o.layer = layer
                    _o.type = itd.type
                    _o.cs_command = itd.cs_command
                    _o.value = itd.value
                    _o.limit_type = _o.limit = itd.limit_type
                    _o.limit = itd.limit
                    _o.version = 1
                    _o.create_by = create_by
                    _o.create_date = getDateStr()
                    _o.create_time = getMilliSecond()
                    if itd.type == 'MDT':
                        _o.save()
                        mdt_data_list = []
                        for mdt in list(mdt_list):
                            _mdt = unreleased_mdt()
                            _mdt.unreleased_id = _o.id
                            _mdt.type = mdt['type']
                            _mdt.cad_layer = mdt['cad_layer']
                            _mdt.data_type = mdt['data_type']
                            _mdt.writer_dose = mdt['writer_dose']
                            _mdt.writer_mdt = mdt['writer_mdt']
                            mdt_data_list.append(_mdt)
                    else:
                        data_list.append(_o)
                unreleased_mdt.objects.bulk_create(mdt_data_list)
                unreleased_info.objects.bulk_create(data_list)

                data["success"] = True
                data["msg"] = "Success"

        except Exception as e:
            traceback.print_exc()
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    def upd_info_tree_data(self, tree_data):
        data = {}
        try:
            tree_data.save()
            data["success"] = True
            data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    def del_info_tree_data(self, tree_data):
        data = {}
        data["success"] = False
        data["msg"] = "Failed"

        tool = tree_data.tool
        node = tree_data.node
        tone = tree_data.tone
        blank = tree_data.blank
        grade = tree_data.grade
        pattern_density = tree_data.pattern_density
        layer = tree_data.layer

        if not (tool and node and tone and blank and grade and pattern_density and layer):
            data["success"] = False
            data["msg"] = "Failed"
            return JsonResponse(data, safe=False)

        with transaction.atomic():
            id = unreleased_info.objects.filter(tool=tool,
                                                node=node,
                                                tone=tone,
                                                blank=blank,
                                                grade=grade,
                                                pattern_density=pattern_density,
                                                layer=layer,
                                                is_delete=0,
                                                cs_command='MDT').values('id')[0]['id']

            _o = unreleased_info.objects.filter(tool=tool,
                                                node=node,
                                                tone=tone,
                                                blank=blank,
                                                grade=grade,
                                                pattern_density=pattern_density,
                                                layer=layer,
                                                is_delete=0).update(is_delete=1)

            unreleased_mdt.objects.filter(type=1, unreleased_id=id, is_delete=0).update(is_delete=1)

        data["success"] = True
        data["msg"] = "Success"
        return JsonResponse(data, safe=False)

    def add_export_log(self, log):
        try:
            log.save()
        except Exception as e:
            print(e)

    def add_release_check(self, release_data):
        data = {}
        try:
            with transaction.atomic():
                group = release_data.group

                mdt_id = unreleased_info.objects.filter(group=group, is_delete=0, cs_command='MDT').values('id')[0][
                    'id']
                unreleased_mdt.objects.filter(unreleased_id=mdt_id, is_delete=0).update(lock=1)
                unreleased_info.objects.filter(group=group, is_delete=0).update(lock=1)
                released_info.objects.filter(group=group, is_delete=0).update(lock=1)
                release_data.save()
                data["success"] = True
                data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    def add_mdt(self, mdt_data):
        data = {}
        try:
            mdt_data.save()
            data["success"] = True
            data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    def upd_mdt(self, mdt_data):
        data = {}
        try:
            mdt_data.save()
            data["success"] = True
            data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    def del_mdt(self, mdt_data):
        data = {}
        try:
            ids = mdt_data.id
            id_list = ids.split(',')
            with transaction.atomic():
                for id in id_list:
                    _o = unreleased_mdt.objects.get(id=id)
                    _o.is_delete = 1
                    _o.save()
            data['success'] = True
            data['msg'] = 'Delete Success'
            return JsonResponse(data, safe=False)
        except Exception as e:
            data['success'] = False
            data['msg'] = e
            print(e)
            return JsonResponse(data, safe=True)
