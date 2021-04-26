# -*- coding: utf-8 -*-
# Create your views here.
import json

from django.shortcuts import render
from django.http.response import JsonResponse
from utilslibrary.base.base import BaseView
from django.db.models import Q
from infotree.models import cd_map
from infotree.service.cd_map_service import cd_map_upload_service
from utilslibrary.utils.date_utils import getDateStr, getMilliSecond
from utilslibrary.utils.common_utils import getCurrentSessionName, getCurrentSessionID
from django.views.decorators.csrf import csrf_exempt


class cd_map_list(BaseView):

    def get(self, request):
        if request.method == 'GET':
            return render(request, 'info_tree/cd_map/infotree_cd_map_list.html')

    def post(self, request):
        if request.method == 'POST':
            super().post(request)

            dat_name = request.POST.get('s_dat_name')
            prm_name = request.POST.get('s_prm_name')

            q = Q()
            q.connector = 'and'
            q.children.append(('is_delete', 0))

            if dat_name:
                q.children.append(('cd_map_dat_name__contains', dat_name))

            if prm_name:
                q.children.append(('index_prm_name__contains', prm_name))

            _o = cd_map.objects.filter(q).order_by('-id').values()[self.startIndex: self.endIndex]

            data = {'total': cd_map.objects.filter(q).count(), 'rows': list(_o)}

            return JsonResponse(data, safe=False)


class cd_map_view(BaseView):

    def get(self, request):
        id = request.GET.get("id")
        if not id:
            return render(request, 'info_tree/cd_map/infotree_cd_map_form.html')
        else:
            _o = cd_map.objects.get(id=id)
            return render(request, 'info_tree/cd_map/infotree_cd_map_form.html', {"cd_map": _o})


class cd_map_upload(BaseView):
    def get(self, request):
        _o = cd_map()
        _o.is_delete = 1
        _o.create_date = getDateStr()
        _o.create_time = getMilliSecond()
        _o.create_by = getCurrentSessionID(request)
        _o.create_name = getCurrentSessionName(request)
        _o.save()

        folder_name = str(getMilliSecond()) + '_' + str(str(_o.id).zfill(8))

        cd_m = cd_map.objects.get(id=_o.id)
        print(type(folder_name), folder_name)
        cd_m.folder_name = folder_name
        cd_m.save()

        return render(request, 'info_tree/cd_map/infotree_cd_map_upload.html', {'cd_map_id': _o.id})

    def post(self, request):
        return cd_map_upload_service().file_upload(request)


@csrf_exempt
def cd_map_check_file_exists(request):
    data = {}

    file_name = request.POST.get('file_name')
    file_name = file_name.split(',')

    _o = cd_map.objects.filter(Q(cd_map_dat_name__in=file_name) | Q(index_prm_name__in=file_name), is_delete=0).count()

    if _o == 0:
        data['success'] = True
    else:
        data['success'] = False

    return JsonResponse(data, safe=False)
