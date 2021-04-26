# code: utf-8

import logging
import string
import random
import traceback

from PyPDF4 import PdfFileReader, PdfFileWriter
from fpdf import FPDF
from Mask_DP.settings import PROJECT_NAME
import os

log = logging.getLogger('log')


class PDF(FPDF):
    def header(self):
        # logo
        self.image('static/logo/QYMASK.png', 10, 5, 20, 20)
        self.set_font('Arial', 'B', 20)
        self.cell(0, 15, 'QYMASK', 0, 1, 'C')
        self.cell(0, 0, '', 'B')
        self.ln(10)


def get_mail_pdf(user_name, password, pdf_pwd, expire_date):
    # return gen_pdf(gen_user_name(6), gen_password(10), '2020/12/12', 'D:/zzz/test_01.pdf')

    cur_path = os.path.abspath(os.path.dirname(__file__)).split(PROJECT_NAME)[0]  # 获得项目同级目录
    sgd_pdf_path = os.path.join(os.path.dirname(cur_path), PROJECT_NAME + '_SGD_PDF')
    print(sgd_pdf_path)
    if not os.path.exists(sgd_pdf_path):
        os.mkdir(sgd_pdf_path)  # 如果不存在这个logs文件夹，就自动创建一个
    sgd_pdf_path = sgd_pdf_path + '\\'
    print(sgd_pdf_path)
    return gen_pdf(user_name, password, pdf_pwd, expire_date, sgd_pdf_path)


def gen_pdf(user_name, password, pdf_pwd, expiration_date, pdf_path):
    """生成pdf文件的内容"""
    pdf = PDF('P')
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Arial', '', 15)
    pdf.cell(0, 10, 'An account on rJDV Server has been created for you.', 0, 1, 'C')
    pdf.cell(0, 10, 'Following is the detailed account information.', 0, 1, 'C')
    pdf.ln(10)
    pdf.set_fill_color(192, 192, 192)
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(50)
    pdf.cell(50, 8, 'UserName:', 0, 0, 'L', 1)
    pdf.cell(0, 8, user_name, 0, 1, 'L')
    pdf.ln(2)
    pdf.cell(50)
    pdf.cell(50, 8, 'Password:', 0, 0, 'L', 1)
    pdf.cell(0, 8, password, 0, 1, 'L')
    pdf.ln(2)
    pdf.cell(50)
    pdf.cell(50, 8, 'Expiration Date:', 0, 0, 'L', 1)
    pdf.cell(0, 8, expiration_date, 0, 1, 'L')
    pdf.ln(15)
    pdf.set_font('Arial', '', 15)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 10, 'Note: The password is case-sensitive.', 0, 1, 'C')
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, 'Thank you for using QXIC server.', 0, 1, 'C')
    input_path = pdf_path + user_name + '.pdf'
    pdf.output(input_path, 'F')
    pdf.close()
    log.info("PDF文件生成成功，路径为%s" % pdf_path)
    # 加密pdf文件
    out_path = pdf_path + user_name + '_encrypt.pdf'
    flag, encrypt_password = encrypt_pdf(input_path, out_path, pdf_pwd)
    if flag:
        log.info("PDF文件加密成功，加密后路径为%s" % out_path)
        return True, out_path, encrypt_password
    else:
        log.info("PDF文件加密失败")
        return False, out_path, encrypt_password


# def gen_user_name(num):
#     return ''.join(random.sample(string.ascii_lowercase, num))
#
#
# def gen_password(num):
#     return ''.join(random.sample(string.ascii_letters + string.digits, num))


def encrypt_pdf(input_pdf, output_pdf, pdf_pwd):
    try:
        # password = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        password = pdf_pwd
        pdf_writer = PdfFileWriter()
        input = open(input_pdf, 'rb')
        pdf_reader = PdfFileReader(input)
        for page in range(pdf_reader.getNumPages()):
            pdf_writer.addPage(pdf_reader.getPage(page))
        pdf_writer.encrypt(password, owner_pwd=None, use_128bit=True)
        print(password)
        out = open(output_pdf, 'wb')
        pdf_writer.write(out)
        input.close()
        out.close()
        return True, password

    except Exception as e:
        log.error("pdf加密方法出现错误：")
        log.error(traceback.format_exc())
        return False, password
