#--coding:utf-8 --
"""script and file templates manage

"""
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.http.response import  JsonResponse
from django.db.models import F,Q
import json

from utilslibrary.base.base import BaseView
from system.models import template,dict
from system.service.template_service import TemplateService
from utilslibrary.system_constant import Constant

class TemplateList(BaseView):
    
    def get(self,request):
        return render(request,"system_template_list.html")
    
    def post(self,request):
         #-----------------------------
        #需要获得翻页参数时添加
        #代码中使用self.startIndex和self.endIndex获取相应范围的记录
        #------------------------------
        super().post(request)
        
        #接收查询参数---与页面上要查询的条件匹配
        template_type = request.POST.get('template_type','')
        file_name = request.POST.get('file_name','')
        """query by where1"""
        #添加查询条件，设置为逻辑与查询
        q = Q()
        q.connector = 'and '
        q.children.append(('is_delete',0))
        if template_type:
            q.children.append(('template_type',template_type))
        if file_name:
            
            q.children.append(('file_name__contains',file_name))   
        #执行查询
        o_list = template.objects.filter(q).order_by('-id')[self.startIndex:self.endIndex].values()     
        
        
        #组装JSON数据
        data = {}
        #设置总记录数
        data["total"] = template.objects.filter(q).count()
        data["rows"] = list(o_list)
        print(data)
        
        return JsonResponse(data,safe=False)

        
        
class TemplateAdd(BaseView):
    
    def get(self,request):
        #query dictionary info tree
        _o_p_list = dict.objects.filter(type=Constant.INFO_TREE_DICT_TYPE_NAME)
        if _o_p_list.count()>0:
            _o = _o_p_list[0]
            _infotree_list = dict.objects.filter(parent_id=_o.id)
        #query dictionary floor plan
        _o_p_list = dict.objects.filter(type=Constant.FLOOR_PLAN_DICT_TYPE_NAME)
        if _o_p_list.count()>0:
            _o = _o_p_list[0]
            _floorplan_list = dict.objects.filter(parent_id=_o.id)

        _o_p_list = dict.objects.filter(type=Constant.SCRIPT_TEMPLATE_FILE_DICT_TYPE)
        if _o_p_list.count() > 0:
            _o = _o_p_list[0]
            _template_list = dict.objects.filter(parent_id=_o.id)
        _o = template()
        return render(request,"system_template_edit.html",{"method":"add","info_tree":_infotree_list,"floor_plan":_floorplan_list,"template_list":_template_list,"template":_o})
    
    def post(self,request):
        templateType = request.POST.get("templateType")
        dictType = request.POST.get("dictType")

        templateName = request.POST.get("templateName")
        fileName = request.POST.get("fileName")
        fileExtension = request.POST.get("fileExtension")
        templateJson = request.POST.get("templateJson")
        #package template text
        template_text = ''
        row_dict = json.loads(templateJson)
        for item in row_dict:
            template_text = template_text+'\n'+item['value']

        _o = template()
        _o.template_type = templateType
        _o.template_name = templateName
        _o.dict_type = dictType

        _o.file_name = fileName
        _o.file_extension = fileExtension
        _o.template_json = templateJson
        _o.template_text = template_text
        _s = TemplateService()
        return _s.add_template(_o)

class TemplateView(BaseView):
    
    def get(self,request):

        # query dictionary info tree
        _o_p_list = dict.objects.filter(type=Constant.INFO_TREE_DICT_TYPE_NAME)
        if _o_p_list.count() > 0:
            _o = _o_p_list[0]
            _infotree_list = dict.objects.filter(parent_id=_o.id)
        # query dictionary floor plan
        _o_p_list = dict.objects.filter(type=Constant.FLOOR_PLAN_DICT_TYPE_NAME)
        if _o_p_list.count() > 0:
            _o = _o_p_list[0]
            _floorplan_list = dict.objects.filter(parent_id=_o.id)

        _o_p_list = dict.objects.filter(type=Constant.SCRIPT_TEMPLATE_FILE_DICT_TYPE)
        if _o_p_list.count() > 0:
            _o = _o_p_list[0]
            _template_list = dict.objects.filter(parent_id=_o.id)
        id = request.GET.get("id")
        _o = template.objects.get(id=id)
        row_dict = json.loads(_o.template_json)

        return render(request,"system_template_edit.html",{"template":_o,"row_dict":row_dict,"info_tree":_infotree_list,"floor_plan":_floorplan_list,"template_list":_template_list})
        

