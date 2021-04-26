from django.shortcuts import render

from jdv.models import lot_info
from tooling_form.models import import_list
from utilslibrary.base.base import BaseView
from django.shortcuts import render_to_response
from utilslibrary.utils.common_utils import getCurrentSessionID
from system.models import menu, user


# Create your views here.

# tree select
class TreeSelect(BaseView):

    def get(self, request):
        url = request.GET.get('url')
        return render(request, 'system_tree_select.html', {"url": url})


def page_not_found(self, exception):
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response


def page_error(self):
    return render_to_response('500.html')


def permission_error(self):
    return render_to_response('permission_error.html')


# home
class Home(BaseView):

    def get(self, request):
        # query tooling form list
        u_id = getCurrentSessionID(request)
        tooling_form_list = import_list.objects.filter(create_by=u_id, is_delete=0).order_by('-create_time')[0:10].values()
        # query in product tooling form
        in_production_tooling_form_list = import_list.objects.filter(create_by=u_id, is_delete=0, check_status=3).values()
        in_pro_count = in_production_tooling_form_list.count()
        # query complete tooling form
        com_tooling_form_list = import_list.objects.filter(create_by=u_id, is_delete=0, check_status=10).values()
        com_count = in_production_tooling_form_list.count()
        validating_lot_count = lot_info.objects.filter(status=1).count()
        pending_payment_lot_count = lot_info.objects.filter(status=3, payment_status=0).count()
        in_production_lot_count = lot_info.objects.filter(status=3, payment_status=1, release_status=1).count()
        return render(request, 'home.html', {"tooling_form_list": tooling_form_list, "in_pro_count": in_pro_count,
                                             "com_count": com_count, 'user_id': u_id, 'validating_lot_count':
                                                 validating_lot_count, 'pending_payment_lot_count':
                                                 pending_payment_lot_count, 'in_production_lot_count':
                                                 in_production_lot_count})


# index
class Index(BaseView):

    def get(self, request):
        # query menu
        _menu_list_parent = menu.objects.filter(is_delete=0, is_show=1, parent_id=0).order_by("sort")
        _menu_list_sub = menu.objects.filter(is_delete=0, is_show=1).exclude(parent_id=0).order_by("sort")
        # query role name
        user_id = getCurrentSessionID(request)
        if user_id == '':
            return render(request, 'system_login.html')

        _o = user.objects.get(id=user_id)
        _user_role_list = _o.user_role_set.all()
        role_names = ''
        for _user_role in _user_role_list:
            if role_names == '':
                role_names = _user_role.role.name
            else:
                role_names = role_names + ',' + _user_role.role.name

        return render(request, "index.html", {"menu_list_parent": _menu_list_parent, "menu_list_sub": _menu_list_sub,
                                              "role_names": role_names, 'user_id': user_id})


class CustomerIndex(BaseView):

    def get(self, request):
        # query menu
        _menu_list_parent = menu.objects.filter(is_delete=0, is_show=1, parent_id=0).order_by("sort")
        _menu_list_sub = menu.objects.filter(is_delete=0, is_show=1).exclude(parent_id=0).order_by("sort")
        # query role name
        user_id = getCurrentSessionID(request)
        if user_id == '':
            return render(request, 'system_login.html')

        _o = user.objects.get(id=user_id)
        _user_role_list = _o.user_role_set.all()
        role_names = ''
        for _user_role in _user_role_list:
            if role_names == '':
                role_names = _user_role.role.name
            else:
                role_names = role_names + ',' + _user_role.role.name

        return render(request, "customer_index.html",
                      {"menu_list_parent": _menu_list_parent, "menu_list_sub": _menu_list_sub,
                       "role_names": role_names, 'user_id': user_id})
