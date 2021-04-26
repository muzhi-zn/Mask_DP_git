import re
import string
import threading
import time
import random
import json
from urllib import request

from django.http import JsonResponse
from django.shortcuts import render
from dwebsocket import accept_websocket, require_websocket

# 存储连接websocket的用户
from dwebsocket.websocket import WebSocket

from system.models import message_log
from utilslibrary.base.base import BaseView
from utilslibrary.utils.common_utils import getCurrentSessionID
from utilslibrary.utils.date_utils import getDateStr

clients = {}


@accept_websocket
def websocket_connect(request):
    """websocket的连接方法"""
    lock = threading.RLock()  # rlock线程锁
    user_id = getCurrentSessionID(request)
    # print("-----" * 5)
    # user_id = request.GET.get('user_id')
    try:
        lock.acquire()  # 抢占资源
        s = {}
        #  因为同一个账号打开多个页面连接信息是不同的
        if clients.get(user_id) is not None:
            # 连接信息  键 连接名  值：连接保存
            s[str(request.websocket)] = request.websocket
            # 已存在的连接信息继续增加
            clients[user_id].update(s)
        else:
            #  连接信息  键 连接名  值：连接保存
            s[str(request.websocket)] = request.websocket
            # 新增 用户  连接信息
            clients[user_id] = s
        # print(clients)
        # 监听接收客户端发送的消息 或者 客户端断开连接
        for message in request.websocket:
            msg_json_list = re.findall(r'(\{.*?\})', str(message))
            if msg_json_list:
                msg_json_str = msg_json_list[0]
                msg_json = json.loads(msg_json_str)
                if msg_json['is_confirm']:
                    message_log.objects.filter(message_id=msg_json['message_id'], status=0).update(status=1,
                                                                                                   confirm_time=
                                                                                                   getDateStr())
    finally:
        # 通过用户名找到 连接信息 再通过 连接信息 k 找到 v (k就是连接信息)
        try:
            clients.get(user_id).pop(str(request.websocket))
        except ConnectionAbortedError as e:
            print(str(e))
        # 释放锁
        lock.release()


# 发送消息
def websocket_msg(client, msg):
    # 因为一个账号会有多个页面打开 所以连接信息需要遍历
    for cli in client:
        b1 = json.dumps(msg).encode('utf-8')
        client[cli].send(b1)


# 服务端发送消息
def send_msg(user_id, msg_json):
    'username:用户名 title：消息标题 data：消息内容，消息内容:ulr'
    try:
        if clients[user_id]:
            websocket_msg(clients[user_id], msg_json)
            # 根据业务需求 可有可无    数据做 持久化
            # messageLog = MessageLog(name=username, msg_title=title, msg=data, msg_url=url, is_required=0)
    except BaseException as e:
        # messageLog = MessageLog(name=username, msg_title=title, msg=data, msg_url=url, is_required=1)
        pass
    finally:
        pass


# 服务端发送跑马灯通知
def send_notice(user_id, notice, notice_type, tag='Notice', is_resend=False):
    'username:用户名 title：消息标题 data：消息内容，消息内容:ulr'
    message_id = time.strftime('%Y%m%d%H%M%S', time.localtime()) + ''.join(random.sample(string.ascii_letters +
                                                                                         string.digits, 6))
    try:
        if clients[user_id]:
            websocket_msg(clients[user_id], {'message_id': message_id, 'is_notice': True, 'tag': tag, 'notice': notice,
                                             'notice_type': notice_type})
            # 根据业务需求数据做持久化
            if not is_resend:
                message_log.objects.create(message_id=message_id, user_id=user_id, message_type=notice_type,
                                           message_tag=
                                           tag, message=notice, send_time=getDateStr())
            return True
    except BaseException as e:
        print(e)
        if not is_resend:
            message_log.objects.create(message_id=message_id, user_id=user_id, message_type=notice_type, message_tag=
            tag, message=notice, send_time=getDateStr(), status=2)
        return False


# message_log
class message_log_list(BaseView):

    def get(self, request):
        if request.method == 'GET':
            print('get')
            return render(request, 'message_log.html')

    def post(self, request):
        """根据查询条件获取 message"""
        if request.method == 'POST':
            super().post(request)
            data = {}
            meg_list = message_log.objects.filter()
            # 多条件查询，层级筛选
            message_id = request.POST.get('message_id')
            user_id = request.POST.get('user_id')
            type = request.POST.get('type')
            status = request.POST.get('status')
            if message_id:
                meg_list = meg_list.filter(message_id=message_id)
            if user_id:
                meg_list = meg_list.filter(user_id=user_id)
            if type:
                meg_list = meg_list.filter(message_type=type)
            if status:
                meg_list = meg_list.filter(status=status)
            print(len(meg_list), meg_list)
            data["total"] = meg_list.count()
            data["rows"] = list(meg_list.values())
            print(data)
            return JsonResponse(data, safe=False)


class message_resend(BaseView):

    def get(self, request):
        data = {}
        ids = request.GET.get("ids")
        for id in ids.split(','):
            m_l = message_log.objects.get(id=id)
            if clients[m_l.user_id]:
                websocket_msg(clients[m_l.user_id],
                              {'message_id': m_l.message_id, 'is_notice': True, 'tag': m_l.message_tag, 'notice':
                                  m_l.message, 'notice_type': m_l.message_type})
                m_l.status = 0
                m_l.send_time = getDateStr()
                m_l.save()
                data["success"] = True
                data["msg"] = "Resend Success"
            else:
                data["success"] = False
                data["msg"] = "Resend Failed"
        return JsonResponse(data, safe=False)