class TemplateEdit(BaseView):
    
    def get(self,request):
        
        
        #query dictionary info tree
        _o_p_list = dict.objects.filter(type=Constant.INFO_TREE_DICT_TYPE_NAME)
        if _o_p_list.count()>0:
            _o = _o_p_list[0]
            _infotree_list = dict.objects.filter(parent_id=_o.id)
        #query dictionary floor plan
        _o_p_list = dict.objects.filter(type=Constant.FLOOR_PLAN_DICT_TYPE_NAME)
        if _o_p_list.count()>0:
            _o = _o_p_list[0]
            _floorplan_list = dict.objects.filter(parent_id=_o.id)

        _o_p_list = dict.objects.filter(type=Constant.SCRIPT_TEMPLATE_FILE_DICT_TYPE)
        if _o_p_list.count() > 0:
            _o = _o_p_list[0]
            _template_list = dict.objects.filter(parent_id=_o.id)

        id = request.GET.get("id")
        _o = template.objects.get(id=id)
        row_dict = json.loads(_o.template_json)

        _o_dict = dict.objects.get(type=_o.dict_type)
        # 执行查询
        _dict_list = dict.objects.filter(parent_id=_o_dict.id).order_by('-id').values()



        return render(request,"system_template_edit.html",{"method":"edit","template":_o,"row_dict":row_dict,"info_tree":_infotree_list,"floor_plan":_floorplan_list,"template_list":_template_list,"dict_list":_dict_list})
    def post(self,request):
        id = request.POST.get("id")
        templateType = request.POST.get("templateType")
        dictType = request.POST.get("dictType")

        templateName = request.POST.get("templateName")
        fileName = request.POST.get("fileName")
        fileExtension = request.POST.get("fileExtension")
        templateJson = request.POST.get("templateJson")
        # package template text
        template_text = ''
        row_dict = json.loads(templateJson)
        for item in row_dict:
            template_text = template_text+'\n'+item['value']

        _o = template()
        _o.id = id
        _o.template_type = templateType
        _o.dict_type = dictType
        _o.template_name = templateName
        _o.file_name = fileName
        _o.file_extension = fileExtension
        _o.template_json = templateJson
        _o.template_text = template_text
        print(len(template_text))
        _s = TemplateService()
        return _s.upd_template(_o)

class TemplateDel(BaseView):
    
    def get(self,request):
        ids = request.GET.get("ids")
        _o = template()
        _o.id = ids
        _s = TemplateService()
        return _s.del_template(_o)
        

class TemplateRowEdit(BaseView):
    
    def get(self,request):
        return render(request,"system_template_row_edit.html")

def script_template_list_api(request):
     
    return HttpResponse("""{"total":20,"rows":[{"id":"6566203f8de347958b2c2de384818eb2",
    "createDate":"2019-12-13 18:00:08","updateDate":"2019-12-20 10:15:29","template_name":
    "Frame Fracture","type":"VSB12i","genIdType":"2"},{"id":"80e9e2e8da67497992a849c85cef129b","createDate":"2019-12-13 18:00:08","updateDate":"2019-12-13 18:00:08","template_name":"Device Fracture","type":"VSB12i"},{"id":"c3a5e6da7d314cf391e6e41c8a797512","createDate":"2019-12-13 18:00:08","updateDate":"2019-12-13 18:00:08","template_name":"Frame Fracture","type":"VSB12"},{"id":"905fdc773219485ea6c6c22ccad4f172","createDate":"2019-12-13 18:00:08","updateDate":"2019-12-13 18:00:08","template_name":"layout.ini","type":"VSB12i"},{"id":"b899fb3539034c27af58d9076ddd60d2","createDate":"2019-12-23 15:43:02","updateDate":"2019-12-23 15:43:02","template_name":"Layout.ini","type":"Mode5"},{"id":"fd40ef4f092f41a19c32cafabad017ff","createDate":"2019-12-13 18:00:08","updateDate":"2019-12-13 18:00:08","template_name":"Chip.ini","type":"VSB12i"},{"id":"58c1558ade774e66802da90c3178a297","createDate":"2019-12-13 18:00:08","updateDate":"2019-12-13 18:00:08","template_name":"Aux.xml","type":"VSB12i"},{"id":"3c98bea023e44dd5b63fcb1b6c40f20e","createDate":"2019-12-13 18:00:08","updateDate":"2019-12-13 18:00:08","template_name":"OD.aw.xml","type":"VSB12i"},{"id":"4519a82f2c614560a193e5fe6ec1ad04","createDate":"2019-12-13 18:00:08","updateDate":"2019-12-13 18:00:08","template_name":"Layout.mds","type":"VSB12"},{"id":"7368f5d3b0be45df8302fecb2558771f","createDate":"2019-12-13 18:00:08","updateDate":"2019-12-13 18:00:08","template_name":"layout.mds","type":"VSB12i"}]}""")