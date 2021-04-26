# -*- coding: utf-8 -*-
# Create your views here.
import json
from django.db import connection
from django.forms import model_to_dict
from django.shortcuts import render
from django.http.response import JsonResponse
from utilslibrary.base.base import BaseView
from django.db.models import Q
from infotree.models import release_check, info_tree_template, released_info, released_info_alta, released_mdt
from infotree.service.release_check_service import release_check_service
from utilslibrary.utils.date_utils import getDateStr, getMilliSecond
from utilslibrary.utils.common_utils import getCurrentSessionName, getCurrentSessionID
from django.views.decorators.csrf import csrf_exempt


class release_version_list(BaseView):

    def get(self, request):
        if request.method == 'GET':
            tool = request.GET.get('tool', '')
            node = request.GET.get('node', '')
            tone = request.GET.get('tone', '')
            blank = request.GET.get('blank', '')
            grade = request.GET.get('grade', '')
            pattern_density = request.GET.get('pattern_density', '')
            layer = request.GET.get('layer', '')

            if tool and node and tone and blank and grade and pattern_density and layer:
                if tool == 'MS03':
                    _o = released_info_alta.objects.filter(tool=tool, node=node, tone=tone, blank=blank,
                                                           grade=grade, pattern_density=pattern_density,
                                                           layer=layer, is_delete=0).values('group',
                                                                                            'version').distinct()
                    group = _o[0]['group']
                    ver_count = _o[0]['version']
                else:
                    _o = released_info.objects.filter(tool=tool, node=node, tone=tone, blank=blank,
                                                      grade=grade, pattern_density=pattern_density,
                                                      layer=layer, is_delete=0).values('group',
                                                                                       'version').distinct()
                    group = _o[0]['group']
                    ver_count = _o[0]['version']
            else:
                group = 0
                ver_count = 0
            return render(request,
                          'info_tree/release_version/infotree_release_version_list.html',
                          {"ver_count": ver_count, "group": group, "tool": tool, "node": node, "tone": tone,
                           "blank": blank, "grade": grade, "pattern_density": pattern_density, "layer": layer})

    def post(self, request):
        if request.method == 'POST':
            super().post(request)

            tool = request.POST.get('s_tool')
            node = request.POST.get('s_node')
            tone = request.POST.get('s_tone')
            blank = request.POST.get('s_blank')
            grade = request.POST.get('s_grade')
            pattern_density = request.POST.get('s_pattern_density')
            layer = request.POST.get('s_layer')
            group = request.POST.get('s_group')
            ver_count = request.POST.get('s_ver_count')

            if tool and node and tone and blank and grade and pattern_density and layer:

                if not (group and ver_count):
                    _o = release_check.objects.filter(tool=tool, node=node, tone=tone, blank=blank, grade=grade,
                                                      pattern_density=pattern_density, layer=layer).values(
                        'group').distinct().order_by('-group')
                    print(_o.query)

                    if len(_o) == 0:
                        data = {'total': 0, 'rows': []}
                        return JsonResponse(data, safe=False)

                    group = _o.group

                if tool == 'MS03':
                    re_table_name = 'infotree_released_info_alta'
                    col_name = '`item`'
                else:
                    re_table_name = 'infotree_released_info'
                    col_name = 'cs_command'

                cursor = connection.cursor()

                x = ''
                y = ''
                if int(ver_count) == 1:
                    sql = "SELECT last.`group`, last." + col_name + \
                          ", last.`value` as `ver_" + str(ver_count) + "`" + \
                          " " + x + \
                          " FROM (SELECT distinct `group`, `value`, " + col_name + \
                          " from " + re_table_name + " where `group` = " + str(group) + \
                          " and version = " + str(ver_count) + ") as last"
                else:
                    v = int(ver_count) - 1
                    while v > 0:
                        x = x + ", ver_" + str(v) + ".`value` as `ver_" + str(v) + "`"
                        y = y + " LEFT JOIN (SELECT * from " + re_table_name + \
                            " where `group` = " + str(group) + " and version = " + str(v) + ")" + \
                            " as ver_" + str(v) + " ON last." + col_name + " = ver_" + str(v) + "." + col_name
                        v -= 1

                    sql = "SELECT last.`group`, last." + col_name + \
                          ", last.`value` as `ver_" + str(ver_count) + "`" + \
                          " " + x + \
                          " FROM (SELECT distinct `group`, `value`, " + col_name + \
                          " from " + re_table_name + " where `group` = " + str(group) + \
                          " and version = " + str(ver_count) + ") as last" + \
                          " " + y

                # ", pre.`value` as `previous`" + \
                # " LEFT JOIN (SELECT * from " + re_table_name + \
                # " where `group` = " + str(_o.group) + " and version = " + str(version - 1) + ")" + \
                # " as pre ON cur." + col_name + " = pre." + col_name

                print(sql)
                cursor.execute(sql)
                p_list = dictfetchall(cursor)
                data = {'total': len(p_list), 'rows': list(p_list)}

                return JsonResponse(data, safe=False)
            else:
                data = {'total': 0, 'rows': []}
                return JsonResponse(data, safe=False)


def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


class MDTVersion(BaseView):
    def get(self, request):
        tool = request.GET.get('tool', '')
        node = request.GET.get('node', '')
        tone = request.GET.get('tone', '')
        blank = request.GET.get('blank', '')
        grade = request.GET.get('grade', '')
        pattern_density = request.GET.get('pattern_density', '')
        layer = request.GET.get('layer', '')
        return render(request, 'info_tree/release_version/mdt_version_view.html',
                      {'tool': tool, 'node': node, 'tone': tone,
                       'blank': blank, 'grade': grade,
                       'pattern_density': pattern_density,
                       'layer': layer})

    def post(self, request):
        super().post(request)
        tool = request.POST.get('tool')
        node = request.POST.get('node', '')
        tone = request.POST.get('tone', '')
        blank = request.POST.get('blank', '')
        grade = request.POST.get('grade', '')
        pattern_density = request.POST.get('pattern_density', '')
        layer = request.POST.get('layer', '')
        if tool == 'MS03':
            version_count = released_info_alta.objects.values('version').distinct().filter(tool=tool, node=node,
                                                                                           tone=tone, blank=blank,
                                                                                           grade=grade,
                                                                                           pattern_density=pattern_density,
                                                                                           layer=layer)
        else:
            version_count = released_info.objects.values('version', 'id').distinct().filter(tool=tool, node=node,
                                                                                            tone=tone, blank=blank,
                                                                                            grade=grade,
                                                                                            pattern_density=pattern_density,
                                                                                            layer=layer,
                                                                                            cs_command='MDT')
        data = {'total': len(version_count), 'rows': version_count[self.startIndex: self.endIndex]}
        return JsonResponse(data, safe=False)


class ViewMDTInformation(BaseView):
    def get(self, request):
        release_id = request.GET.get('release_id')
        return render(request, 'info_tree/released/infotree_released_mdt_form.html',
                      {'release_id': release_id})
    def post(self, request):
        super().post(request)
        release_id = request.POST.get('release_id')
        query_set = released_mdt.objects.filter(released_id=release_id).values('cad_layer', 'data_type', 'writer_mdt',
                                                                               'writer_dose')
        return JsonResponse({'total': len(query_set), 'rows': query_set[self.startIndex: self.endIndex]}, safe=False)