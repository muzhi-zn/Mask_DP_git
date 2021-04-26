# coding:utf-8
""" 
tree select model
"""


class TreeInfo(object):
    id = ''
    parent = ''
    name = ''
    text = ''
    type = ''
    state =''
    
    
    
    def conver_to_dict(self,obj):
        d = {}
        d.update(obj.__dict__)
        return d

class State(object):
    opened = True
    selected = False        