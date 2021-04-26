# -*- coding: utf-8 -*-
"""Decorators
check login and auth        
"""
from django.views.generic import View
from utilslibrary.system_constant import Constant
from django.http.response import HttpResponseRedirect

class AuthCheck(View):
    def __init__(self,func):
        self.f=func 
        
    def __call__(self,*args,**kw):
        user_json=args[0].session.get(Constant.SESSION_CURRENT_USER)
        if user_json:
            return self.f(*args,**kw)
        else:
            return HttpResponseRedirect('/system/login')     