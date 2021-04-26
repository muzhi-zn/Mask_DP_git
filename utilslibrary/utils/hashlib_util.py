# code = utf-8
'''
@Author:Ligo
@date:2020/4/9 9:22
@File:hashlib_util.py.py
@Project:IEMS
desc:
'''
import hashlib

def get_sha256(str):
    if not str or str=='':
        return ''
    # 1.创建一个hash对象
    h = hashlib.sha256()
    # 2.填充要加密的数据
    h.update(bytes(str, encoding='utf-8'))
    # 3.获取加密结果
    pawd_result = h.hexdigest()
    print(pawd_result)
    return pawd_result