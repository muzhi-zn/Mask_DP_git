
import datetime
import time
  
#example:2019-12-03 12:23:05
def getDateStr():
    c_date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return c_date
    
def getMilliSecond():
    return int(time.time())

def getDateConStr():
    c_date=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return c_date


def getMESDateStr():
    c_date = datetime.datetime.now().strftime('%Y-%m-%d-%H.%M.%S.%f')
    return c_date


print(getMESDateStr())