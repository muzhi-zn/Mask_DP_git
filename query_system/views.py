import json
import os

from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Q
# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from query_system.service.jdv_service import upload_jdv_file, send_mail
from system.models import sgd_user
from utilslibrary.system_constant import Constant
from jdv.models import lot_info
from making.models import convert_status, convert_status_stage
from query_system.models import jdv_data, jdv_data_layer, jdv_data_device
from system.sgd_view import create_sgd
from tooling_form.models import product_info
from utilslibrary.base.base import BaseView
from django.db import connection, transaction

from utilslibrary.utils.date_utils import getDateStr


class ProductionList(BaseView):
    def get(self, request):
        return render(request, 'query_system/production_list.html')

    def post(self, request):
        super().post(request)
        product_list = lot_info.objects.values('product_name', 'tip_no').distinct().filter(is_delete=0,
                                                                                           lot_id__isnull=False)
        query_list = []
        for product in product_list:
            query_dict = {}
            total_layers = lot_info.objects.values('mask_name').distinct().filter(product_name=product['product_name'],
                                                                                  tip_no=product['tip_no'],
                                                                                  is_delete=0).count()
            hold_layers = jdv_data.objects.values('mask_name').distinct().filter(product_name=product['product_name'],
                                                                                 tip_no=product['tip_no'],
                                                                                 hold_status=1).count()
            waiting_layers = convert_status.objects.values('mask_name').distinct().filter(
                Q(stage='Fracture', status=2) |
                Q(Q(status=2) | Q(operation_status=1), stage='XOR'),
                tip_no=product['tip_no']
            ).count()
            release_layers = jdv_data.objects.values('mask_name').distinct().filter(tip_no=product['tip_no'],
                                                                                    release_status=1).count()
            no_error_layers = convert_status.objects.filter(~Q(Q(status=3) | Q(status=4)) & ~Q(operation_status=1),
                                                            tip_no=product['tip_no'],
                                                            stage__in=['Fracture', 'XOR'])
            running_layers = no_error_layers.values('mask_name').distinct().filter(status=1).count()
            query_dict['tip_no'] = product['tip_no']
            query_dict['product_name'] = product['product_name']
            query_dict['total_layers'] = total_layers
            query_dict['running_layers'] = running_layers
            query_dict['waiting_release_layers'] = waiting_layers
            query_dict['release_layers'] = release_layers
            query_dict['hold_layers'] = hold_layers
            query_list.append(query_dict)
        return JsonResponse({'total': len(query_list), 'rows': query_list}, safe=False)


class DeviceListView(BaseView):
    def post(self, request):
        tip_no = request.POST.get("tip_no")
        type = request.POST.get("type")
        query_list = []
        if type == "running":
            no_error_layers = convert_status.objects.filter(~Q(Q(status=3) | Q(status=4)) & ~Q(operation_status=1),
                                                            tip_no=tip_no, stage__in=['Fracture', 'XOR'])
            query_set = no_error_layers.values('mask_name', 'lot_id').distinct().filter(status=1)
        elif type == "wait_release":
            query_set = convert_status.objects.values('mask_name', 'lot_id').distinct().filter(
                Q(stage='Fracture', status=2) |
                Q(Q(status=2) | Q(operation_status=1), stage='XOR'), tip_no=tip_no
            )
        elif type == "released":
            query_set = jdv_data.objects.values('mask_name', 'lot_id').filter(tip_no=tip_no,
                                                                              release_status=1)
        elif type == "hold":
            query_set = jdv_data.objects.values('mask_name', 'lot_id').filter(tip_no=tip_no,
                                                                              hold_status=1)
        else:
            query_set = lot_info.objects.values('mask_name', 'lot_id').distinct().filter(tip_no=tip_no,
                                                                                         is_delete=0)
        for query in query_set:
            query_dict = {}
            query_dict['tip_no'] = tip_no
            query_dict['product_name'] = query['mask_name'].split('-')[0]
            query_dict['mask_name'] = query['mask_name']
            query_dict['layer'] = query['mask_name'].split('-')[-1][0:3]
            query_dict['lot_id'] = query['lot_id']
            # query_dict['status'] = query['status']
            # 判断mask_name的状态
            # layer_status = jdv_data_layer.objects.filter(tip_no=tip_no, mask_name=query['mask_name'])
            query_list.append(query_dict)
        return JsonResponse({'total': len(query_list), 'rows': query_list}, safe=False)


