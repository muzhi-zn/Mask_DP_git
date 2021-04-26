from django.utils.deprecation import MiddlewareMixin
'''system Exception middleware
'''

import logging
import traceback
from django.http.response import JsonResponse
from django.shortcuts import render
logger = logging.getLogger('log')

class BaseResp:  # 基础的返回值类
        def __init__(self, code, msg, data):
                self.code = code
                self.msg = msg
                self.data = data if data else dict()

def json_resp(code=0, msg="成功", data=None):
    return JsonResponse(BaseResp(code, msg, data).__dict__)
    
class ExceptionMiddleWare(MiddlewareMixin):
    
    def process_exception(self,request,exception):
        print('-----------------------------------------');
        print(exception)
        print(traceback.format_exc())
        print('-----------------------------------------');
        logger.error(traceback.format_exc())
        #return json_resp(-13, "访问视图失败, 未知错误, 请联系管理员")
        return render(request,'500.html',{'error_des':exception})
        