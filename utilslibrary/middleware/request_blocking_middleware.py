import time
from django.utils.deprecation import MiddlewareMixin
import logging
from django.conf import  settings
from utilslibrary.utils.common_utils import get_ip

logger = logging.getLogger('log')

#检查访问频率，每10秒可访问15次
class RequestBlockingMiddleware(MiddlewareMixin):
    white_list = ['/tooling/state/', '/tooling/files/upload/', '/tooling/file/check/']

    def process_request(self,request):
        if request.path in self.white_list:
            return None
        now=time.time()
        request_queue = request.session.get('request_queue',[])
        if len(request_queue) < settings.MAX_REQUEST_PER_SECOND:
            request_queue.append(now)
            request.session['request_queue']=request_queue
        else:
            time0=request_queue[0]
            ip = get_ip(request)
            if (now-time0)<10:
                logger.warning('too fast!!!!!!!!!!!!!!!'+ip)
                print('-----------------------------------------')
                print(str(time0)+'----'+str(now))
                print('too fast!!!!!!!!!!!!!!!'+ip)
                print('-----------------------------------------')

                time.sleep(5)
            request_queue.append(time.time())
            request.session['request_queue']=request_queue[14:]
