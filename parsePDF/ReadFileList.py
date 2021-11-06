#!/usr/bin/env python
# coding:UTF-8
# author:keqi time:2021/10/26

import configparser
import os
import sys

class ReadFileList(object):
    root_dir = os.path.dirname(os.path.abspath(sys.argv[0]))  # 获取当前文件所在目录的上一级目录，即项目所在目录E:\Crawler
    current_dir = os.path.abspath('.')  # 获取当前文件的绝对目录
    cf = configparser.ConfigParser()
    cf.read(root_dir + os.sep + "config.ini", "UTF-8")  # 拼接得到config.ini文件的路径，直接使用

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
        if ReadFileList.init_flag:
            return
        print("---初始化----")
        # 数据字典
        self.dict_list = {}
        self.initCreateDict()
        ReadFileList.init_flag = True

    # 初始化获取所有字典
    def initCreateDict(self):
        self.dict_list.clear()   # 如果字典已经初始化, 清空字典所有条目
        dict_values = self.getConfigByKey("dict", "dict_key")
        if dict_values.strip():
            for key_value in dict_values.split(","):
                kv = key_value.split(":")
                self.dict_list[kv[0]] = kv[1]

    # 指定添加字典
    def addDict_list(self, connectOracle):
        # 单独添加字典信息,连接的是 内网数据库 database
        if self.getActiveProfile() == "database":
            tmaas_connection = connectOracle.getConnection("tmaas")
            tmaas_cursor = tmaas_connection.cursor()
            res_code = tmaas_cursor.execute("SELECT NAME,CODE FROM TMU_BCOM.T_BCOM_DICT_ANNC")
            code = res_code.fetchall()
            for row in code:
                self.dict_list[row[0]] = row[1]
            tmaas_cursor.close()
            connectOracle.releaseConnection("tmaas", tmaas_connection)

    # 返回指定文件夹下的所有文件
    def resFileListByPath(self, filePath):
        fileList = []
        for i, j, k in os.walk(filePath):
            for fileName in k:
                fileList.append(i + os.sep + fileName)
            print(i, j, k)
        return fileList

    # 返回指定文件夹下的 指定文件类型的 所有文件
    def resFileListByPath(self, filePath, file_type):
        fileList = []
        for i, j, k in os.walk(filePath):
            for fileName in k:
                if fileName.endswith(file_type):
                    fileList.append(i + os.sep + fileName)
            print(i, j, k)
        return fileList

    # 获取配置文件夹下的指定类型 文件
    def resFileList(self, type):
        fileList = []
        filePath = self.getConfigByKey("file", "filepath")
        for i, j, k in os.walk(filePath):
            for fileName in k:
                if fileName.endswith(type):
                    fileList.append(i + os.sep + fileName)
            print(i, j, k)
        print(fileList)
        return fileList
    
    def getCurrentProPath(self):
        return os.path.abspath('.')
    
    def getConfigParser(self):
        return self.cf
    
    def getSections(self):
        return self.cf.sections()  # 获取文件中所有的section(一个配置文件中可以有多个配置，如数据库相关的配置，邮箱相关的配置，每个section由[]包裹，即[section])，并以列表的形式返回

    def getOptions(self, section):
        self.cf.options(section)   # 获取某个section名为 database 所对应的键
    
    def getItems(self, section):
        return self.cf.items(section)  # 获取section名为 database 所对应的全部键值对
    
    def getConfigByKey(self, options, key):
        print("root_dir:" + str(self.root_dir))
        return self.cf.get(options, key)  # 获取 section 中 key 对应的值

    # 返回活动的数据库模式前缀
    def getConfigDB(self):
        dbs = set()
        for item in self.getItems(self.getActiveProfile()):
            db = item[0].split("_")[0]
            if db.lower() != "linux":
                dbs.add(db)
        return dbs

    # 返回活动的数据库配置
    def getActiveProfile(self):
        active = self.getConfigByKey("profile", "active")
        if not active:
            return "database"
        return active

if __name__ == '__main__':
    readFileList = ReadFileList()
    l = readFileList.resFileListByPath("E:\桌面\恶意提示加注\image\-1245", ".jpg")
    print(l)




