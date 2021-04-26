import functools
import logging
import traceback

from django.http import JsonResponse

log = logging.getLogger('log')


def catch_exception(func):
    """捕捉方法的异常信息"""

    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            fn = func(request, *args, **kwargs)
            return fn
        except Exception as e:
            log.error(traceback.format_exc())
            log.error(func.__name__ + "方法出现错误，错误信息为： " + str(e))
            return JsonResponse({'success': False, 'msg': 'Server Error, Error Info: ' + str(e)}, safe=False)

    return wrapper
