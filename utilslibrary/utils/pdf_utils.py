# coding:utf-8
import comtypes
import reportlab
from docxtpl import DocxTemplate
# from win32com.client import gencache, constants
# import comtypes.client
from PyPDF4.pdf import PdfFileWriter, PdfFileReader
from fpdf.fpdf import FPDF
import random
import string

from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from win32com.client import gencache, DispatchEx


class pdf_utils:

    def excel_to_pdf(self, excel_path, pdf_path):
        xlApp = DispatchEx("Excel.Application")
        xlApp.Visible = False
        xlApp.DisplayAlerts = 0
        books = xlApp.Workbooks.Open(excel_path, False)
        books.ExportAsFixedFormat(0, pdf_path)
        books.Close(False)
        xlApp.Quit()

    # def pdf_gen(self, temp_path, pdf_path, passwd):
    #     tpl = DocxTemplate(temp_path + 'pdf_temp.docx')
    #     tpl.render({'title': '11111'})
    #     tpl.save(temp_path + 'test.docx')
    #     self.doc_to_pdf(temp_path + 'test.docx', temp_path + 'test.pdf')
    #     self.add_passwd(temp_path + 'test.pdf', pdf_path, passwd)
    #
    def doc_to_pdf(self, word_path, pdf_path):
        """
        word转pdf
        :param wordPath: word文件路径
        :param pdfPath:  生成pdf文件路径
        """
        word = gencache.EnsureDispatch('Word.Application')
        doc = word.Documents.Open(word_path)
        #         doc.ExportAsFixedFormat(pdf_path,
        #                                 constants.wdExportFormatPDF,
        #                                 Item=constants.wdExportDocumentWithMarkup,
        #                                 CreateBookmarks=constants.wdExportCreateHeadingBookmarks)
        doc.SaveAs(pdf_path, FileFormat=17)
        doc.Close()
        word.Quit()
    #
    wdFormatPDF = 17

    def covx_to_pdf(self, infile, outfile):
        """Convert a Word .docx to PDF"""
        try:
            word = comtypes.client.CreateObject('Word.Application')
            doc = word.Documents.Open(infile)
            doc.SaveAs(outfile, FileFormat=self.wdFormatPDF)
            doc.Close()
            word.Quit()
        except Exception as e:
            print(e)

    def add_passwd(self, input_pdf, output_pdf):
        password = 12
        pdf_writer = PdfFileWriter()
        pdf_reader = PdfFileReader(open(input_pdf, 'rb'))

        print(pdf_reader.getNumPages())
        for page in range(pdf_reader.getNumPages()):
            pdf_writer.addPage(pdf_reader.getPage(page))

        print(password)
        pdf_writer.encrypt(password, owner_pwd=None,
                           use_128bit=True)

        out = open(output_pdf, 'wb')
        pdf_writer.write(out)
        out.close()
        return password

    def fpdf_test(self):
        pdf = FPDF('P')
        pdf.add_page()
        pdf.set_font('Arial', '', 16)
        pdf.set_text_color(255, 182, 193)
        pdf.cell(0, 10, 'An account on JDV Server has been created for you.', 0, 1, 'C')
        pdf.cell(0, 10, 'An account on JDV Server has been created for you.', 0, 1, 'L')
        pdf.cell(0, 10, 'An account on JDV Server has been created for you.', 0, 1, 'R')
        pdf.set_text_color(0, 0, 255)
        pdf.cell(0, 10, 'An account on JDV Server has been created for you.', 0, 1, 'C')
        pdf.cell(0, 10, 'An account on JDV Server has been created for you.', 0, 1, 'L')
        pdf.set_font('Arial', 'IU', 12)
        pdf.cell(0, 10, 'An account on JDV Server has been created for you.', 0, 1, 'R', link='http://www.baidu.com')
        pdf.set_font('Arial', '', 16)
        pdf.set_text_color(0, 255, 0)
        pdf.cell(0, 10, 'An account on JDV Server has been created for you.', 0, 1, 'C')
        pdf.cell(0, 10, 'An account on JDV Server has been created for you.', 0, 1, 'L')
        pdf.cell(0, 10, 'An account on JDV Server has been created for you.', 0, 1, 'R')
        pdf.output('test.pdf', 'F')

        print(pdf_utils().add_passwd('test.pdf', 'pass.pdf'))


