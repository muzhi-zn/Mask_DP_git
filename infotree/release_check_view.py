# -*- coding: utf-8 -*-
# Create your views here.
import json
from django.db import connection
from django.shortcuts import render
from django.http.response import JsonResponse
from utilslibrary.base.base import BaseView
from django.db.models import Q
from infotree.models import release_check, info_tree_template, released_info, released_info_alta, unreleased_info_alta, \
    unreleased_info, unreleased_mdt, released_mdt
from infotree.service.release_check_service import release_check_service
from utilslibrary.utils.date_utils import getDateStr, getMilliSecond
from utilslibrary.utils.common_utils import getCurrentSessionName, getCurrentSessionID
from django.views.decorators.csrf import csrf_exempt


class release_check_list(BaseView):

    def get(self, request):
        if request.method == 'GET':
            user_name = getCurrentSessionName(request)
            return render(request, 'info_tree/release_check/infotree_release_check_list.html', {"user_name": user_name})

    def post(self, request):
        if request.method == 'POST':
            super().post(request)

            customer = request.POST.get('s_customer')
            tool = request.POST.get('s_tool')
            node = request.POST.get('s_node')
            tone = request.POST.get('s_tone')
            blank = request.POST.get('s_blank')
            grade = request.POST.get('s_grade')
            pattern_density = request.POST.get('s_pattern_density')
            layer = request.POST.get('s_layer')
            status = request.POST.get('s_status')

            q = Q()
            q.connector = 'and'
            q.children.append(('is_delete', 0))

            if tool:
                q.children.append(("customer", customer))
            if tool:
                q.children.append(("tool", tool))
            if node:
                q.children.append(("node", node))
            if tone:
                q.children.append(("tone", tone))
            if blank:
                q.children.append(("blank", blank))
            if grade:
                q.children.append(("grade", grade))
            if pattern_density:
                q.children.append(("pattern_density", pattern_density))
            if layer:
                q.children.append(("layer", layer))
            if status:
                q.children.append(('check_status', status))

            _o = release_check.objects.filter(q).order_by('-id').values()[self.startIndex: self.endIndex]

            data = {'total': release_check.objects.filter(q).count(), 'rows': list(_o)}

            return JsonResponse(data, safe=False)


class release_check_check_list(BaseView):
    def get(self, request):
        if request.method == 'GET':
            # , content_type = "application/json,charset=utf-8"
            id = request.GET.get('id')
            type = request.GET.get('type')
            _o = release_check.objects.get(id=id)

            tool = _o.tool

            if tool == 'MS03':
                field_val = 'item'
                title_val = 'Item'
                count = released_info_alta.objects.filter(tool=_o.tool, node=_o.node, tone=_o.tone, blank=_o.blank,
                                                          grade=_o.grade, pattern_density=_o.pattern_density,
                                                          layer=_o.layer,
                                                          group=_o.group).values('version').distinct().count()
            else:
                field_val = 'cs_command'
                title_val = 'CS_Command'
                count = released_info.objects.filter(tool=_o.tool, node=_o.node, tone=_o.tone, blank=_o.blank,
                                                     grade=_o.grade, pattern_density=_o.pattern_density, layer=_o.layer,
                                                     group=_o.group).values('version').distinct().count()

            # if count == 0:
            #     col = "{field: 'group', title: 'Group'};{field: '" + field_val + "', title: '" + title_val + "'};" + \
            #           "{field: 'current', title: 'Current'," + \
            #           "formatter: function operateFormatter(value, row, index) {" + \
            #           "if (rwo.current !== rwo.previous) {return '<a style='color:red'>rwo.current</a>'}}};" + \
            #           "{field: 'previous', title: 'Previous'," + \
            #           "formatter: function operateFormatter(value, row, index) {" + \
            #           "if (rwo.current !== rwo.previous) {return '<a style='color:red'>rwo.previous</a>'}}};"

            # else:
            #     i = 1
            #     col = "{field: 'group', title: 'Group'};{field: '" + field_val + "', title: '" + title_val + "'};" + \
            #           "{field: 'current', title: 'Current'}"
            #     while 1 <= count:
            #         col = col + ";{field: 'version_" + str(count) + "', title: 'Version_" + str(count) + "'}"
            #         count -= 1

            # print(col)
            return render(request, 'info_tree/release_check/infotree_release_check_check_list.html',
                          {"id": id, "field_val": field_val, "title_val": title_val, "type": type})
            # {"id": id, "column": col, "type": type})

    def post(self, request):
        if request.method == 'POST':
            super().post(request)

            id = request.POST.get('id')

            _o = release_check.objects.get(id=id)
            tool = _o.tool
            group = _o.group
            version = _o.version

            _k = info_tree_template.objects.filter(machine_type__contains=tool, is_delete=0).values('cs_command')
            for k in _k:
                print(k['cs_command'])

            if tool == 'MS03':
                re_table_name = 'infotree_released_info_alta'
                reun_table_name = 'infotree_unreleased_info_alta'
                col_name = '`item`'
                reun_a = released_info_alta.objects.filter(group=group,
                                                           is_delete=0).values('version').distinct().order_by('-id')
                count = reun_a.count()
                if count != 0:
                    last_ver = reun_a[0]['version']
            else:
                re_table_name = 'infotree_released_info'
                reun_table_name = 'infotree_unreleased_info'
                col_name = 'cs_command'
                if version == 0:
                    reun = released_info.objects.filter(group=group,
                                                        is_delete=0).values('version').distinct().order_by('-id')
                else:
                    reun = released_info.objects.filter(group=group,
                                                        # is_delete=0,
                                                        version=version).values('version').distinct().order_by('-id')
                print(reun.query)
                count = reun.count()
                if count != 0:
                    last_ver = reun[0]['version']
                else:
                    last_ver = 0

            print('count', count)

            data = ''
            ssq = ''
            cursor = connection.cursor()

            if count == 0:
                # mask_dp_dev.
                sql = "SELECT `group`, " + col_name + ", `value` as `current` " + \
                      "FROM " + reun_table_name + " where `group` = " + str(_o.group)
            else:
                if version == 0:
                    sql = "SELECT cur.`group`, cur." + col_name + \
                          ", cur.`value` as `current`, pre.`value` as `previous`" + \
                          " FROM (SELECT distinct `group`, `value`, " + col_name + \
                          " from " + reun_table_name + " where `group` = " + str(_o.group) + ") as cur" + \
                          " LEFT JOIN (SELECT * from " + re_table_name + \
                          " where `group` = " + str(_o.group) + " and version = " + str(last_ver) + ")" + \
                          " as pre ON cur." + col_name + " = pre." + col_name
                elif version - 1 == 0:
                    sql = "SELECT `group`, " + col_name + ", `value` as `current` " + \
                          " FROM " + re_table_name + " where `group` = " + str(_o.group) + \
                          " and version = " + str(version)
                else:
                    sql = "SELECT cur.`group`, cur." + col_name + \
                          ", cur.`value` as `current`, pre.`value` as `previous`" + \
                          " FROM (SELECT distinct `group`, `value`, " + col_name + \
                          " from " + re_table_name + " where `group` = " + str(_o.group) + \
                          " and version = " + str(version) + ") as cur" + \
                          " LEFT JOIN (SELECT * from " + re_table_name + \
                          " where `group` = " + str(_o.group) + " and version = " + str(version - 1) + ")" + \
                          " as pre ON cur." + col_name + " = pre." + col_name

                # while 1 <= count:
                #     data = data + ", v" + str(count) + ".`value` as version_" + str(count)
                #     ssq = ssq + " LEFT JOIN (SELECT * from " + table_name + " where `group` = " + str(_o.group) + \
                #           " and version = " + str(count) + ") as v" + str(count) + " ON col.cs_command = v" + str(
                #         count) + "." + col_name
                #     count -= 1
                # print(data)
                #
                # sql = "SELECT col.`group`, col." + col_name + " " + data + \
                #       " FROM (SELECT distinct `group`, " + col_name + " from " + table_name + " where `group` = " + \
                #       str(_o.group) + ") as col" + ssq
                # print(sql)

            print(sql)
            cursor.execute(sql)

            p_list = dictfetchall(cursor)
            # print(p_list)
            # print(len(p_list))

            data = {'total': len(p_list), 'rows': list(p_list)}
            # data = {'total': release_check.objects.filter(q).count(), 'rows': list(_o)}

            return JsonResponse(data, safe=False)


