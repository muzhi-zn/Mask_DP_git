# code:utf-8
import functools

from utilslibrary.mes_webservice.mes_webservice import mes_op_start, mes_op_comp


def op_start(status):
    """MES某操作开始状态请求"""

    def wrapper(func):
        def in_func(request, *args, **kwargs):
            print("%s op start" % status)
            lot_id = request.POST.get('lot_id')
            start_flag = mes_op_start(lot_id, status)
            print(lot_id + " op start flag = " + str(start_flag))
            return func(request, *args, **kwargs)

        return in_func

    return wrapper


def op_end(status):
    """MES某操作结束状态请求"""

    def wrapper(func):
        @functools.wraps(func)
        def in_func(request, *args, **kwargs):
            lot_id = request.POST.get('lot_id')
            fn = func(request, *args, **kwargs)
            comp_flag = mes_op_comp(lot_id, status)
            print("%s op end" % status)
            print(lot_id + " op comp flag = " + str(comp_flag))
            return fn

        return in_func

    return wrapper


def op_process(status):
    """完整的op流程，包括op_start和op_end"""

    def wrapper(func):
        @functools.wraps(func)
        def in_func(request, *args, **kwargs):
            print("%s op process start" % status)
            lot_id = request.POST.get('lot_id')
            start_flag = mes_op_start(lot_id, status)
            print(lot_id + " op start flag = " + str(start_flag))
            fn = func(request, *args, **kwargs)
            comp_flag = mes_op_comp(lot_id, status)
            print("%s op process end" % status)
            print(lot_id + " op comp flag = " + str(comp_flag))
            return fn

        return in_func

    return wrapper
