# coding:utf-8
'''
Created on 2019-12-27

@author: Ligo
'''

""" base class for db Model
"""
from django.db import models

class BaseModel(models.Model):
    #create date,example:2019-12-03
    create_date = models.CharField(max_length=45,null=True,default="")
    #create time millisecond,example:217773273243
    create_time = models.IntegerField(null=True,default=0)
    #update time millisecond,example:217773273243
    update_time = models.IntegerField(null=True,default=0)
    #update date,example:2019-12-03
    update_date = models.CharField(max_length=45,null=True,default="")
    #is delete flag,0:not delete 1:delete
    is_delete = models.IntegerField(default=0)
    #create user
    create_by = models.CharField(max_length=256,null=True,default="")
    #update user
    update_by = models.CharField(max_length=256,null=True,default="")
    
    class Meta:
        abstract = True
    #-------------------------------------------
    #convert to dict,you can convert object to json use:  json.dumps(subclass_object, default=subclass_object.conver_to_dict)
    #-------------------------------------------    
    def conver_to_dict(self,obj):
        d = {}
        d.update(obj.__dict__)
        return d
    
    
from django.views.generic import View

class BaseView(View):
    
    class Meta:
        abstract = True
    pageNo = 0
    pageSize = 0
    startIndex = 0
    endIndex = 0
    
    def post(self,request):
        self.pageNo = int(request.POST.get('pageNo'))
        print('BaseView ------post(){}'.format(self.pageNo))  
        self.pageSize = int(request.POST.get('pageSize'))
        print('BaseView ------post() pageSize{}'.format(self.pageSize))  
        
        self.startIndex = 0
        self.endIndex = self.startIndex + self.pageSize
        if self.pageNo > 1:
            self.startIndex = (self.pageNo - 1) * self.pageSize
            self.endIndex = self.startIndex + self.pageSize  
        print('BaseView startIndex{} endIndex{}'.format(self.startIndex,self.endIndex))
        
    
class BaseService(object):
    
    
    class Meta:
        abstract = True    