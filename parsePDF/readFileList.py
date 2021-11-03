#!/usr/bin/env python
# coding:utf8
# author:keqi time:2021/10/26

import os
import configparser
import sys

root_dir = os.path.dirname(os.path.abspath(sys.argv[0]))  # 获取当前文件所在目录的上一级目录，即项目所在目录E:\Crawler
current_dir = os.path.abspath('.')  # 获取当前文件的绝对目录
cf = configparser.ConfigParser()
cf.read(root_dir + "\\config.txt", "UTF-8")  # 拼接得到config.ini文件的路径，直接使用


def resFileList(filePath):
    fileList = []
    for i, j, k in os.walk(filePath):
        for fileName in k:
            fileList.append(i + "\\" + fileName)
        print(i, j, k)
    return fileList

def resFileList(type):
    fileList = []
    filePath = getConfigByKey("file", "filepath")
    for i, j, k in os.walk(filePath):
        for fileName in k:
            if fileName.endswith(type):
                fileList.append(i + "\\" + fileName)
        print(i, j, k)
    print(fileList)
    return fileList

def getCurrentProPath():
    return os.path.abspath('.')

def getConfigParser():
    return cf

def getSections():
    return cf.sections()  # 获取文件中所有的section(一个配置文件中可以有多个配置，如数据库相关的配置，邮箱相关的配置，每个section由[]包裹，即[section])，并以列表的形式返回

def getOptions(section):
    cf.options(section)   # 获取某个section名为 database 所对应的键

def getItems(section):
    return cf.items(section)  # 获取section名为 database 所对应的全部键值对

def getConfigByKey(options, key):
    print("root_dir:" + str(root_dir))
    return cf.get(options, key)  # 获取 section 中 key 对应的值

if __name__ == '__main__':
    print("hhh:" + getConfigByKey("database", "host"))
