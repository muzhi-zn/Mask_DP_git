from utilslibrary.base.base import BaseService, BaseView
from django.shortcuts import render_to_response, render
from tooling_form.models import import_list, product_info, tapeout_info, device_info, ccd_table, boolean_info, layout_info, \
    mlm_info
import json
from django.db.models import F, Q
from django.http.response import JsonResponse
from utilslibrary.system_constant import Constant
from tooling_form.service.show_tip_no_service import ShowTipNoListService
from system.models import user, user_role

'''
显示TIP_no信息
'''


class ShowTipNoList(BaseView):
    def get(self, request):
        return render(request, 'tooling_form/tooling_show_tip_no_list.html')

    def post(self, request):
        super().post(request)
        tip_no = request.POST.get('tipno', '')
        u_id = request.session[Constant.SESSION_CURRENT_USER_ID]

        # up_list = import_list.objects.all().values()
        # print(up_list)
        # for index in up_list:
        #     login_name = user.objects.get(id=index['create_by']).loginname
        #     f_name = import_list.objects.filter(id=index['id']).update(create_name=login_name)

        # 查詢是否為管理員
        is_admin = user_role.objects.filter(user_id=u_id)
        role_id_list = [role_id.role_id for role_id in is_admin ]
        if 10 in role_id_list or 18 in role_id_list:
            office_user_list = user.objects.filter(is_delete=0).values('id')
        else:
            # 查詢 user 部門 id
            u_office_id = user.objects.filter(id=u_id).values()[0]['office_id']

            # 查詢所有部門id為u_office_id的用戶
            office_user_list = user.objects.filter(is_delete=0,
                                                   office_id=u_office_id).values('id')

        q_1 = Q()
        q_1.connector = 'or'

        for office_user_id in office_user_list:
            q_1.children.append(('create_by', office_user_id['id']))  # 用户ID，匹配用户

        q_2 = Q()
        q_2.connector = 'and'
        q_2.children.append(('is_delete', 0))
        if tip_no:
            q_2.children.append(('tip_no__contains', tip_no))

        q = q_1 & q_2

        # 执行查询
        tip_no_list = import_list.objects.filter(q).order_by('-id')[self.startIndex:self.endIndex].values()
        data = {}

        data["total"] = import_list.objects.filter(q).count()
        data["rows"] = list(tip_no_list)

        return JsonResponse(data, safe=False)


class TipNoform(BaseView):
    def get(self, request):
        id = request.GET.get("id")
        print(id)
        if not id:
            return render(request, 'tooling_show_tip_no_form.html')
        else:
            _o = import_list.objects.get(id=id)
            return render(request, 'show_tip_no_form.html', {"upload": _o})

    def post(self, request):
        # super().post(request)
        id = request.POST.get('id')
        print(id)
        '''
        print('startIndex{} endIndex{}'.format(self.startIndex,self.endIndex))
        wrong_list = import_error_list.objects.filter().values()
        wrong_all = import_error_message_log().objects.all()     
                
        data = {}
        wrongrow = list(wrong_list)
        
        '''

        '''
        import_data_id = 
        tip_no = 
        import_data = 
        error_code = 
        error_description = 
        error_type =     
        '''
        return render_to_response("show_tip_no_form.html", locals())


# ShowTipNoList_del
class ShowTipNo_del(BaseView):

    def get(self, request):
        data = {}
        ids = request.GET.get("ids")
        data["success"] = True
        data["msg"] = "Success"
        _o = import_list()
        _o.id = ids
        _s = ShowTipNoListService()

        return _s.del_upload(_o)


# ShowTipNo_data_view
class ShowTipNo_data_view(BaseView):

    def get(self, request):
        # id = request.GET.get("id")
        tip_no = request.GET.get("tip_no")
        print('aaa', tip_no)

        # _o = import_data_temp.objects.filter(tip_no=tip_no)
        return render(request, 'tooling_form/tooling_show_tip_no_import_data_list.html', {"tip_no": tip_no})

    def post(self, request):
        super().post(request)
        tip_no = request.POST.get('tip_no')

        q = Q()
        q.connector = 'and'
        q.children.append(('is_delete', 0))
        if tip_no:
            q.children.append(('tip_no', tip_no))

        product_info_data = product_info.objects.filter(q).order_by('id')[self.startIndex:self.endIndex].values()

        data = {}
        data["total"] = product_info.objects.filter(q).order_by('id').count()
        data["rows"] = list(product_info_data)

        return JsonResponse(data, safe=False)


# ShowTipNo_product_info
class ShowTipNo_product_info(BaseView):
    def get(self, request):
        tip_no = request.GET.get("tip_no")
        return render(request, 'tooling_data_view_product_info.html', {"tip_no": tip_no})

    def post(self, request):
        super().post(request)

        tip_no = request.POST.get('tip_no')
        q = Q()
        q.connector = 'and'
        q.children.append(('is_delete', 0))
        if tip_no:
            q.children.append(('tip_no', tip_no))

        product_info_data = tapeout_info.objects.filter(q).order_by('id')[self.startIndex:self.endIndex].values()

        data = {}
        data["total"] = tapeout_info.objects.filter(q).count()
        data["rows"] = list(product_info_data)

        return JsonResponse(data, safe=False)

