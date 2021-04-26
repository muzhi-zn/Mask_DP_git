# coding:utf-8

from utilslibrary.proxy.log_db_proxy import ProxyFactory, InvocationHandler
from django.http.response import JsonResponse
from django.db import transaction
from utilslibrary.base.base import BaseService
from infotree.models import unreleased_info_alta, info_tree_template, maintain_table_mdt, released_info, unreleased_mdt
from utilslibrary.utils.date_utils import getDateStr, getMilliSecond


@ProxyFactory(InvocationHandler)
class unreleased_alta_service(BaseService):

    def add_unreleased_alta(self, tree_data):
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

                _unrelease_data = unreleased_info_alta.objects.all()
                if _unrelease_data.count() == 0:
                    group = 1
                else:
                    group = int(_unrelease_data.values('group').distinct().order_by('-group')[0]['group']) + 1

                temp_list = info_tree_template.objects.filter(is_delete=0, machine_type__contains=tool).values()

                data_list = list()
                for i in range(0, temp_list.count()):
                    _o = unreleased_info_alta()
                    _o.group = group
                    _o.tool = tool
                    _o.customer = customer
                    _o.node = node
                    _o.tone = tone
                    _o.blank = blank
                    _o.grade = grade
                    _o.pattern_density = pattern_density
                    _o.layer = layer
                    _o.level = temp_list[i]['level']
                    _o.type = temp_list[i]['type']
                    _o.item = temp_list[i]['cs_command']
                    _o.value = ''
                    _o.limit_type = _o.limit = temp_list[i]['limit_type']
                    _o.limit = temp_list[i]['limit']
                    _o.version = 1
                    _o.status = 1
                    _o.create_by = create_by
                    _o.create_date = getDateStr()
                    _o.create_time = getMilliSecond()
                    data_list.append(_o)

                unreleased_info_alta.objects.bulk_create(data_list)

                data["success"] = True
                data["msg"] = "Success"

        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    def add_copy_unreleased_alta(self, unreleased_alta_data):
        data = {}
        try:
            with transaction.atomic():

                s_list = unreleased_alta_data.id
                customer = unreleased_alta_data.customer
                tool = unreleased_alta_data.tool
                node = unreleased_alta_data.node
                tone = unreleased_alta_data.tone
                blank = unreleased_alta_data.blank
                grade = unreleased_alta_data.grade
                pattern_density = unreleased_alta_data.pattern_density
                layer = unreleased_alta_data.layer
                create_by = unreleased_alta_data.create_by

                group = int(
                    unreleased_info_alta.objects.all().values('group').distinct().order_by('-group')[0]['group']) + 1

                itd_list = unreleased_info_alta.objects.filter(customer=s_list[0], tool=s_list[1], node=s_list[2],
                                                               tone=s_list[3], blank=s_list[4], grade=s_list[5],
                                                               pattern_density=s_list[6], layer=s_list[7],
                                                               level=s_list[8], is_delete=0)

                data_list = list()
                for itd in itd_list:
                    print(itd.level, itd.type, itd.item, itd.value, itd.limit_type, itd.limit)

                    _o = unreleased_info_alta()
                    _o.group = group
                    _o.customer = customer
                    _o.tool = tool
                    _o.node = node
                    _o.tone = tone
                    _o.blank = blank
                    _o.grade = grade
                    _o.pattern_density = pattern_density
                    _o.layer = layer
                    _o.level = itd.level
                    _o.type = itd.type
                    _o.level = itd.level
                    _o.item = itd.item
                    _o.value = itd.value
                    _o.limit_type = _o.limit = itd.limit_type
                    _o.limit = itd.limit
                    _o.version = 1
                    _o.create_by = create_by
                    _o.create_date = getDateStr()
                    _o.create_time = getMilliSecond()
                    data_list.append(_o)

                unreleased_info_alta.objects.bulk_create(data_list)

                data["success"] = True
                data["msg"] = "Success"

        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    def upd_unreleased_alta(self, tree_data):
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

    def del_unreleased_alta(self, tree_data):
        data = {}
        data["success"] = False
        data["msg"] = "Failed"

        customer = tree_data.customer
        tool = tree_data.tool
        node = tree_data.node
        tone = tree_data.tone
        blank = tree_data.blank
        grade = tree_data.grade
        pattern_density = tree_data.pattern_density
        layer = tree_data.layer
        level = tree_data.level

        if not (customer and tool and node and tone and blank and grade and pattern_density and layer):
            data["success"] = False
            data["msg"] = "Failed"
            return JsonResponse(data, safe=False)

        with transaction.atomic():
            id = unreleased_info_alta.objects.filter(customer=customer, tool=tool, node=node, tone=tone, blank=blank,
                                                     grade=grade, pattern_density=pattern_density, layer=layer,
                                                     level=level,
                                                     is_delete=0, item='MDT').values('id')[0]['id']

            _o = unreleased_info_alta.objects.filter(tool=tool,
                                                     node=node,
                                                     customer=customer,
                                                     tone=tone,
                                                     blank=blank,
                                                     grade=grade,
                                                     pattern_density=pattern_density,
                                                     layer=layer,
                                                     level=level,
                                                     is_delete=0).update(is_delete=1)

            unreleased_mdt.objects.filter(type=2, unreleased_id=id, is_delete=0).update(is_delete=1)

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

                mdt_id = unreleased_info_alta.objects.filter(group=group, is_delete=0).values('id')[0]['id']

                unreleased_mdt.objects.filter(unreleased_id=mdt_id, is_delete=0).update(lock=1)
                unreleased_info_alta.objects.filter(group=group, is_delete=0).update(lock=1)
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
