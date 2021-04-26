# code: utf-8
import logging
import os
import smtplib
import traceback
import time
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jdv.models import email_group
from jdv.service.pdf_service import get_mail_pdf

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Mask_DP.settings')
django.setup()
log = logging.getLogger('log')
mail_host = "192.168.40.11"  # 设置服务器
mail_user = "neo.liu@qxic.net"  # 用户名
mail_pass = "!qxic666"  # 口令

url = 'http://172.16.20.242:8090/workflow/maskdp/check/?id=%s&user_id=%s'


def send_mail(pdf_pwd, pdf_path, pdf_name):
    sender = 'harry.tao@qxic.net'
    receivers = ['harry.tao@qxic.net']
    # password = send_pdf_email(sender, receivers)
    # if password:
    #     send_password_email(password, receivers)

    send_pdf_email(sender, receivers, pdf_path, pdf_name)
    time.sleep(1)
    send_password_email(sender, receivers, pdf_pwd)


def send_pdf_email(sender, receivers, pdf_path, pdf_name):
    print('111')
    """发送pdf邮件方法"""
    sender = sender
    receivers = receivers  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    message = MIMEMultipart()
    message['From'] = Header("admin@qxic.net", 'utf-8')
    message['To'] = Header("customer", 'utf-8')
    subject = 'JDV Notice'
    message['Subject'] = Header(subject, 'utf-8')

    # 邮件正文内容
    message.attach(MIMEText('Welcome to QXIC Job Deck View System.', 'plain', 'utf-8'))

    # 生成pdf
    # flag, path, password = get_mail_pdf()

    # 构造附件1，传送当前目录下的 test.txt 文件
    att = MIMEText(open(pdf_path, 'rb').read(), 'base64', 'utf-8')
    att["Content-Type"] = 'application/octet-stream'

    # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
    att["Content-Disposition"] = 'attachment; filename=' + pdf_name
    message.attach(att)

    try:
        smtpObj = smtplib.SMTP(host='192.168.40.11')
        smtpObj.connect(mail_host, 465)  # 25 为 SMTP 端口号
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        log.info(pdf_path + '邮件发送成功')
        return True
    except smtplib.SMTPException:
        log.error(pdf_path + '无法发送邮件')
        log.error(traceback.format_exc())
        return None


def send_password_email(sender, receivers, pdf_pwd):
    print('222')
    """发送pdf密码email"""
    sender = sender
    receivers = receivers  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    message = MIMEText('This Pdf Password is ' + pdf_pwd, 'plain', 'utf-8')
    message['From'] = Header("admin@qxic.net", 'utf-8')
    message['To'] = Header("customer", 'utf-8')
    subject = 'Pdf Password'
    message['Subject'] = Header(subject, 'utf-8')
    try:
        smtpObj = smtplib.SMTP(host='192.168.40.11')
        smtpObj.connect(mail_host, 465)  # 25 为 SMTP 端口号
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        log.info("password邮件发送成功")
    except Exception as e:
        log.error('Error: 无法发送邮件')
        log.error(traceback.format_exc())


def get_receivers(user_id):
    """获取邮件组"""
    group_id = email_group.objects.values('group_id').get(pk=user_id)
    if group_id:
        l = []
        email_list = email_group.objects.values('email').filter(group_id=group_id)
        for e in email_list:
            l.append(e['email'])
        return list(l)
    else:
        log.error('id为%s的用户没有office_id' % user_id)
        return None


def send_sign_notice(receivers, name, data_form_id, user_id, path_list):
    sender = 'Bard.Zhang@qxic.net'
    receivers = receivers  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    message = MIMEMultipart()
    message['From'] = Header("MaskDP@qxic.net", 'utf-8')
    message['To'] = Header(name, 'utf-8')
    subject = 'Mask DP Sign Off Notice'
    message['Subject'] = Header(subject, 'utf-8')

    # 邮件正文内容
    message.attach(MIMEText('There is a process that needs your approval, please log in to your Mask DP account for '
                            'approval. '
                            ' DP system website: '
                            'http://172.16.20.242:8090/workflow/maskdp/check/?id=%s&user_id=%s'
                            % (data_form_id,
                               user_id),
                            'plain', 'utf-8'))
    for path in path_list:
        att = MIMEApplication(open(path, 'rb').read())
        att.add_header('Content-Disposition', 'attachment', filename=path.split('/')[-1])
        message.attach(att)
    try:
        smtpObj = smtplib.SMTP(host='192.168.40.11')
        smtpObj.connect(mail_host, 465)  # 25 为 SMTP 端口号
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        # log.info(pdf_path + '邮件发送成功')
        return True
    except smtplib.SMTPException:
        # log.error(pdf_path + '无法发送邮件')
        log.error(traceback.format_exc())
        return None


if __name__ == '__main__':
    send_sign_notice()
