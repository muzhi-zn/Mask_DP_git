import inspect, re
from utilslibrary.system_constant import Constant


#trans var to str
def varname(p):
    for line in inspect.getframeinfo(inspect.currentframe().f_back)[3]:
        m = re.search(r'\bvarname\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)', line)
    if m:
        return m.group(1)

#get user id in session
def getCurrentSessionID(request):
    try:
        return request.session[Constant.SESSION_CURRENT_USER_ID]
    except Exception as e:
        return ''
    #get user name in session
def getCurrentSessionName(request):
    return request.session[Constant.SESSION_CURRENT_USER_LOGINNAME]

def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:

        ip = x_forwarded_for.split(',')[0]  # 所以这里是真实的ip

    else:

        ip = request.META.get('REMOTE_ADDR')  # 这里获得代理ip
    return ip
