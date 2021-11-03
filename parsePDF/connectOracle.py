#!/usr/bin/env python
# coding:utf8
# author:keqi time:2021/10/27
import os
from datetime import datetime

import cx_Oracle

import readFileList
import xlrd
import re

def insertData():
    connection = cx_Oracle.connect(
        readFileList.getConfigByKey("database", "username"), readFileList.getConfigByKey("database", "password"),
        readFileList.getConfigByKey("database", "host"), encoding="UTF-8")
    tmaas_connection = cx_Oracle.connect(
        readFileList.getConfigByKey("database", "tmaas_username"), readFileList.getConfigByKey("database", "tmaas_password"),
        readFileList.getConfigByKey("database", "tmaas_host"), encoding="UTF-8")
    files = readFileList.resFileList(".xls")
    print(files)
    for path in files:
        # 导入需要读取Excel表格的路径
        data = xlrd.open_workbook(path)
        sheet = data.sheets()[0]
        # 使用连接进行查询
        cursor = connection.cursor()
        # 商标每个标题的数量
        tm_num = 1
        print("sheet.nrows-1:" + str(sheet.nrows-1))
        for i in range(0, sheet.nrows):
            print("i:" + str(i))
            if sheet.cell_type(i, 0) not in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
                tmaas_cursor = tmaas_connection.cursor()
                res_code = tmaas_cursor.execute("select code from TMU_BCOM.T_BCOM_DICT_ANNC  where name='{}'"
                                                .format(str(re.sub(r'\W+', ' ', sheet.row(i)[1].value).strip())))
                code = res_code.fetchone()
                tmaas_cursor.close()
                cursor.execute(
                    "insert into TMU_TMEDMS.T_PARSER_PDF_DATA (FILE_NAME, TITLE_NAME, TITLE_DATE, REG_NUM, PAGE_NUM) \
                    values ('{FILE_NAME}', '{TITLE_NAME}', '{TITLE_DATE}','{REG_NUM}', '{PAGE_NUM}')".format(
                        FILE_NAME=re.match(r'[0-9]+', re.sub(r'\W+', ' ', sheet.row(i)[0].value).strip()).group(),
                        TITLE_NAME=code[0],
                        TITLE_DATE=re.sub(r'(\d{4})年(\d{1,2})月(\d{1,2})日', r'\1-\2-\3', re.sub(r'\W+', ' ', sheet.row(i)[2].value).strip()),
                        REG_NUM=re.sub(r'\W+', ' ', sheet.row(i)[3].value).strip(),
                        PAGE_NUM=str(sheet.row(i)[4].value).strip().split(".")[0]
                    ))

            if sheet.cell_type(i, 5) not in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
                print("--" + str(sheet.row(i)[5].value))
                cursor.execute("update TMU_TMEDMS.T_PARSER_PDF_DATA set LAST_PAGE_NUM={LAST_PAGE_NUM},TOTAL_NUM={TOTAL_NUM} where LAST_PAGE_NUM is null ".format(
                        LAST_PAGE_NUM=tm_num - 1,
                        TOTAL_NUM=str(sheet.row(i)[5].value).strip().split(".")[0]
                        ))
                tm_num = 1
            tm_num = tm_num + 1

        cursor.close()
        os.remove(path)
    connection.commit()

