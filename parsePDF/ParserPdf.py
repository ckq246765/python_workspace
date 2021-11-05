#!/usr/bin/env python
# coding:UTF-8
# author:keqi time:2021/10/26

import xlwt
from SplitPDF2Oracle import *
from ConnectOracle import *
from Pdf_2_Image import *
from Pdf_2_SFTP import *

importlib.reload(sys)

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument, PDFTextExtractionNotAllowed
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal, LAParams

class ParserPdf:
    # 记录第一个被创建对象的引用
    instance = None
    # 记录是否执行过初始化动作
    init_flag = False

    def __new__(cls, *args, **kwargs):
        # 1.判断类属性是否为空对象，若为空说明第一个对象还没被创建
        if cls.instance is None:
            # 2.对第一个对象没有被创建，我们应该调用父类的方法，为第一个对象分配空间
            cls.instance = super().__new__(cls)
        # 3.把类属性中保存的对象引用返回给python的解释器
        return cls.instance

    def __init__(self):
        # 1.判断是否执行过初始化动作,若执行过，直觉return
        if ParserPdf.init_flag:
            return
        ParserPdf.init_flag = True

    def parse(self, path, excle_path, sheet_name, file_name):
        fp = open(path, 'rb')  # 以二进制读模式打开
        praser = PDFParser(fp) # 用文件对象来创建一个pdf文档分析器
        doc = PDFDocument(praser) # 创建一个PDF文档
        praser.set_document(doc) # 连接分析器 与文档对象
        # 检测文档是否提供txt转换，不提供就忽略
        if not doc.is_extractable:
            raise PDFTextExtractionNotAllowed
        else:
            # 创建PDf 资源管理器 来管理共享资源
            rsrcmgr = PDFResourceManager()
            # 创建一个PDF设备对象
            laparams = LAParams()
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            # 创建一个PDF解释器对象
            interpreter = PDFPageInterpreter(rsrcmgr, device)

            # 创建写入文件
            workbook = xlwt.Workbook(encoding="ascii")
            # 创建写入sheet页
            worksheet = workbook.add_sheet(sheet_name,cell_overwrite_ok=True)
            num = 0  # excle写入记录
            title_name = ""
            title_date = ""
            page_num = 0
            # 循环遍历列表，每次处理一个page的内容
            for page in PDFPage.create_pages(doc):
                interpreter.process_page(page)
                # 接受该页面的LTPage对象
                layout = device.get_result()
                # 这里layout是一个LTPage对象 里面存放着 这个page解析出的各种对象 一般包括LTTextBox, LTFigure, LTImage, LTTextBoxHorizontal 等等 想要获取文本就获得对象的text属性，
                for x in layout:
                    if (isinstance(x, LTTextBoxHorizontal)):
                        context = x.get_text()
                        print("context:" + context)
                        try:
                            if re.search("初步审定公告\s$", context) != None:
                                title_name = context
                                if num > 0:
                                    worksheet.write(num, 5, page_num)
                                    num = num + 1
                                    page_num = 0
                        except Exception:
                            print("reg_col1未匹配内容:" + context)

                        try:
                            if re.search("^[0-9]{4}年[0-9]{1,2}月[0-9]{1,2}日\s$", context) != None and num < 1:
                                title_date = context
                        except Exception:
                            print("reg_col2未匹配内容:" + context)

                        try:
                            if re.search('^第 [0-9]+ 类', context) != None or re.search('\S+\s+第 [0-9]+ 号\s+\S+', context) != None or re.search('第 [0-9]+ 类', context) != None or re.search('第 [0-9]+ 号', context) != None:
                                texts = context.split("\n")
                                for text in texts:
                                    try:
                                        if len(text.strip()) == 0:
                                            continue
                                        elif re.search('^第 [0-9]+ 号 ', text) != None:
                                            worksheet.write(num, 0, file_name)
                                            worksheet.write(num, 1, title_name)
                                            worksheet.write(num, 2, title_date)
                                            worksheet.write(num, 3, re.search('[0-9]+', text).group())
                                            worksheet.write(num, 4, page_num + 1)
                                    except Exception:
                                        print("context.split：" + text)
                                num = num + 1
                        except Exception:
                            print("reg_col3未匹配内容:" + context)

                page_num = page_num + 1
            worksheet.write(num, 5, page_num)
            workbook.save(excle_path)


    def matchText(self, context, worksheet, num):
        try:
            ret = re.search("初步审定公告\s$", context)
            if ret.group() != None:
                worksheet.write(num, 0, context)
        except Exception:
            print("reg_col1未匹配内容:" + context)

        try:
            ret = re.search("^[0-9]{4}年[0-9]{1,2}月[0-9]{1,2}日\s$", context)
            if ret.group() != None:
                worksheet.write(num, 1, context)
        except Exception:
            print("reg_col2未匹配内容:" + context)

        try:
            if re.search('^\s*第 [0-9]+ 类', context) != None or re.search('\S+\s+申 请 人\s+\S+', context) != None\
                    or re.search('\S*\s*第 [0-9]+ 类\s*', context) != None:
                texts = context.split("\n")
                for text in texts:
                    try:
                        if len(text.strip()) == 0:
                            continue
                        elif re.search('^第 [0-9]+ 类', text) != None:
                            worksheet.write(num, 2, text)
                        elif re.search('^第 [0-9]+ 号 ', text) != None:
                            worksheet.write(num, 3, text)
                        elif re.search('^申请日期\s+', text) != None:
                            worksheet.write(num, 4, text)
                        elif re.search('\S+商标\s+$', text) != None:
                            worksheet.write(num, 5, text)
                        elif re.search('^使用商品/服务\s+', text) != None:
                            worksheet.write(num, 6, text)
                        elif re.search('^申 请 人\s+', text) != None:
                            worksheet.write(num, 7, text)
                        elif re.search('^地\s+址\s+', text) != None:
                            worksheet.write(num, 8, text)
                        elif re.search('^代 理 人\s+', text) != None:
                            worksheet.write(num, 9, text)
                    except Exception:
                        print("context.split：" + text)
                num = num + 1
        except Exception:
            print("reg_col3未匹配内容:" + context)

        try:
            ret = re.search("商标使用管理规则\s$", context)
            if ret.group() != None:
                worksheet.write(num - 1, 10, context)
        except Exception:
            print("reg_col4未匹配内容:" + context)

    def test(self):
        print(re.search('^第 [0-9]+ 号', "第 6748052 号 \
    申请日期  2008 年 5 月 27 日 \
    集体商标  "))