class MaskNameGroupStatusView(BaseView):
    """同一mask_name聚合device下的状态"""

    def get(self, request):
        tip_no = request.GET.get("tip_no")
        mask_name = request.GET.get("mask_name")
        return render(request, 'query_system/mask_name_stage_status.html', {'tip_no': tip_no, 'mask_name': mask_name})

    @csrf_exempt
    def post(self, request):
        """获取聚合device的状态"""
        tip_no = request.POST.get("tip_no")
        mask_name = request.POST.get("mask_name")
        col_list = convert_status.objects.filter(tip_no=tip_no, mask_name=mask_name).values('stage').distinct()
        c_list = []
        for col in col_list:
            c_list.append(col['stage'])
        stage_status_dict_list = []
        for col in col_list:
            stage_status_dict = {}
            status_set = convert_status.objects.values('status', 'operation_status').distinct().filter(tip_no=tip_no,
                                                                                                       mask_name=mask_name,
                                                                                                       stage=col[
                                                                                                           'stage'])
            if len(status_set) == 1 and status_set[0]['status'] == 2:
                stage_status_dict[col['stage']] = 3
                stage_status_dict_list.append(stage_status_dict)
            elif len(status_set) == 1 and status_set[0]['status'] == 4:
                query_set = convert_status.objects.filter(tip_no=tip_no, mask_name=mask_name,
                                                          stage=col['stage'], status=4)
                for query in query_set:
                    if query.operation_status != 1:
                        stage_status_dict[col['stage']] = 4
                        stage_status_dict_list.append(stage_status_dict)
                        break
                    else:
                        stage_status_dict[col['stage']] = 3
                        stage_status_dict_list.append(stage_status_dict)
                        break
            elif len(status_set) != 1:
                for status in status_set:
                    if 2 in status.values():
                        continue
                    if 4 in status.values():
                        query_set = convert_status.objects.filter(tip_no=tip_no, mask_name=mask_name,
                                                                  stage=col['stage'], status=4)
                        for query in query_set:
                            if query.operation_status != 1:
                                stage_status_dict[col['stage']] = 4
                                stage_status_dict_list.append(stage_status_dict)
                            else:
                                stage_status_dict[col['stage']] = 3
                                stage_status_dict_list.append(stage_status_dict)
                    elif 3 in status.values():
                        stage_status_dict[col['stage']] = 2
                        stage_status_dict_list.append(stage_status_dict)
                    continue
            elif len(status_set) != 1:
                for status in status_set:
                    if 1 in status.values():
                        stage_status_dict[col['stage']] = 0
                        stage_status_dict_list.append(stage_status_dict)
                        break
            elif len(status_set) == 1 and status_set[0]['status'] == 3:
                stage_status_dict[col['stage']] = 2
                stage_status_dict_list.append(stage_status_dict)
            elif len(status_set) != 1:
                for status in status_set:
                    if 3 in status.values():
                        stage_status_dict[col['stage']] = 2
                        stage_status_dict_list.append(stage_status_dict)
                        break
            elif len(status_set) == 1 and status_set[0]['status'] == 1:
                stage_status_dict[col['stage']] = 1
                stage_status_dict_list.append(stage_status_dict)
            else:
                stage_status_dict[col['stage']] = 0
                stage_status_dict_list.append(stage_status_dict)
        return JsonResponse({'col_list': c_list, 'data': stage_status_dict_list}, safe=False)


class StageStatusView(BaseView):
    """获取站点的执行状态"""

    def get(self, request):
        """跳转stage_status页面"""
        tip_no = request.GET.get("tip_no")
        mask_name = request.GET.get("mask_name")
        return render(request, 'query_system/stage_status.html', {'tip_no': tip_no, 'mask_name': mask_name})

    @csrf_exempt
    def get_stage_status(self, request):
        """获取站点的执行状态"""
        data_list = list()
        tip_no = request.POST.get("tip_no")
        mask_name = request.POST.get("mask_name")
        device_list = convert_status.objects.filter(tip_no=tip_no, mask_name=mask_name).values('device_name').distinct()
        for device in device_list:
            data = dict()
            col_list = list()
            status_list = list()
            device_name = device['device_name']
            data['device_name'] = device_name
            flow_list = convert_status.objects.filter(tip_no=tip_no, mask_name=mask_name, device_name=device_name)
            for f in flow_list:
                d = dict()
                col_list.append(convert_status_stage.objects.values().get(pk=f.stage_id))
                if f.status == 4 and f.operation_status == 1:
                    d["status"] = 5
                else:
                    d['status'] = f.status
                status_list.append(d)
            data['col_list'] = col_list
            data['status_list'] = status_list
            data_list.append(data)
        return JsonResponse({'data': data_list}, safe=False)


