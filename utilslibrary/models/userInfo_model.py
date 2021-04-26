# coding:utf-8
""" 
存放当前用户信息的模型
"""


class UserInfo(object):
    Id =''
    LoginName=''
    RealName=''
    IsAdmin=0
    Icon=''
    
    
    
    def conver_to_dict(self,obj):
        d = {}
        d.update(obj.__dict__)
        return d
        