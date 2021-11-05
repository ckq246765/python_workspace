#!/usr/bin/env python
# coding:UTF-8
# author:keqi time:2021/10/26
import os
from pathlib import Path

import PyPDF2
import importlib
from ConnectOracle import *
from ReadFileList import *


importlib.reload(sys)

class SplitPDF2Oracle:
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

    def __init__(self, readFileList, connectOracle):
        # 1.判断是否执行过初始化动作,若执行过，直觉return
        if SplitPDF2Oracle.init_flag:
            return
        self.readFileList = readFileList
        self.connectOracle = connectOracle
        SplitPDF2Oracle.init_flag = True

    def readPdf2Oracle(self):
        for path in self.readFileList.resFileList(".pdf"):
            self.splitPdf(path)

    def splitPdf(self, file_path):
        connection = self.connectOracle.getConnection("tmedms")

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

            # 内网
            if self.readFileList.getActiveProfile() == "database":
                self.write2DB(connection, new_name, page_num + 1, source_name)
            # 外网
            else:
                file_name = source_name.split(".")[0].split("-")[1]
                self.dealWaiWangWrite2DB(connection, new_name, page_num + 1, source_name)

            os.remove(str(new_name))
        pdf_file.close()
        connection.commit()
        self.connectOracle.releaseConnection("tmedms", connection)

    # 内网处理
    def write2DB(self, connection, file_path, page_num, source_name):
        file_name = re.match(r'[0-9]+', source_name.split(".")[0].split("-")[1]).group()

        cursor = connection.cursor()
        file = open(file_path, 'rb')
        context = file.read()
        file.close()
        cursor.execute("INSERT INTO TMU_TMEDMS.T_PARSER_PDF_PAGE_CONTEXT(FILE_NAME, PAGE_NUM, PDF_PAGE_CONTEXT) VALUES (:fileName, :pageNum, :blobData)"
                       , fileName=str(file_name), pageNum=page_num, blobData=context)
        cursor.close()

    # 外网处理
    def dealWaiWangWrite2DB(self, connection, file_path, page_num, source_name):
        file_name = re.match(r'[0-9]+', source_name.split(".")[0].split("-")[1]).group()

        cursor = connection.cursor()
        file = open(file_path, 'rb')
        context = file.read()
        file.close()

        # 获取生成的图片
        imagepath = self.readFileList.getConfigByKey("file", "imagepath")
        if not imagepath:
            imagepath = self.readFileList.getConfigByKey("file", "filepath")
            path = Path(imagepath)
            image_local_path = str(path.parent.absolute()) + os.sep + "image"
            # 判断文件或文件夹是否存在可以用来安全的创建文件
            Path(image_local_path).mkdir(parents=True, exist_ok=True)
            imagepath = image_local_path
        image_source_path = "/group2/M00/96/49/" + Path(source_name.split(".")[0]).name.replace("-","") + "/" + str(page_num) + ".jpg"
        imgPath = imagepath + os.sep + Path(source_name.split(".")[0]).name.replace("-","") + os.sep + str(page_num) + ".jpg"   # 本地的图片路径
        file = open(imgPath, 'rb')
        image_context = file.read()
        file.close()

        cursor.execute(
            "INSERT INTO TMU_ANN.T_PARSER_PDF_PAGE_CONTEXT(FILE_NAME, PAGE_NUM, PDF_PAGE_CONTEXT, PDF_PAGE_CONTEXT_IMAGE, IMAGE_PATH) VALUES (:fileName, :pageNum, :blobData, :image_context, :IMAGE_PATH)"
            , fileName=str(file_name), pageNum=page_num, blobData=context, image_context=image_context, IMAGE_PATH=image_source_path)
        cursor.close()

if __name__ == '__main__':
    readFileList = ReadFileList()
    connectOracle = ConnectOracle(readFileList)
    splitPDF2Oracle = SplitPDF2Oracle(readFileList, connectOracle)
    splitPDF2Oracle.readPdf2Oracle()