class JDVAccountListView(BaseView):
    """jdv account list"""

    def get(self, request):
        tip_no = request.GET.get("tip_no")
        return render(request, 'query_system/jdv_data_account_list.html', {'tip_no': tip_no})

    def post(self, request):
        """获取jdv account数据"""
        tip_no = request.POST.get("tip_no")
        j_d_list = jdv_data.objects.filter(tip_no=tip_no).values()
        for j_d in j_d_list:
            chips = list()
            layers = list()
            chip_list = jdv_data_device.objects.filter(jdv_data_id=j_d["id"])
            layer_list = jdv_data_layer.objects.filter(jdv_data_id=j_d["id"])
            for chip in chip_list:
                chips.append(chip.device)
            for layer in layer_list:
                layers.append(layer.mask_name)
            j_d["chips"] = ','.join(chips)
            j_d["layers"] = ','.join(layers)
        return JsonResponse({"success": True, "data": list(j_d_list)})


class JDVAccountAddView(BaseView):

    def get(self, request):
        """跳转jdv页面"""
        chip_list = []
        layer_list = []
        tip_no = request.GET.get("tip_no")
        chips = convert_status.objects.filter(tip_no=tip_no).values("device_name").distinct()
        layers = convert_status.objects.filter(tip_no=tip_no).values("mask_name").distinct()
        chip_id = 2
        layer_id = 2
        for chip in chips:
            chip['id'] = chip_id
            chip['title'] = chip['device_name']
            chip_list.append(chip)
            chip_id = chip_id + 1
        for layer in layers:
            layer['id'] = layer_id
            layer['title'] = layer['mask_name']
            layer_list.append(layer)
            layer_id = layer_id + 1
        return render(request, "query_system/jdv_account_add_form.html",
                      {"chips": json.dumps(chip_list), "tip_no": tip_no,
                       "layers": json.dumps(list(layer_list))})

    def post(self, request):
        """提交jdv form表单数据"""
        tip_no = request.POST.get("tip_no")
        jdv_account_id = request.POST.get("jdv_account")
        if jdv_account_id == "":
            return JsonResponse({"success": False, "msg": "Please Chose A JDV Account"})
        sgd_account = sgd_user.objects.get(id=jdv_account_id)
        if not sgd_account:
            return JsonResponse({"success": False, "msg": "Invalid JDV Account"})
        # start_date = request.POST.get("start_date")
        # end_date = request.POST.get("end_date")
        job_deck_name = request.POST.get("job_deck_name")  # 多选
        chips = request.POST.getlist("chips")
        layers = request.POST.getlist("layers")
        p_i = product_info.objects.get(tip_no=tip_no)
        with transaction.atomic():
            j_d = jdv_data.objects.create(tip_no=tip_no, product_name=p_i.product, customer_code=p_i.customer,
                                          jdv_account=jdv_account_id, sgd_user_name=sgd_account.user_name,
                                          sgd_password=sgd_account.user_pwd, start_date=sgd_account.create_date,
                                          end_date=sgd_account.extension_expire_date, job_deck_name=job_deck_name)
            jdv_data_id = j_d.id
            chip_list = list()
            layer_list = list()
            for chip in chips:
                j_d_c = jdv_data_device()
                j_d_c.jdv_data_id = jdv_data_id
                j_d_c.device = chip
                j_d_c.create_date = getDateStr()
                chip_list.append(j_d_c)
            jdv_data_device.objects.bulk_create(chip_list)

            for layer in layers:
                j_d_l = jdv_data_layer()
                j_d_l.jdv_data_id = jdv_data_id
                j_d_l.mask_name = layer
                j_d_l.create_date = getDateStr()
                layer_list.append(j_d_l)
            jdv_data_layer.objects.bulk_create(layer_list)

        return JsonResponse({'success': True, 'msg': 'create success'})


@csrf_exempt
def jdv_data_del(request):
    """删除jdv_data"""
    jdv_data_id = request.POST.get("jdv_data_id")
    with transaction.atomic():
        jdv_data.objects.get(id=jdv_data_id).delete()
        jdv_data_layer.objects.filter(jdv_data_id=jdv_data_id).delete()
        jdv_data_device.objects.filter(jdv_data_id=jdv_data_id).delete()
    return JsonResponse({"success": True, "msg": "del success"})


