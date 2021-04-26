from django.shortcuts import render, HttpResponse
from django.http.response import JsonResponse
from utilslibrary.base.base import BaseView
from system.models import sync_config, sync_log, sync_log_detail
from django.db.models import Q
from system.service.sync_service import Sync_Service, SYNC_JOB_SERVICE


# sync list
class sync_list(BaseView):

    def get(self, request):
        if request.method == 'GET':
            return render(request, 'system_sync_list.html')

    def post(self, request):
        if request.method == 'POST':
            # user_id = request.session.get(Constant.SESSION_CURRENT_USER_ID)
            # super().post(request)
            # q = Q()
            # q.connector = 'and'
            # q.children.append(('is_delete', 0))
            #
            # sync_config_list = sync_config.objects.filter(q).order_by('sort').values()[self.startIndex: self.endIndex]
            sync_config_list = sync_config.objects.all().values()
            data = {}
            # data['total'] = sync_config.objects.filter(q).count()
            data['total'] = sync_config.objects.all().values().count()
            data['rows'] = list(sync_config_list)

            print(data['total'], data['rows'])

            return JsonResponse(data, safe=False)


# sync view
class sync_view(BaseView):

    def get(self, request):
        if request.method == 'GET':
            sync_id = request.GET.get('id')
            if not sync_id:
                return render(request, 'system_sync_form.html')
            else:
                _o = sync_config.objects.get(id=sync_id)
                print(_o)
                return render(request, 'system_sync_form.html', {"sync": _o})


# sync add
class sync_add(BaseView):

    def get(self, request):
        if request.method == 'GET':
            _o = sync_config()
            return render(request, 'system_sync_form.html', {"sync": _o, "method": "add"})

    def post(self, request):
        if request.method == 'POST':
            m_sync_name = request.POST.get('sync_name')
            m_enable = request.POST.get('enable')
            m_mode = request.POST.get('mode')
            m_day_of_week = request.POST.get('day_of_week')
            m_hour = request.POST.get('hour', 0)
            m_minute = request.POST.get('minute', 0)
            m_second = request.POST.get('second', 0)
            m_ldap_server_pool = request.POST.get('ldap_server_pool')
            m_ldap_server_port = request.POST.get('ldap_server_port')
            m_admin_dn = request.POST.get('admin_dn')
            m_admin_pwd = request.POST.get('admin_pwd')
            m_search_base = request.POST.get('search_base')
            m_group = request.POST.get('group')
            m_default = request.POST.get('default')

            _o = sync_config()
            _o.sync_name = m_sync_name
            _o.enable = m_enable
            _o.mode = m_mode
            _o.day_of_week = m_day_of_week
            _o.hour = m_hour
            _o.minute = m_minute
            _o.second = m_second
            _o.ldap_server_pool = m_ldap_server_pool
            _o.ldap_server_port = m_ldap_server_port
            _o.admin_dn = m_admin_dn
            _o.admin_pwd = m_admin_pwd
            _o.search_base = m_search_base
            _o.group = m_group
            _o.default = m_default

            _s = Sync_Service()

            return _s.add_sync(_o)


# sync edit
class sync_edit(BaseView):

    def get(self, request):
        if request.method == 'GET':
            sync_id = request.GET.get('id')
            if not sync_id:
                return render(request, 'system_sync_form.html')
            else:
                _o = sync_config.objects.get(id=sync_id)
                print(_o)
                return render(request, 'system_sync_form.html', {"sync": _o, "method": "edit"})

    def post(self, request):
        if request.method == 'POST':
            m_id = request.POST.get('id')
            m_sync_name = request.POST.get('sync_name')
            m_enable = request.POST.get('enable')
            m_mode = request.POST.get('mode')
            m_mode_time = request.POST.get('mode_time')
            m_ldap_server_pool = request.POST.get('ldap_server_pool')
            m_ldap_server_port = request.POST.get('ldap_server_port')
            m_admin_dn = request.POST.get('admin_dn')
            m_admin_pwd = request.POST.get('admin_pwd')
            m_search_base = request.POST.get('search_base')
            m_group = request.POST.get('group')
            m_default = request.POST.get('default')

            _o = sync_config.objects.get(id=m_id)

            _o.sync_name = m_sync_name
            _o.enable = m_enable
            _o.mode = m_mode
            _o.mode_time = m_mode_time
            _o.ldap_server_pool = m_ldap_server_pool
            _o.ldap_server_port = m_ldap_server_port
            _o.admin_dn = m_admin_dn
            _o.admin_pwd = m_admin_pwd
            _o.search_base = m_search_base
            _o.group = m_group
            _o.default = m_default
            _s = Sync_Service()

            return _s.upd_sync(_o, m_id)


# sync del
class sync_del(BaseView):

    def get(self, request):
        if request.method == 'GET':
            return render(request, 'system_sync_list.html')

    def post(self, request):
        if request.method == 'POST':
            return


# sync log
class sync_log_list(BaseView):

    def get(self, request):
        if request.method == 'GET':
            sync_id = request.GET.get('id', '')
            return render(request, 'system_sync_log_list.html', {"sync_id": sync_id})

    def post(self, request):
        if request.method == 'POST':
            # request param
            c_id = request.POST.get('s_c_id', '')
            start_time = request.POST.get('s_start_time', '')
            end_time = request.POST.get('s_end_time', '')

            super().post(request)
            q = Q()
            q.connector = 'and'
            q.children.append(('is_delete', 0))

            if c_id:
                q.children.append(('config_id', c_id))

            if start_time:
                q.children.append(('start_time__contains', start_time))

            if end_time:
                q.children.append(('end_time__contains', end_time))

            log_list = sync_log.objects.filter(q).order_by('-id').values()[self.startIndex: self.endIndex]

            data = {}
            data['total'] = sync_log.objects.all().values().count()
            data['rows'] = list(log_list)

            print(data['total'], data['rows'])

            return JsonResponse(data, safe=False)


# sync log view
class sync_log_view(BaseView):

    def get(self, request):
        if request.method == 'GET':
            sync_id = request.GET.get('id')
            if not sync_id:
                return render(request, 'system_sync_log_form.html')
            else:
                _o = sync_log.objects.get(id=sync_id)
                print(_o)
                return render(request, 'system_sync_form.html', {"sync": _o})


# sync log detail
class sync_log_detail_list(BaseView):

    def get(self, request):
        if request.method == 'GET':
            return render(request, 'system_sync_log_detail_list.html')

    def post(self, request):
        if request.method == 'POST':
            # request param
            sync_log_id = request.POST.get('roleId', '')
            super().post(request)
            q = Q()
            q.connector = 'and'
            q.children.append(('is_delete', 0))

            if sync_log_id:
                q.children.append(('log_id', sync_log_id))

            log_detail_list = sync_log_detail.objects.filter(q).order_by('-id').values()[self.startIndex: self.endIndex]

            data = {}
            data['total'] = sync_log_detail.objects.filter(q).values().count()
            data['rows'] = list(log_detail_list)

            print(data['total'], data['rows'])

            return JsonResponse(data, safe=False)


SYNC_JOB_SERVICE()
