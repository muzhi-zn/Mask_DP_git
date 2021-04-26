import logging
import os
import re
import string
import traceback
import random

from jdv.service.email_service import send_pdf_email, send_password_email
from jdv.service.pdf_service import get_mail_pdf
from query_system.models import jdv_data
from system.models import sgd_user, user
from tooling_form.models import product_info
from utilslibrary.system_constant import Constant
from utilslibrary.utils.sftp_utils import sftp_upload


log = logging.getLogger("log")


def jdv_service():
    """jdv执行的流程"""
    """
    1、先创建对应的sgd账号
    2、创建jb文件
    3、上传jb及对应的文件到sgd服务器
    4、发送邮件到客户
    """
    pass


def upload_jdv_file(jdv_data_id, jdv_path, jb_file_name):
    """利用sftp上传jdv文件到sgd_server"""
    try:
        jb_file_path = os.path.join(jdv_path, jb_file_name)
        jdv_data_obj = jdv_data.objects.get(id=jdv_data_id)
        sgd_user_obj = sgd_user.objects.get(id=jdv_data_obj.jdv_account)
        sgd_account = sgd_user_obj.user_name
        sgd_password = sgd_user_obj.user_pwd
        mebes_list = match_mebes_file(jb_file_path)
        product_path = os.path.join(Constant.DEVICE_INFO_FILE_BASE_PATH, jdv_data_obj.product_name)
        jdv_path = os.path.join(product_path, "JDV")
        non_existent_list = judge_mebes_file(jdv_path, mebes_list)
        if len(non_existent_list) > 0:  # 存在未找到的mebes档案
            msg = ""
            for non_e in non_existent_list:
                msg += non_e + ','
            return False, msg + "not existent"
        # 连接sgd server上传档案
        sgd_server_ip = Constant.SGD_SERVER_IP
        # 上传jb文件
        log.info("开始上传jb文件--" + jb_file_path)
        sftp_upload(sgd_server_ip, 22, sgd_account, sgd_password, jb_file_path, './' + jb_file_name)
        log.info("jb文件上传成功--" + jb_file_path)
        # 上传mebes档案
        log.info("开始上传mebes文件--" + jdv_path)
        for mebes_file in mebes_list:
            local_path = os.path.join(jdv_path, mebes_file)
            log.info("上传mebes文件--" + local_path)
            sftp_upload(sgd_server_ip, 22, sgd_account, sgd_password, local_path, './' + jb_file_name)
        return True, "Upload Success"
    except Exception as e:
        log.error("jdv_upload_file出现错误：" + str(e))
        traceback.print_exc()
        return False, str(e)


def match_mebes_file(jb_file_path):
    """从jb文件中筛选出mebes档"""
    with open(jb_file_path) as jb_obj:  # 从文件中读取内容
        jb_content = jb_obj.read()
        match_list = re.findall(r'\w{7}-\w{2}-\w{2}', jb_content)
        match_list = list(set(match_list))
        mebes_list = []
        for s in match_list:
            arr = str(s).split("-")
            mebes = arr[0] + arr[1] + '.' + arr[2]
            mebes_list.append(mebes)
        print(mebes_list)
        return mebes_list


def judge_mebes_file(jdv_path, mebes_list):
    """检查mebes档是否存在, 返回不存在的列表"""
    non_existent_list = []
    for mebes_file in mebes_list:
        mebes_file_path = os.path.join(jdv_path, mebes_file)
        if not os.path.exists(mebes_file_path):
            non_existent_list.append(mebes_file)
    return non_existent_list


def send_mail(jdv_data_id):
    """发送pdf邮件"""
    # 创建pdf文件
    jdv_data_obj = jdv_data.objects.get(id=jdv_data_id)
    s_u = sgd_user.objects.get(id=jdv_data_obj.jdv_account)
    sgd_user_name = s_u.user_name
    sgd_password = s_u.user_pwd
    expire_date = s_u.extension_expire_date
    pdf_password = ''.join(random.sample(string.ascii_letters + string.digits, 8))
    flag, pdf_path, pdf_pwd = get_mail_pdf(sgd_user_name, sgd_password, pdf_password, expire_date)
    if flag:  # pdf生成成功
        # 获取该产品的创建人
        tip_no = jdv_data_obj.tip_no
        product_info_obj = product_info.objects.get(tip_no=tip_no, is_delete=0)
        user_email = user.objects.get(id=product_info_obj.create_by).email
        # 发送pdf附件email
        email_flag = send_pdf_email("neo.liu@qxic.net", [user_email], pdf_path, "jdv_account_info.pdf")
        if email_flag:
            # 发送pdf密码邮件
            send_password_email("neo.liu@qxic.net", [user_email], pdf_pwd)
            log.info("密码文件发送成功")
            return True, "邮件发送成功"
        else:
            return False, "PDF邮件发送失败"
    else:  # pdf生成失败
        return False, "PDF文件生成失败"


if __name__ == "__main__":
    match_mebes_file("C:\\qxic\\qxic\\MaskData\\Engineering\\example\\QEA001\\JDV\\test1.jb")
