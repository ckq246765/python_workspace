#!/usr/bin/env python
# coding:UTF-8
# author:keqi time:2021/11/04
import os
from pathlib import Path
from ReadFileList import *
import fitz

class Pdf_2_Image:
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

    def __init__(self, readFileList):
        # 1.判断是否执行过初始化动作,若执行过，直觉return
        if Pdf_2_Image.init_flag:
            return
        self.readFileList = readFileList
        Pdf_2_Image.init_flag = True

    '''
    # 插入图片目录下，生成对应的pdf所有图片目录
    # 将PDF转化为图片
    pdfPath pdf文件的路径
    imgPath 图像要保存的文件夹
    zoom_x x方向的缩放系数
    zoom_y y方向的缩放系数
    rotation_angle 旋转角度
    '''
    def pdf_image(self, pdfPath, imgPath, zoom_x, zoom_y, rotation_angle):
        # 打开PDF文件
        pdf = fitz.open(pdfPath)

        # 生成对应的目录
        file = Path(pdfPath)
        file_name = file.name.split(".")[0].replace("-", "")
        imgPath = imgPath + os.sep + file_name
        Path(imgPath).mkdir(parents=True, exist_ok=True)

        # 逐页读取PDF
        for pg in range(0, pdf.pageCount):
            page = pdf[pg]
            # 设置缩放和旋转系数
            trans = fitz.Matrix(zoom_x, zoom_y).preRotate(rotation_angle)
            pm = page.getPixmap(matrix=trans, alpha=False)
            # 开始写图像
            pm.writePNG(imgPath + os.sep + str(pg + 1) + ".jpg")
        pdf.close()

    def parsePdf2Image(self):
        imagepath = self.readFileList.getConfigByKey("file", "imagepath")
        if not imagepath:
            imagepath = self.readFileList.getConfigByKey("file", "filepath")
            path = Path(imagepath)
            image_local_path = str(path.parent.absolute()) + os.sep + "image"
            # 判断文件或文件夹是否存在可以用来安全的创建文件
            Path(image_local_path).mkdir(parents=True, exist_ok=True)
            imagepath = image_local_path

        for path in self.readFileList.resFileList(".pdf"):
            self.pdf_image(path, imagepath, 5, 5, 0)


if __name__ == '__main__':
    readFileList = ReadFileList()
    pdf_2_Image = Pdf_2_Image(readFileList)
    pdf_2_Image.parsePdf2Image()