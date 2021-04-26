# -*- coding: utf-8 -*-
# Create your views here.
from django.shortcuts import render
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from utilslibrary.base.base import BaseView
from django.db.models import Q
from infotree.models import cec
from infotree.service.cec_service import cec_upload_service
from utilslibrary.utils.date_utils import getDateStr, getMilliSecond
from utilslibrary.utils.common_utils import getCurrentSessionName, getCurrentSessionID
import os


class cec_list(BaseView):

    def get(self, request):
        if request.method == 'GET':
            return render(request, 'info_tree/cec/infotree_cec_list.html')

    def post(self, request):
        if request.method == 'POST':
            super().post(request)

            cec_name = request.POST.get('s_cec_name')

            q = Q()
            q.connector = 'and'
            q.children.append(('is_delete', 0))

            if cec_name:
                q.children.append(('cec_name__contains', cec_name))

            _o = cec.objects.filter(q).order_by('-id').values()[self.startIndex: self.endIndex]

            print(_o.query)

            data = {'total': cec.objects.filter(q).count(), 'rows': list(_o)}

            return JsonResponse(data, safe=False)


class cec_view(BaseView):

    def get(self, request):
        id = request.GET.get("id")
        if not id:
            return render(request, 'info_tree/cec/infotree_cec_form.html')
        else:
            _o = cec.objects.get(id=id)
            path = os.path.join(_o.cec_path, _o.cec_name)
            cec_data = ''
            with open(path, 'r') as f:
                for line in f:
                    cec_data += line
            f.close()
            return render(request, 'info_tree/cec/infotree_cec_form.html', {"cec": _o, 'cec_data': cec_data})


class cec_upload(BaseView):

    def get(self, request):
        _o = cec()
        _o.is_delete = 1
        _o.create_date = getDateStr()
        _o.create_time = getMilliSecond()
        _o.create_by = getCurrentSessionID(request)
        _o.create_name = getCurrentSessionName(request)
        _o.save()

        folder_name = str(getMilliSecond()) + '_' + str(str(_o.id).zfill(8))

        cec_ = cec.objects.get(id=_o.id)
        print(type(folder_name), folder_name)
        cec_.folder_name = folder_name
        cec_.save()

        return render(request, 'info_tree/cec/infotree_cec_upload.html', {'cec_id': _o.id})

    def post(self, request):
        return cec_upload_service().file_upload(request)


@csrf_exempt
def cec_check_file_exists(request):
    data = {}

    file_name = request.POST.get('file_name')

    _o = cec.objects.filter(cec_name=file_name, is_delete=0).count()
    print(_o)
    if _o == 0:
        data['success'] = True
    else:
        data['success'] = False

    return JsonResponse(data, safe=False)
