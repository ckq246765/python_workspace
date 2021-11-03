#!/usr/bin/env python
# coding:utf8
# author:keqi time:2021/10/26

import sys
import re
import xlwt
import xlrd
import xlutils.copy
import PyPDF2
import os
import importlib
import readFileList
import cx_Oracle
importlib.reload(sys)

def readPdf2Oracle():
    for path in readFileList.resFileList(".pdf"):
        splitPdf(path)

def splitPdf(file_path):
    connection = cx_Oracle.connect(
        readFileList.getConfigByKey("database", "username"), readFileList.getConfigByKey("database", "password"),
        readFileList.getConfigByKey("database", "host"), encoding="UTF-8")

    pdf_file = open(file_path, 'rb')  # 获取原 PDF 文件
    pdf_reader = PyPDF2.PdfFileReader(pdf_file)  # 创建 PDF 对象
    source_name = pdf_file.name  # 获取源文件名称，包含绝对路径

    for page_num in range(pdf_reader.numPages):  # 将每页内容分别写入一个新文件
        pdf_writer = PyPDF2.PdfFileWriter()  # 创建一个空白 PDF 对象
        pdf_writer.__init__()  # 将 PDF 对象初始化
        page_obj = pdf_reader.getPage(page_num)
        pdf_writer.addPage(page_obj)  # 向空白 PDF 对象中添加要复制的 PDF页面

        new_name = source_name[:-4] + "-" + str(page_num) + ".pdf"
        pdf_new_file = open(new_name, 'wb')  # 创建一个新文件
        pdf_writer.write(pdf_new_file)  # 将添加了内容的空白 PDF 对象，写入到新建文件中
        pdf_new_file.close()

        file_name = re.match(r'[0-9]+', source_name.split(".")[0].split("-")[1]).group()
        write2DB(connection, new_name, page_num + 1, file_name)
        os.remove(str(new_name))

    pdf_file.close()
    connection.commit()

def write2DB(connection, file_path, page_num, file_name):
    cursor = connection.cursor()
    file = open(file_path, 'rb')
    context = file.read()
    file.close()
    cursor.execute("INSERT INTO TMU_TMEDMS.T_PARSER_PDF_PAGE_CONTEXT(FILE_NAME, PAGE_NUM, PDF_PAGE_CONTEXT) VALUES (:fileName, :pageNum, :blobData)"
                   , fileName=str(file_name), pageNum=page_num, blobData=context)
    cursor.close()

if __name__ == '__main__':
    readPdf2Oracle()


