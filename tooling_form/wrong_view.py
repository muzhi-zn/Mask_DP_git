import copy
from _io import BytesIO

import xlwt
from django.db.models import Q
from django.forms import model_to_dict
from django.http.response import HttpResponse
from django.shortcuts import render

from tooling_form.models import import_check_list, import_error_list
from tooling_form.service import wrong_service
from tooling_form.service.wrong_service import WrongService
from tooling_form.tooling_view import *
from utilslibrary.base.base import BaseView
from utilslibrary.utils.date_utils import getDateConStr

'''
通过点击show tip no list 每行中的按钮，
获取tip_no 用来查询
'''


class WrongList_tipno(BaseView):
    '''
        def get(self,request):
        id = request.GET.get("id")
        print(id)
        if not id:
            return render(request, 'user_form.html')
        else:
            _o = import_error_list.objects.get(id=id)
            return render(request, 'wrong_form.html',{"import_error_list":_o})
    '''

    def get(self, request):
        print('a')
        tip_no = request.GET.get("tip_no")
        print(tip_no)
        id = request.POST.get('id')

        u_id = request.session[Constant.SESSION_CURRENT_USER_ID]
        print(u_id)
        # print(id)
        q = Q()
        q.connector = 'and'
        q.children.append(('is_delete', 0))  # 错误显示状态，0为需要显示，1为不显示
        q.children.append(('create_by', u_id))
        q.children.append(('import_data_id', id))
        # if tip_no:
        # q.children.append(('tip_no__contains',tip_no))
        # if error_code :
        # q.children.append(('error_code__contains',error_code))
        print('startIndex{} endIndex{}'.format(self.startIndex, self.endIndex))

        # 执行查询

        wrong_list = import_error_list.objects.filter(q).values()
        print(wrong_list)
        # return render(request,'wrong_list_tipno')

        # data = {}

        #  data["total"] = import_error_list.objects.filter(q).count()
        #  data["rows"] = list(wrong_list)

        # print(data)

        # return JsonResponse(data,safe=False)
        # tip_no = request.GET.get("tip_no")
        # print(tip_no)
        # if not id:
        # return render(request,'wrong_form.html')
        # else:
        # _o = import_error_list.objects.filter(import_data_id = id).values()
        # print(_o)
        return render(request, 'tooling_form/wrong_list.html', {"import_error_list": wrong_list})

    def post(self, request):
        # super().post(request)
        # -----------------------------
        # 需要获得翻页参数时添加
        # 代码中使用self.startIndex和self.endIndex获取相应范围的记录
        # ------------------------------
        # isadmin = request.POST.get('isadmin','')
        # super().post(request)
        # isadmin = request.POST.get('isadmin','')
        # 接收查询参数---与页面上要查询的条件匹配
        # tip_no = request.POST.get('tipno','')
        # error_code = request.POST.get('errorcode','')
        # print(tip_no,error_code)
        id = request.POST.get('id')
        is_delete = request.POST.get('is_delete')
        print(is_delete)
        u_id = request.session[Constant.SESSION_CURRENT_USER_ID]
        print(u_id)
        print(id)
        q = Q()
        q.connector = 'and'
        q.children.append(('is_delete', 0))  # 错误显示状态，0为需要显示，1为不显示
        q.children.append(('create_by', u_id))
        q.children.append(('import_data_id', id))
        # if tip_no:
        # q.children.append(('tip_no__contains',tip_no))
        # if error_code :
        # q.children.append(('error_code__contains',error_code))
        print('startIndex{} endIndex{}'.format(self.startIndex, self.endIndex))

        # 执行查询

        wrong_list = import_error_list.objects.filter(q).values()
        print(wrong_list)
        data = {}

        data["total"] = import_error_list.objects.filter(q).count()
        data["rows"] = list(wrong_list)

        print(data)

        return JsonResponse(data, safe=False)

        '''
        wrong_lists = import_error_list.objects.filter()
        wrongall = import_error_list.objects.all()
        wrongdata = {}
        wrongdata["total"] = import_error_list.objects.filter(error_status = 1).count()
        wronglist = list(wrong_lists)
        
        conter = wrongdata["total"] - 1
        while conter >= 0:
            print(conter)
            printer=wronglist[conter]
            
        
        
        return render_to_response("",locals())
        '''


'''
直接显示错误
通过user_id,is_delete控制
带有模糊查询
'''