class JdvDataUploadListView(BaseView):
    """jdv数据上传view"""

    def get(self, request):
        """跳转页面"""
        tip_no = request.GET.get("tip_no")
        mask_name = request.GET.get("mask_name")
        return render(request, 'query_system/jdv_data_upload_list.html', {'tip_no': tip_no, 'mask_name': mask_name})

    def post(self, request):
        """获取列表数据"""
        tip_no = request.POST.get("tip_no")
        mask_name = request.POST.get("mask_name")
        c_f_list = convert_status.objects.values('tip_no', 'mask_name').distinct().filter(
            tip_no=tip_no, mask_name=mask_name)
        for c_f in c_f_list:
            c_f['product_name'] = c_f['mask_name'].split('-')[0]
            c_f['lot_id'] = lot_info.objects.get(mask_name=c_f['mask_name']).lot_id
        total = c_f_list.count()
        return JsonResponse({'total': total, 'rows': list(c_f_list)})


class JDVDataListView(BaseView):
    """jdv data list """

    def get(self, request):
        tip_no = request.GET.get("tip_no")
        mask_name = request.GET.get("mask_name")
        return render(request, 'query_system/jdv_data_list.html', {'tip_no': tip_no, 'mask_name': mask_name})

    def post(self, request):
        super().post(request)
        j_d_list = list()
        tip_no = request.POST.get("tip_no")
        mask_name = request.POST.get("mask_name")
        _j_d_list = jdv_data.objects.values().filter(tip_no=tip_no)
        for j_d in _j_d_list:
            flag = jdv_data_layer.objects.filter(jdv_data_id=j_d['id'], mask_name=mask_name).count()
            if flag > 0:
                j_d['mask_name'] = mask_name
                j_d_list.append(j_d)
        l = j_d_list[self.startIndex: self.endIndex]
        total = len(j_d_list)
        return JsonResponse({'total': total, 'rows': list(l)}, safe=False)

    def to_released_page(self, request):
        tip_no = request.GET.get("tip_no")
        mask_name = request.GET.get("mask_name")
        return render(request, 'query_system/released_jdv_data_list.html', {'tip_no': tip_no, 'mask_name': mask_name})

    @csrf_exempt
    def hold(self, request):
        """hold 操作"""
        id = request.POST.get("id")
        j_d = jdv_data.objects.get(pk=id)
        if j_d and j_d.hold_status == 0:
            j_d.hold_status = 1
            j_d.save()
            layer_list = jdv_data_layer.objects.filter(jdv_data_id=id, is_upload=1)
            chip_list = jdv_data_device.objects.filter(jdv_data_id=id, is_upload=1)
            layers = [layer.mask_name for layer in layer_list]
            chips = [chip.chip for chip in chip_list]
            convert_status.objects.filter(tip_no=j_d.tip_no, mask_name__in=layers,
                                          device_name__in=chips).update(status=4)
        return JsonResponse({"success": True, 'msg': 'hold success'})


class JdvDataUploadFormView(BaseView):
    """jdv data form"""

    def get(self, request):
        """跳转form页面"""
        chip_list = []
        layer_list = []
        jdv_data_id = request.GET.get("jdv_data_id")
        j_d = jdv_data.objects.get(pk=jdv_data_id)
        chips = jdv_data_device.objects.values().filter(jdv_data_id=jdv_data_id)
        layers = jdv_data_layer.objects.values().filter(jdv_data_id=jdv_data_id)
        chip_id = 2
        layer_id = 2
        for chip in chips:
            chip['id'] = chip_id
            chip['title'] = chip['device']
            chip['checked'] = True
            chip_list.append(chip)
            chip_id = chip_id + 1
        for layer in layers:
            layer['id'] = layer_id
            layer['title'] = layer['mask_name']
            layer['checked'] = True
            layer_list.append(layer)
            layer_id = layer_id + 1
        return render(request, 'query_system/jdv_data_upload_form.html', {'jdv_data': j_d,
                                                                          'chips': json.dumps(chip_list),
                                                                          'layers': json.dumps(layer_list)})

    def post(self, request):
        """执行新增jdv account的操作 【生成sgd user、上传jdv文件到sgd server、发送email给客户】"""
        jdv_data_id = request.POST.get("jdv_data_id")
        layers = request.POST.getlist("layers")  # mask_name 集合
        chips = request.POST.getlist("chips")  # device_name 集合
        with transaction.atomic():
            for layer in layers:
                jdv_data_layer.objects.filter(jdv_data_id=jdv_data_id, mask_name=layer).update(is_upload=1,
                                                                                               upload_date=getDateStr())
            for chip in chips:
                jdv_data_device.objects.filter(jdv_data_id=jdv_data_id, device=chip).update(is_upload=1,
                                                                                            upload_date=getDateStr())
            j_d = jdv_data.objects.get(pk=jdv_data_id)
            # user_id = j_d.user_id
            # 上传文件到sgd server
            product_path = os.path.join(Constant.DEVICE_INFO_FILE_BASE_PATH, j_d.product_name)
            jdv_path = os.path.join(product_path, "JDV")
            upload_flag, upload_message = upload_jdv_file(jdv_data_id, jdv_path, j_d.job_deck_name)
            print("upload_flag=" + str(upload_flag))
            print("upload_message=" + upload_message)
            # 发送email文件给客户
            if upload_flag:
                email_flag, email_message = send_mail(jdv_data_id)
                print("email_flag=" + str(email_flag))
                print("email_message=" + email_message)
                if email_flag:
                    # 更新jdv_data
                    j_d.send_email_date = getDateStr()
                    j_d.send_email_status = 1
                    j_d.save()
                    # 更新convert_flow中的jdv状态
                    convert_status.objects.filter(tip_no=j_d.tip_no, mask_name__in=layers,
                                                  device_name__in=chips).update(jdv_status=1)
                    return JsonResponse({"success": False, "msg": "Upload Success"})
                else:
                    return JsonResponse({"success": False, "msg": "Email Error"})
            else:
                return JsonResponse({"success": True, "msg": "Upload Error"})