if __name__ == '__main__':
    readFileList = ReadFileList()
    connectOracle = ConnectOracle(readFileList)
    splitPDF2Oracle = SplitPDF2Oracle(readFileList, connectOracle)
    parserPdf = ParserPdf()
    pdf_2_Image = Pdf_2_Image(readFileList)
    pdf_2_SFTP = Pdf_2_SFTP(readFileList)

    # 内网运行
    if readFileList.getActiveProfile() == "database":
        # step1  解析PDF到EXCLE
        for path in readFileList.resFileList(".pdf"):
            parserPdf.parse(path, str(path).split(".")[0]+".xls", "data", str(path).split("-")[1].split(".")[0])

        # step2
        splitPDF2Oracle.readPdf2Oracle()

        # step3
        dict = connectOracle.checkFile()
        input_str = ""
        if dict:
            while dict or input_str == "":
                input_str = input("检测到有待补全记录,是否先补全记录,再执行导入数据库？yes or no:\n")
                if str(input_str).upper() == "NO":
                    connectOracle.insertData()
                    connectOracle.analyze2Tab()
                    break
                else:
                    dict = connectOracle.checkFile()
        else:
            connectOracle.insertData()
            connectOracle.analyze2Tab()

    # 外网运行
    else:
        print("外网运行")
        # step1  解析PDF到EXCLE
        for path in readFileList.resFileList(".pdf"):
            parserPdf.parse(path, str(path).split(".")[0] + ".xls", "data", str(path).split("-")[1].split(".")[0])

        #  step2  解析PDF图片
        pdf_2_Image.parsePdf2Image()

        # step3  插入每页的PDF
        splitPDF2Oracle.readPdf2Oracle()

        # step4
        dict = connectOracle.checkFile()
        input_str = ""
        if dict:
            while dict or input_str == "":
                input_str = input("检测到有待补全记录,是否先补全记录,再执行导入数据库？yes or no:\n")
                if str(input_str).upper() == "NO":
                    connectOracle.dealWaiWangInsertData()
                    connectOracle.dealWaiWangAnalyze2Tab()
                    pdf_2_SFTP.uploadPdf(None, None)
                    break
                else:
                    dict = connectOracle.checkFile()
        else:
            connectOracle.dealWaiWangInsertData()
            connectOracle.dealWaiWangAnalyze2Tab()
            pdf_2_SFTP.uploadPdf(None, None)