# error list 列表
class WrongList(BaseView):
    def get(self, request):
        tip_no = request.GET.get('tip_no')
        print(id)
        return render(request, 'tooling_form/wrong_list.html', {'tip_no': tip_no})

    def post(self, request):
        super().post(request)
        # -----------------------------
        # 需要获得翻页参数时添加
        # 代码中使用self.startIndex和self.endIndex获取相应范围的记录
        # ------------------------------
        # isadmin = request.POST.get('isadmin','')
        # super().post(request)
        # isadmin = request.POST.get('isadmin','')
        # 接收查询参数---与页面上要查询的条件匹配
        data = {}
        tip_no = request.POST.get('tip_no')

        print(tip_no)
        u_id = request.session[Constant.SESSION_CURRENT_USER_ID]
        print(u_id)
        q = Q()
        q.connector = 'and'
        q.children.append(('is_delete', 0))  # 错误显示状态，0为需要显示，1为不显示
        q.children.append(('create_by', u_id))
        # if tip_no:
        #   q.children.append(('tip_no__contains', tip_no))
        # else:
        #     q.children.append(('tip_no', ''))
        # if error_code :
        #    q.children.append(('error_code__contains',error_code))
        print('startIndex{} endIndex{}'.format(self.startIndex, self.endIndex))

        # 执行查询

        wrong_list = import_error_list.objects.filter(q)[self.startIndex:self.endIndex].values()
        print(wrong_list)

        data["total"] = import_error_list.objects.filter(q).count()
        data["rows"] = list(wrong_list)

        print(data)

        return JsonResponse(data, safe=False)

        '''
        wrong_lists = import_error_list.objects.filter()
        wrongall = import_error_list.objects.all()
        wrongdata = {}
        wrongdata["total"] = import_error_list.objects.filter(error_status = 1).count()
        wronglist = list(wrong_lists)

        conter = wrongdata["total"] - 1
        while conter >= 0:
            print(conter)
            printer=wronglist[conter]



        return render_to_response("",locals())
        '''


# error list 修改
class WrongForm_type1(BaseView):
    def get(self, request):
        id = request.GET.get("id")
        print(id)
        if not id:
            return render(request, 'user_form.html')
        else:
            _o = import_error_list.objects.get(id=id)
            dict_list = []
            if _o and _o.parent_id > 0:
                # 解析循环JSON数据
                # '"[\'OMOG\', \'Binary_Cr_Qz\', \'PSM\']"'
                # str
                res = eval(_o.validate_value)
                # str -> list
                dict_list = eval(res)
            return render(request, 'tooling_form/wrong_form.html', {"import_error_list": _o, "dict_list": dict_list})

    def post(self, request):

        id = request.POST.get('id')
        import_data_id = request.POST.get('import_data_id')
        parent_id = request.POST.get('parent_id')
        regex_no = request.POST.get('regex_no')
        tip_no = request.POST.get('tip_no')
        import_data = request.POST.get('import_data')
        u_id = getCurrentSessionID(request)

        operation_str = request.POST.get('operation_import_data')
        print('operation_str =', operation_str)
        _s = ToolService()
        data = {}

        if operation_str is not None:
            op_check_result = ToolService().check_operation(operation_str)
            if op_check_result == 1:
                # 插入數據
                flag = _s.update_import_data_operation(id, import_data_id, tip_no, operation_str)
                flag_status = _s.update_import_error_message_log_status(tip_no)

                #判断该tipNo对应的所有异常资料是否均修改完成，若未修改完成，则继续修改；若修改完成则进行新增正式表或进行数据比对操作
                error_count = import_error_list.objects.filter(tip_no=tip_no, is_delete=0).count()

                if flag == 1 and flag_status == 1 and error_count > 0:
                    data["success"] = "true"
                    data["msg"] = "Success"
                elif flag == 1 and flag_status == 1 and error_count == 0:

                    '''
                        1.判断该tipNo是否在正式表存在，若不存在则新增
                        2.若存在，则进行数据一致性比对                    
                    '''
                    product_info_tip_no = product_info.objects.filter(tip_no=tip_no, is_delete=0)

                    # 若正式表没有该tipNo，则将该tipNo在临时表中的数据保存到正式表中
                    if product_info_tip_no.count() > 0:

                        # 根据tipNo获取import_list_id，用户数据比对
                        import_list_id = import_list.objects.get(tip_no=tip_no, is_delete=0)
                        tooling_check_data_service().check_data_main(tip_no, import_list_id.id, u_id)

                        data["success"] = "true"
                        data["msg"] = "Mask Data Checking"
                    else:
                        WrongService().add_import_data_copy_temp(tip_no)

                        data["success"] = "true"
                        data["msg"] = "Success"
                else:
                    data["success"] = "false"
                    data["msg"] = "Failed"
            else:
                data["success"] = False
                data["msg"] = "Failed"
            return JsonResponse(data, safe=False)

        _s = ToolService()
        flag = _s.update_import_data(id, import_data_id, tip_no, parent_id, regex_no, import_data)
        flag_status = _s.update_import_error_message_log_status(tip_no)

        error_count = import_error_list.objects.filter(tip_no=tip_no, is_delete=0).count()

        if flag == 1 and flag_status == 1 and error_count > 0:
            data["success"] = "true"
            data["msg"] = "Success"
        elif flag == 1 and flag_status == 1 and error_count == 0:

            '''
                1.判断该tipNo是否在正式表存在，若不存在则新增
                2.若存在，则进行数据一致性比对                    
            '''
            product_info_tip_no = product_info.objects.filter(tip_no=tip_no, is_delete=0)

            # 若正式表没有该tipNo，则将该tipNo在临时表中的数据保存到正式表中
            if product_info_tip_no.count() > 0:

                # 根据tipNo获取import_list_id，用户数据比对
                import_list_id = import_list.objects.get(tip_no=tip_no, is_delete=0)
                tooling_check_data_service().check_data_main(tip_no, import_list_id.id, u_id)

                data["success"] = "true"
                data["msg"] = "Mask Data Checking"
            else:
                WrongService().add_import_data_copy_temp(tip_no)

                data["success"] = "true"
                data["msg"] = "Success"
        else:
            data["success"] = "false"
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)


