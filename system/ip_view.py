# from utilslibrary.base.base import BaseView
# from django.shortcuts import render
# from django.db.models import Q
# from system.models import log
# from django.http.response import JsonResponse
# from system.service.ip_service import IPService
# import datetime
#
# class IPList(BaseView):
#     def get(self,request):
#         # ip = request.GET.get('ip')
#         # print('ip:',ip)
#         id = request.POST.get('id')
#         q = Q()
#         q.children.append(('id',id))
#         print('startIndex{} endIndex{}'.format(self.startIndex,self.endIndex))
#         ip_list = ip_authorize_info.objects.filter().values()
#         # print('iplist:',ip_list)
#         return render(request, 'system_ip_list.html', {"ip_authorize_info":ip_list})
#
#     def post(self,request):
#         super().post(request)
#         ip = request.POST.get('ip','')
#         print('ip:',ip)
#         time = request.POST.get('time','')
#         ip_type = request.POST.get('ip_type','')
#         # print('iptype:',ip_type)
#         q = Q()
#         q.connector = 'and'
#         # q.children.append(('',))
#         if ip:
#             q.children.append(('ip__contains',ip))
#         if ip_type:
#             q.children.append(('ip_type__contains',ip_type))
#
#         print('post start')
#         print('startIndex{} endIndex{}'.format(self.startIndex, self.endIndex))
#
#         ip_list = ip_authorize_info.objects.filter(q).order_by('-id')[self.startIndex:self.endIndex].values()
#         # print(ip_list)
#         new_ip_list = log.objects.values('ip').distinct()
#         old_ip_list = ip_authorize_info.objects.values('ip')
#         for ip in new_ip_list:
#             print("开始查询：",ip)
#             nip = ip
#             for ip in old_ip_list:
#                 oip = ip
#                 if oip == nip:
#                     print("已经存在此IP")
#                     mark = 1
#                     break
#                 else:
#                     print("正在查询此IP")
#                     mark = 0
#             if mark == 1:
#                 continue
#             else:
#                 print("此IP为新IP：",nip)
#                 _o = ip_authorize_info()
#                 _o.ip = nip['ip']
#                 datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#                 _o.time = datetime.datetime.now()
#                 _o.type = 0
#                 _s = IPService()
#                 _s.addIP(_o)
#
#
#
#
#         data = {}
#         data["total"] = ip_authorize_info.objects.filter().count()
#         data["rows"] = list(ip_list)
#         # print(data['rows'])
#
#         return JsonResponse(data,safe=False)
#
# class IPForm(BaseView):
#     def get(self,request):
#         id = request.GET.get("id")
#         if not id:
#             return render(request, 'system_ip_form.html')
#         else:
#             _o =ip_authorize_info.objects.get(id = id)
#             dict_list = []
#             if _o and _o.parent_id > 0:
#                 dict_list = eval(_o.validate_value)
#                 dict_list = eval(dict_list)
#             return  render(request, 'system_ip_form.html', {"ip_authorize_info" : _o, "dict_list" : dict_list})
#
# class AddIP(BaseView):
#     def get(self,request):
#         _o = ip_authorize_info()
#         return render(request, 'system_ip_form.html', {"method": "add", "ip_o":_o})
#     def post(self,request):
#         data = {}
#         id = request.POST.get('id')
#         ip = request.POST.get('ip','')
#         ip_type = request.POST.get('ip_type','')
#         time = request.POST.get('time','')
#         if ip == '' or ip_type == '':
#             data["success"]=False
#             data["msg"]="Input Data Error!"
#             return JsonResponse(data,safe=False)
#
#         _o = ip_authorize_info.objects.filter(ip = ip)
#         if _o:
#             data["success"] = False
#             data["msg"] = "login name exists!"
#             return JsonResponse(data,self = False)
#         _o = ip_authorize_info()
#         _o.ip = ip
#         _o.ip_type = ip_type
#         _o.time = time
#         _s = IPService()
#         return  _s.addIP(_o)
#
#
# class IPEdit(BaseView):
#     def get(self,request):
#         id = request.GET.get("id")
#         if not id:
#             return render(request, 'system_ip_form.html', {"method": "edit"})
#         else:
#             _o = ip_authorize_info.objects.get(id = id)
#             return render(request, 'system_ip_form.html', {"ip_o":_o, "method": "edit"})
#
#     def post(self,request):
#         data = {}
#         id = request.POST.get('id')
#         ip = request.POST.get('ip')
#         time = request.POST.get('time')
#         ip_type = request.POST.get('ip_type')
#
#         if ip == '' or ip_type == '' or time =='':
#             data["success"] = False
#             data["msg"] = "Input Data Error!"
#             return JsonResponse(data,safe = False)
#         if id :
#             _o = ip_authorize_info.objects.get(id = id)
#             _o.ip = ip
#             _o.id = id
#             _o.time = time
#             _o.ip_type = ip_type
#
#             _s = IPService()
#             return _s.updateIP(_o)
#         else:
#             data["success"] = False
#             data["msg"] = "id Error"
#             return  JsonResponse(data,safe = False)
# class IPDel(BaseView):
#     def get(self,request):
#         data = {}
#         ids = request.GET.get('ids')
#         data["success"] = True
#         data["msg"] = "success"
#         _o = ip_authorize_info
#         _o.id = ids
#         _s = IPService()
#
#         return _s.delIP(_o)
#