class JDVDataReleaseFormView(BaseView):
    """jdv data release方法"""

    def get(self, request):
        """跳转jdv_data_release页面"""
        layer_list = []
        jdv_data_id = request.GET.get("jdv_data_id")
        j_d = jdv_data.objects.get(pk=jdv_data_id)
        layers = jdv_data_layer.objects.values().filter(jdv_data_id=jdv_data_id, is_upload=1)
        layer_id = 2
        for layer in layers:
            layer['id'] = layer_id
            layer['title'] = layer['mask_name']
            layer['checked'] = True
            layer_list.append(layer)
            layer_id = layer_id + 1
        return render(request, 'query_system/jdv_data_release_form.html', {'jdv_data': j_d,
                                                                           'layers': json.dumps(layer_list)})

    def post(self, request):
        """进行release操作"""
        jdv_data_id = request.POST.get("jdv_data_id")
        layers = request.POST.getlist("layers")
        note = request.POST.get("note")
        user_id = request.session.get(Constant.SESSION_CURRENT_USER_ID)
        user_name = request.session.get(Constant.SESSION_CURRENT_USER_LOGINNAME)
        with transaction.atomic():
            j_d = jdv_data.objects.get(pk=jdv_data_id)
            j_d.release_status = 1
            j_d.customer_release_date = getDateStr()
            j_d.dp_release_date = getDateStr()
            j_d.dp_release_user = user_name
            j_d.note = note
            j_d.save()
            jdv_data_layer.objects.filter(jdv_data_id=jdv_data_id,
                                          mask_name__in=layers).update(is_release=1, release_date=getDateStr(),
                                                                       release_user_id=user_id,
                                                                       release_user_name=user_name)
            j_d_c_list = jdv_data_device.objects.filter(jdv_data_id=jdv_data_id, is_upload=1)
            chips = list()
            for j_d_c in j_d_c_list:
                chips.append(j_d_c.chip)
            convert_status.objects.filter(tip_no=j_d.tip_no,
                                          mask_name__in=layers,
                                          device_name__in=chips).update(jdv_status=3)
        return JsonResponse({"success": True, "msg": "Release Success"})


@csrf_exempt
def get_jb_file_list(request):
    """获取jb文件列表"""
    tip_no = request.POST.get("tip_no")
    p = product_info.objects.get(tip_no=tip_no, is_delete=0)
    if not p:
        return JsonResponse({"success": False, "message": "tip_no err"})
    product_path = os.path.join(Constant.DEVICE_INFO_FILE_BASE_PATH, p.product)
    path = os.path.join(product_path, "JDV")
    file_list = os.listdir(path)
    jb_list = [x for x in file_list if os.path.splitext(x)[1] == '.jb']  # 获取后缀名为jb的文件列表
    return JsonResponse({"success": True, "data": jb_list})


@csrf_exempt
def sgd_account_options(request):
    """获取sgd账号选项"""
    tip_no = request.POST.get("tip_no")
    account_list = sgd_user.objects.filter(tip_no=tip_no, is_delete=0, is_lock=0).values()
    return JsonResponse({'success': True, "data": list(account_list)})