# wrong list export
class WrongListExport(BaseView):

    def get(self, request):
        tip_no = request.GET.get('tip_no')

        print(tip_no)
        u_id = request.session[Constant.SESSION_CURRENT_USER_ID]
        print(u_id)
        q = Q()
        q.connector = 'and'
        q.children.append(('is_delete', 0))  # 错误显示状态，0为需要显示，1为不显示
        q.children.append(('create_by', u_id))
        if tip_no:
            q.children.append(('tip_no__contains', tip_no))
        else:
            q.children.append(('tip_no', ''))
        # if error_code :
        #    q.children.append(('error_code__contains',error_code))

        # 执行查询

        wrong_list = import_error_list.objects.filter(q)

        time = getDateConStr()
        filename = time + '.xls'
        # 设置HTTPResponse的类型
        reposnse = HttpResponse(content_type='application/vnd.ms-excel')
        # 创建一个文件对象
        reposnse['Content-Disposition'] = 'attachment;filename=' + filename
        # 创建一个sheet对象
        wb = xlwt.Workbook(encoding='utf-8')
        sheet = wb.add_sheet('Wrror List')
        # 写入文件标题
        sheet.write(0, 0, 'Index')
        sheet.write(0, 1, 'Tip NO')
        sheet.write(0, 2, 'Column Name')
        sheet.write(0, 3, 'Import Data')
        sheet.write(0, 4, 'Error Description')
        sheet.write(0, 5, 'Error Code')
        data_row = 1
        for item in wrong_list:
            sheet.write(data_row, 0, data_row)
            sheet.write(data_row, 1, item.tip_no)
            sheet.write(data_row, 2, item.column_name)
            sheet.write(data_row, 3, item.import_data)
            sheet.write(data_row, 4, item.error_description)
            sheet.write(data_row, 5, item.error_code)
            data_row += 1

        output = BytesIO()
        wb.save(output)
        output.seek(0)
        reposnse.write(output.getvalue())
        return reposnse


# check list 列表
class CheckList(BaseView):

    def get(self, request):
        return render(request, 'tooling_form/tooling_check_list.html', {'tip_no': request.GET.get('tip_no')})

    def post(self, request):
        super().post(request)

        tip_no = request.POST.get('tip_no', '')

        q = Q()

        q.connector = 'and'
        q.children.append(('is_delete', 0))

        if tip_no:
            q.children.append(('tip_no', tip_no))

        results = import_check_list.objects.filter(q)[self.startIndex:self.endIndex].values()

        data = {"total": import_check_list.objects.filter(q).count(), "rows": list(results)}

        return JsonResponse(data, safe=False)


# check list view
class CheckListView(BaseView):

    def get(self, request):
        tip_no = request.GET.get("tip_no")
        mask_name = request.GET.get("mask_name")
        sheet_name = request.GET.get("sheet_name")

        q = Q()

        q.connector = 'and'
        q.children.append(('is_delete', 0))

        if tip_no:
            q.children.append(('tip_no', tip_no))
        if mask_name:
            q.children.append(('mask_name', mask_name))

        # 获取所有在checklist中的sheet_name
        results = import_check_list.objects.filter(q)

        sheet_name_list = []
        # 前台判断显示 0隐藏 1显示
        tab2 = 0
        tab3 = 0
        tab4 = 0
        tab5 = 0
        tab6 = 0
        tab7 = 0

        for loop in results:
            sheet_name_list.append(loop.sheet_name)

            if loop.sheet_name == 'Tapeout_Info':
                tab2 = 1
            elif loop.sheet_name == 'Device_Info':
                tab3 = 1
            elif loop.sheet_name == 'CCD_Table':
                tab4 = 1
            elif loop.sheet_name == 'Boolean_Info':
                tab5 = 1
            elif loop.sheet_name == 'Layout_Info':
                tab6 = 1
            elif loop.sheet_name == 'MLM_Info':
                tab7 = 1

        return render(request, 'tooling_form/tooling_check_list_view.html',
                      {"tip_no": tip_no, "mask_name": mask_name, "sheet_name": sheet_name,
                       "sheet_name_list": sheet_name_list, "tab2": tab2, "tab3": tab3, "tab4": tab4, "tab5": tab5,
                       "tab6": tab6, "tab7": tab7
                       })

# check list 列表
class CheckListDelete(BaseView):

    def get(self, request):

        id = request.GET.get('id', '')
        return WrongService().check_list_delete(id, getCurrentSessionID(request))

