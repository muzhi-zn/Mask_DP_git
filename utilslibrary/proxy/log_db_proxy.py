# coding:utf-8
"""代理反射机制,将数据库的增加删改查记录到数据库
 

"""
from django.core import serializers
from utilslibrary.middleware.global_request_middleware import GlobalRequestMiddleware
import sys

from types import MethodType
from utilslibrary.system_constant import Constant
import json
from utilslibrary.utils.date_utils import getDateStr, getMilliSecond
from system.models import log
from utilslibrary.utils.common_utils import getCurrentSessionName, getCurrentSessionID
from utilslibrary.utils.common_utils import get_ip


# ProxyFactory  传入hcls（被装饰类的处理器类型）作为init的参数， 传入 cls（被装饰类的类型）作为call的参数
class ProxyFactory:
    def __init__(self, hcls):
        print('ProxyFacotry __init__', hcls)
        if issubclass(hcls, InvocationHandler) or hcls is InvocationHandler:
            self.hcls = hcls
        else:
            raise HandlerException(hcls)

    def __call__(self, cls):
        print('ProxyFacotry __call__', cls)
        return Proxy(cls, self.hcls)


# Proxy  传入cls（被装饰类的类型）、hcls（被装饰类的处理器类型）作为init的参数
class Proxy:

    def __init__(self, cls, hcls):
        print('Proxy __init__')
        self.cls = cls
        self.hcls = hcls
        self.handlers = dict()

    def __call__(self, *args, **kwargs):
        print('Proxy __call__', args, kwargs)
        self.obj = self.cls(*args, **kwargs)

        return self

    def __getattr__(self, attr):
        sys.setrecursionlimit(10000)
        print('Proxy get attr', attr)

        isExist = hasattr(self.obj, attr)
        res = None
        if isExist:
            res = getattr(self.obj, attr)
            if isinstance(res, MethodType):
                if self.handlers.get(res) is None:
                    self.handlers[res] = self.hcls(self.obj, res, attr)
                return self.handlers[res]
            else:
                return res
        return res


# InvocationHandler 传入func（被装饰类的实例方法）作为init的参数
class InvocationHandler:
    def __init__(self, obj, func, attr):
        print('InvocationHandler __init__', obj, func, attr)
        self.attr = attr
        self.obj = obj
        self.func = func

    def __call__(self, *args, **kwargs):
        '''
        print('InvocationHandler __call__:',self.func, args, kwargs)
        print('InvocationHandler __call__:',self.func)
        print('InvocationHandler __call__:',self.attr)
        print('InvocationHandler __call__:', args, kwargs)
        print('object:',args[0])
        '''
        if self.attr and len(self.attr) > 4:
            pre_str = self.attr[:4]
            if pre_str in Constant.LOG_DB_OPERATIONS_METHOD:
                from django_middleware_global_request.middleware import get_request
                print("log_db_proxy_print_start")
                # request2 = request = get_request()
                # u_id = getCurrentSessionID(request2)
                # u_name = getCurrentSessionName(request2)
                request = request = get_request()
                # request=args[0]
                # request = GlobalRequestMiddleware.getRequest()
                u_id = getCurrentSessionID(request)
                u_name = getCurrentSessionName(request)
                print("u_id =", u_id)
                print("u_name =", u_name)
                print("log_db_proxy_print_end")
                data = json.dumps(args[0], default=args[0].conver_to_dict)
                # log into db
                log_o = log()
                log_o.ip = get_ip(request)
                log_o.obj = args[0]
                log_o.data_id = args[0].id
                log_o.user_id = u_id
                log_o.user_name = u_name
                log_o.action = self.attr
                log_o.json = data
                log_o.create_date = getDateStr()
                log_o.create_time = getMilliSecond()
                if pre_str == 'add_':
                    args[0].create_date = getDateStr()
                    args[0].create_time = getMilliSecond()
                    args[0].create_by = u_id
                elif pre_str == 'upd_':
                    args[0].update_date = getDateStr()
                    args[0].update_time = getMilliSecond()
                    args[0].update_by = u_id
                log_o.save()

                print('{} insert into db:{}'.format(u_name, data))
        return self.func(*args, **kwargs)


class HandlerException(Exception):
    def __init__(self, cls):
        super(HandlerException, self).__init__(cls, 'is not a hanlder class')


@ProxyFactory(InvocationHandler)
class Sample:
    def __init__(self, age):
        print('Sample __init__')
        self.age = age

    def foo(self):
        print('Sample foo()', self.age)

    def add(self, x, y):
        print('Sample add()')
        return x + y


if __name__ == '__main__':
    s = Sample(12)
    print('main types=', type(s))
    s.foo()
    s.add(1, 2)
    s.add(2, 4)
    print(s.age)