#-------------------------------------------------------------------
# ShowTipNo_tapeout_info
class ShowTipNo_tapeout_info(BaseView):
    def get(self, request):
        tip_no = request.GET.get("tip_no")
        return render(request, 'tooling_data_view_product_info.html', {"tip_no": tip_no})

    def post(self, request):
        super().post(request)
        tip_no = request.POST.get('tip_no')
        mask_name = request.POST.get('mask_name')

        q = Q()
        q.connector = 'and'
        q.children.append(('is_delete', 0))
        if tip_no:
            q.children.append(('tip_no', tip_no))
        if mask_name:
            q.children.append(('mask_name', mask_name))

        tapeout_info_data = tapeout_info.objects.filter(q).order_by('id')[self.startIndex:self.endIndex].values()

        data = {}
        data["total"] = tapeout_info.objects.filter(q).count()
        data["rows"] = list(tapeout_info_data)

        return JsonResponse(data, safe=False)


# ShowTipNo_device_info
class ShowTipNo_device_info(BaseView):
    def get(self, request):
        tip_no = request.GET.get("tip_no")
        return render(request, 'tooling_data_view_product_info.html', {"tip_no": tip_no})

    def post(self, request):
        super().post(request)
        mask_name = request.POST.get('mask_name')
        tip_no = request.POST.get('tip_no')
        res = boolean_info.objects.filter(mask_name=mask_name)

        #tip_no_list = []
        boolean_index_list = []
        source_db_list = []

        for loop in res:
            #tip_no_list.append(loop.tip_no)
            boolean_index_list.append(loop.boolean_index)
            source_db_list.append(loop.source_db)

        q = Q()
        q.connector = 'and'
        q.children.append(('is_delete', 0))
        if tip_no:
            q.children.append(('tip_no', tip_no))
        if boolean_index_list:
            q.children.append(('boolean_index__in', boolean_index_list))
        if source_db_list:
            q.children.append(('source_db__in', source_db_list))

        device_info_data = device_info.objects.filter(q).order_by('id')[self.startIndex:self.endIndex].values()

        data = {}
        data["total"] = device_info.objects.filter(q).count()
        data["rows"] = list(device_info_data)

        return JsonResponse(data, safe=False)


# ShowTipNo_ccd_table
class ShowTipNo_ccd_table(BaseView):
    def get(self, request):
        tip_no = request.GET.get("tip_no")
        return render(request, 'tooling_data_view_product_info.html', {"tip_no": tip_no})

    def post(self, request):
        super().post(request)
        tip_no = request.POST.get('tip_no')
        mask_name = request.POST.get('mask_name')

        q = Q()
        q.connector = 'and'
        q.children.append(('is_delete', 0))
        if tip_no:
            q.children.append(('tip_no', tip_no))
        if mask_name:
            q.children.append(('mask_name', mask_name))
        ccd_table_data = ccd_table.objects.filter(q).order_by('id')[self.startIndex:self.endIndex].values()

        data = {}
        data["total"] = ccd_table.objects.filter(q).count()
        data["rows"] = list(ccd_table_data)

        return JsonResponse(data, safe=False)


# ShowTipNo_boolean_info
class ShowTipNo_boolean_info(BaseView):
    def get(self, request):
        tip_no = request.GET.get("tip_no")
        return render(request, 'tooling_data_view_boolean_info.html', {"tip_no": tip_no})

    def post(self, request):
        super().post(request)
        tip_no = request.POST.get('tip_no')
        mask_name = request.POST.get('mask_name')

        q = Q()
        q.connector = 'and'
        q.children.append(('is_delete', 0))
        if tip_no:
            q.children.append(('tip_no', tip_no))
        if mask_name:
            q.children.append(('mask_name', mask_name))

        boolean_info_data = boolean_info.objects.filter(q).order_by('id')[self.startIndex:self.endIndex].values()

        data = {}
        data["total"] = boolean_info.objects.filter(q).order_by('id').count()
        data["rows"] = list(boolean_info_data)

        return JsonResponse(data, safe=False)


# ShowTipNo_layout_info
class ShowTipNo_layout_info(BaseView):

    def get(self, request):
        tip_no = request.GET.get("tip_no")
        return render(request, 'tooling_data_view_layout_info.html', {"tip_no": tip_no})

    def post(self, request):
        super().post(request)
        tip_no = request.POST.get('tip_no')
        mask_name = request.POST.get('mask_name')

        q = Q()
        q.connector = 'and'
        q.children.append(('is_delete', 0))
        if tip_no:
            q.children.append(('tip_no', tip_no))
        if mask_name:
            q.children.append(('mask_name', mask_name))

        layout_info_data = layout_info.objects.filter(q).order_by('id')[self.startIndex:self.endIndex].values()

        data = {}
        data["total"] = layout_info.objects.filter(q).count()
        data["rows"] = list(layout_info_data)

        return JsonResponse(data, safe=False)


# ShowTipNo_mlr_info
class ShowTipNo_mlm_info(BaseView):
    def get(self, request):
        tip_no = request.GET.get("tip_no")
        return render(request, 'tooling_data_view_mlm_info.html', {"tip_no": tip_no})

    def post(self, request):
        super().post(request)
        tip_no = request.POST.get('tip_no')
        mask_name = request.POST.get('mask_name')

        q = Q()
        q.connector = 'and'
        q.children.append(('is_delete', 0))
        if tip_no:
            q.children.append(('tip_no', tip_no))
        if mask_name:
            q.children.append(('mask_name', mask_name))

        mlm_info_data = mlm_info.objects.filter(q).order_by('id')[self.startIndex:self.endIndex].values()

        data = {}
        data["total"] = mlm_info.objects.filter(q).count()
        data["rows"] = list(mlm_info_data)

        return JsonResponse(data, safe=False)