# 创建水印信息
def create_watermark(content):
    """水印信息"""
    # 默认大小为21cm*29.7cm
    file_name = "mark.pdf"
    # 水印PDF页面大小
    c = canvas.Canvas(file_name, pagesize=(30 * cm, 30 * cm))
    # 移动坐标原点(坐标系左下为(0,0))
    c.translate(4 * cm, 0 * cm)
    # 设置字体格式与大小,中文需要加载能够显示中文的字体，否则就会乱码，注意字体路径
    try:
        reportlab.pdfbase.pdfmetrics.registerFont(
            reportlab.pdfbase.ttfonts.TTFont('yahei', 'C:\\Windows\\Fonts\\msyhbd.ttf'))
        c.setFont('yahei', 50)
    except:
        # 默认字体，只能够显示英文
        c.setFont("Helvetica", 30)
    # 旋转角度度,坐标系被旋转
    c.rotate(30)
    # 指定填充颜色
    c.setFillColorRGB(0, 0, 0)
    # 设置透明度,1为不透明
    c.setFillAlpha(0.15)
    # 画几个文本,注意坐标系旋转的影响
    c.drawString(0 * cm, 3 * cm, content)
    # 关闭并保存pdf文件
    c.save()
    return file_name


# 插入水印
def add_watermark(pdf_file_in, pdf_file_mark, pdf_file_out):
    pdf_output = PdfFileWriter()
    input_stream = open(pdf_file_in, 'rb')
    pdf_input = PdfFileReader(input_stream, strict=False)

    # 获取PDF文件的页数
    pageNum = pdf_input.getNumPages()

    # 读入水印pdf文件
    pdf_watermark = PdfFileReader(open(pdf_file_mark, 'rb'), strict=False)
    # 给每一页打水印
    for i in range(pageNum):
        page = pdf_input.getPage(i)
        page.mergePage(pdf_watermark.getPage(0))
        page.compressContentStreams()  # 压缩内容
        pdf_output.addPage(page)
    pdf_output.write(open(pdf_file_out, 'wb'))


if __name__ == '__main__':
    # pdf_utils().excel_to_pdf("C:/Users/15595/Desktop/績效考核表單(刘克思).xlsx", "C:/Users/15595/Desktop/2.pdf")
    # pdf_utils().fpdf_test()
    pdf_file_mark = create_watermark('test011002000300004')
    add_watermark("C:\\Users\\15595\\Desktop\\test.pdf", pdf_file_mark, "C:\\Users\\15595\\Desktop\\test111.pdf")
#     for i in range(10):
#         print(''.join(random.sample(string.ascii_letters + string.digits, 8)))
#     pdf_utils().pdf_gen('C:/Users/ligo.lu/Desktop/pdf_test/','C:/Users/ligo.lu/Desktop/pdf_test/test_passwd.pdf','1111')
#     pdf_utils().doc_to_pdf('C:/Users/15595/Desktop/593_1595383396593.docx', 'C:/Users/15595/Desktop/1.pdf')
    # pdf_utils().doc_to_pdf('C:/Users/15595/Desktop/績效考核表單(刘克思).xlsx', 'C:/Users/15595/Desktop/2.pdf')
#     pdf_utils().add_passwd('C:/Users/ligo.lu/Desktop/pdf_test/pdf_temp_wrapper.pdf', 'C:/Users/ligo.lu/Desktop/pdf_test/ppp.pdf', '111111')
