# -*- coding: utf-8 -*-
import smtplib
import traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header


def mail():
    # 第三方 SMTP 服务
    mail_host = "192.168.40.11"  # 设置服务器
    mail_user = "Neo.Liu@qxic.net"  # 用户名
    mail_pass = "!qxic666666"  # 口令
    sender = 'Neo.Liu@qxic.net'
    receivers = ['neo.liu@qxic.net']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    message = MIMEText('Python 邮件发送测试...', 'plain', 'utf-8')
    message['From'] = Header("qxic", 'utf-8')
    message['To'] = Header("neo.liu@qxic.net", 'utf-8')
    subject = 'Python SMTP 邮件测试'
    message['Subject'] = Header(subject, 'utf-8')
    # smtpObj = smtplib.SMTP(host='192.168.40.11')
    # smtpObj.connect(mail_host, 465)  # 25 为 SMTP 端口号
    # smtpObj.ehlo()
    # smtpObj.starttls()
    # smtpObj.login(mail_user, mail_pass)
    # smtpObj.sendmail(sender, receivers, message.as_string())
    # print("邮件发送成功")
    try:
        smtpObj = smtplib.SMTP(host='192.168.40.11')
        smtpObj.connect(mail_host, 465)  # 25 为 SMTP 端口号
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("邮件发送成功")
    except Exception as e:
        print(traceback.format_exc())
        print("Error: 无法发送邮件")


def send_file_email():
    mail_host = "192.168.40.11"  # 设置服务器
    mail_user = "Neo.Liu@qxic.net"  # 用户名
    mail_pass = "!qxic666666"  # 口令
    sender = 'Neo.Liu@qxic.net'
    receivers = ['1559504282@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    message = MIMEMultipart()
    message['From'] = Header("fromfromfrom", 'utf-8')
    message['To'] = Header("tototo", 'utf-8')
    subject = 'Python SMTP 邮件测试'
    message['Subject'] = Header(subject, 'utf-8')

    # 邮件正文内容
    message.attach(MIMEText('Python 邮件发送测试...', 'plain', 'utf-8'))

    # 构造附件1，传送当前目录下的 test.txt 文件
    att1 = MIMEText(open('c:/Neo/hello.pdf', 'rb').read(), 'base64', 'utf-8')
    att1["Content-Type"] = 'application/octet-stream'
    # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
    att1["Content-Disposition"] = 'attachment; filename="hello.pdf"'
    message.attach(att1)

    smtpObj = smtplib.SMTP(host='192.168.40.11')
    smtpObj.connect(mail_host, 465)  # 25 为 SMTP 端口号
    smtpObj.ehlo()
    smtpObj.starttls()
    smtpObj.login(mail_user, mail_pass)
    smtpObj.sendmail(sender, receivers, message.as_string())
    print("邮件发送成功")
    # try:
    #     smtpObj = smtplib.SMTP()
    #     smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
    #     smtpObj.login(mail_user, mail_pass)
    #     smtpObj.sendmail(sender, receivers, message.as_string())
    #     print("邮件发送成功")
    # except smtplib.SMTPException:
    #     print("Error: 无法发送邮件")


if __name__ == '__main__':
    # send_file_email()
    # mail()
    dict = {}
    print('a' in dict.keys())
    print(False and True)