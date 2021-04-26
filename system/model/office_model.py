# coding:utf-8
""" 
tree select model
"""


class OfficeInfo(object):
    id = ''
    parentId = ''
    name = ''
    sort = ''
    type = ''
    code = ''
    state =''
    hasChildren = ''
    useable = ''
    parentIds = ''
    
    
    
    def conver_to_dict(self,obj):
        d = {}
        d.update(obj.__dict__)
        return d

class State(object):
    opened = True        