@csrf_exempt
def release_check_check(request):
    id = request.POST.get('id')
    check_status = request.POST.get('check_status')

    _o = release_check.objects.get(id=id)
    _o.check_user_id = getCurrentSessionID(request)
    _o.check_user_name = getCurrentSessionName(request)
    _o.check_status = int(check_status)
    _o.check_time = getDateStr()

    _s = release_check_service()

    if _o.tool == 'MS03':
        return _s.upd_release_check_alta(_o)
    else:
        return _s.upd_release_check(_o)


def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


class MdtDetail(BaseView):
    def get(self, request):
        id = request.GET.get('id')
        return render(request, 'info_tree/release_check/infotree_release_check_mdt_detail.html', {'id': id})

    def post(self, request):
        super().post(request)
        id = request.POST.get('id')
        _o = release_check.objects.get(id=id)
        tool = _o.tool
        node = _o.node
        tone = _o.tone
        blank = _o.blank
        grade = _o.grade
        pattern_density = _o.pattern_density
        layer = _o.layer
        group = _o.group
        check_status = _o.check_status
        if tool != 'MS03' and check_status == 0:
            unreleased_id = unreleased_info.objects.filter(tool=tool, node=node, tone=tone, blank=blank, grade=grade,
                                                           pattern_density=pattern_density,
                                                           layer=layer, group=group, type='MDT').order_by('-id')[0].id
            mdt_set = unreleased_mdt.objects.filter(unreleased_id=unreleased_id, is_delete=0)
            query_list = list(mdt_set.values())[self.startIndex: self.endIndex]
            return JsonResponse({'total': len(mdt_set), 'rows': query_list})
        elif tool != 'MS03' and check_status == 1:
            release_id = released_info.objects.filter(tool=tool, node=node, tone=tone, blank=blank, grade=grade,
                                                      pattern_density=pattern_density,
                                                      layer=layer, group=group, type='MDT').order_by('-id')[0].id
            mdt_set = released_mdt.objects.filter(released_id=release_id, is_delete=0)
            query_list = list(mdt_set.values())[self.startIndex: self.endIndex]
            return JsonResponse({'total': len(mdt_set), 'rows': query_list})
        else:
            return JsonResponse({'total': 0, 'rows': []})
