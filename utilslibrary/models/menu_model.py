# coding:utf-8
""" 
tree select model
"""


class MenuInfo(object):
    id = ''
    parentIds = ''
    name = ''
    href = ''
    icon = ''
    sort =''
    isShow = ''
    type = ''
    hasChildren = ''
    parentId = ''
    
    
    
    def conver_to_dict(self,obj):
        d = {}
        d.update(obj.__dict__)
        return d

        