def analyze2Tab():
    # 插入每期公告类型数据  TMU_TMEDMS.T_TMEDMS_TM_ANN_INFO
    connection = cx_Oracle.connect(
        readFileList.getConfigByKey("database", "username"), readFileList.getConfigByKey("database", "password"),
        readFileList.getConfigByKey("database", "host"), encoding="UTF-8")
    cursor = connection.cursor()
    _result = cursor.execute("SELECT  A.FILE_NAME,A.TITLE_DATE,A.TITLE_NAME,A.LAST_PAGE_NUM,A.TOTAL_NUM\
 FROM TMU_TMEDMS.T_PARSER_PDF_DATA a GROUP BY A.FILE_NAME,A.TITLE_DATE,A.TITLE_NAME,A.LAST_PAGE_NUM,A.TOTAL_NUM ORDER BY A.FILE_NAME")
    for row in _result.fetchall():
        result = cursor.execute("SELECT A.ID FROM TMU_TMEDMS.T_TMEDMS_TM_ANN_INFO A WHERE A.ANN_NUM=:ANN_NUM AND A.ANN_TYPE_CODE=:ANN_TYPE_CODE"
                       ,
                       ANN_NUM=row[0],
                       ANN_TYPE_CODE=row[2]
                       )
        his_data = result.fetchone()
        if his_data:
            cursor.execute("UPDATE TMU_TMEDMS.T_TMEDMS_TM_ANN_INFO A SET A.CASE_NUM=:CASE_NUM, A.PAGE_NUM=:PAGE_NUM,A.UPDATE_USER='GAGE' WHERE A.ID=:ID"
                           ,
                           CASE_NUM = int(row[3]),
                           PAGE_NUM = int(row[4]),
                           ID = his_data[0]
                           )
        else:
            cursor.execute("INSERT INTO TMU_TMEDMS.T_TMEDMS_TM_ANN_INFO(ID,ANN_NUM,ANN_DATE,ANN_TYPE_CODE,CASE_NUM,PAGE_NUM,IS_VALID,OFF_STATE,CREATE_USER)VALUES(SYS_GUID(), :ANN_NUM, :ANN_DATE, :ANN_TYPE_CODE, :CASE_NUM, :PAGE_NUM, 1, 1, 'GAGE')"
                            ,
                            ANN_NUM=row[0],
                            ANN_DATE=datetime.strptime(row[1], '%Y-%m-%d'),
                            ANN_TYPE_CODE=row[2],
                            CASE_NUM=int(row[3]),
                            PAGE_NUM=int(row[4])
                            )

    # 插入注册号数据 TMU_TMEDMS.T_TMEDMS_TM_ANN_SEARCH
    _result = cursor.execute("SELECT A.FILE_NAME,A.TITLE_NAME, A.REG_NUM,A.PAGE_NUM FROM TMU_TMEDMS.T_PARSER_PDF_DATA A")
    for row in _result.fetchall():
        cursor.execute("INSERT INTO TMU_TMEDMS.T_TMEDMS_TM_ANN_SEARCH(ID,ANN_NUM,ANN_TYPE_CODE,REG_NUM,PAGE_NO,IS_VALID,CREATE_USER)VALUES(SYS_GUID(), :ANN_NUM, :ANN_TYPE_CODE, :REG_NUM, :PAGE_NO, 1, 'GAGE')"
                       ,
                       ANN_NUM=row[0],
                       ANN_TYPE_CODE=row[1],
                       REG_NUM=row[2],
                       PAGE_NO=row[3]
                       )
    connection.commit()

    # 插入每页PDF内容 TMU_TMEDMS.T_TMEDMS_TM_ANNO_FILES
    _result = cursor.execute("SELECT A.ID,A.ANN_NUM,A.ANN_TYPE_CODE,A.PAGE_NUM FROM TMU_TMEDMS.T_TMEDMS_TM_ANN_INFO A WHERE A.CREATE_USER='GAGE'ORDER BY A.ANN_NUM,A.PAGE_NUM")
    rows = _result.fetchall()
    ANN_NUM = ""
    PAGE_NUM = 0
    min_page_num = 0
    max_page_num = 0
    for i in range(len(rows)):
        DOC_ID = rows[i][0]
        if ANN_NUM == "" or ANN_NUM != rows[i][1]:
            ANN_NUM = rows[i][1]
            PAGE_NUM = rows[i][3]
            min_page_num = 0
            max_page_num = 0
            max_page_num = rows[i][3]
        elif ANN_NUM == rows[i][1]:
            min_page_num = max_page_num
            max_page_num = max_page_num + rows[i][3]

        _result = cursor.execute("SELECT A.ID,:ID,A.PAGE_NUM-:min_page_num,A.PDF_PAGE_CONTEXT FROM TMU_TMEDMS.T_PARSER_PDF_PAGE_CONTEXT A WHERE A.FILE_NAME =:ANN_NUM  AND :min_page_num<a.page_num  AND A.PAGE_NUM<=:max_page_num ORDER BY A.PAGE_NUM"
                       ,
                       ID = DOC_ID,
                       min_page_num = min_page_num,
                       ANN_NUM = ANN_NUM,
                       max_page_num = max_page_num
                       )
        for row in _result.fetchall():
            cursor.execute("INSERT INTO TMU_TMEDMS.T_TMEDMS_TM_ANNO_FILES(ID,DOC_ID,DOC_TYPE_CODE,DOC_NO,CONTENT,IS_VALID,CREATE_TIME,CREATE_USER) VALUES (:ID,:DOC_ID,'ANNO',:DOC_NO,:CONTENT,1,SYSDATE,'GAGE')"
                           ,
                           ID = row[0],
                           DOC_ID = row[1],
                           DOC_NO = row[2],
                           CONTENT = row[3]
                           )
    cursor.execute("TRUNCATE TABLE TMU_TMEDMS.T_PARSER_PDF_DATA")
    cursor.execute("TRUNCATE TABLE TMU_TMEDMS.T_PARSER_PDF_PAGE_CONTEXT")
    cursor.close()
    connection.commit()

def checkFile():
    dict_file = {}
    for path in readFileList.resFileList(".xls"):
        # 导入需要读取Excel表格的路径
        data = xlrd.open_workbook(path)
        sheet = data.sheets()[0]
        num = 0
        for i in range(0, sheet.nrows):
            if sheet.cell_type(i, 0) in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK) and sheet.cell_type(i, 5) in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
               num += 1
        if num > 0:
            dict_file[path] = num
    for key in dict_file:
        print("注意文件：" + key + "  ,  需要补全空行：" + str(dict_file[key]))
    return dict_file

if __name__ == '__main__':
    dict = checkFile()
    input_str = ""
    while dict or input_str == "":
        input_str = input("检测到有待补全记录,是否先补全记录,再执行导入数据库？yes or no:\n")
        if str(input_str).upper() == "NO":
            insertData()
            analyze2Tab()
            break
        else:
            dict = checkFile()