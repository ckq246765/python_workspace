import json

import xlwt
from ConnectOracle import *
from ReadFileList import *

def fun():
    readFileList = ReadFileList()
    connectOracle = ConnectOracle(readFileList)
    # 创建写入文件
    workbook = xlwt.Workbook(encoding="ascii")
    # 创建写入sheet页
    worksheet = workbook.add_sheet("T_TMEDMS_TM_ANNO_FILES", cell_overwrite_ok=True)
    connection = connectOracle.getConnection("tmedms")
    cursor = connection.cursor()
    _result = cursor.execute("SELECT * FROM TMU_TMEDMS.T_TMEDMS_TM_ANN_FILES_AUX A WHERE A.CREATE_USER='GAGE'")
    num = 0
    for row in _result.fetchall():
        worksheet.write(num, 0, row[0])
        worksheet.write(num, 1, row[1])
        worksheet.write(num, 2, row[2])
        worksheet.write(num, 3, row[3])
        worksheet.write(num, 4, str(row[4].read()))
        worksheet.write(num, 5, row[5])
        worksheet.write(num, 6, row[6])
        worksheet.write(num, 7, row[7])
        worksheet.write(num, 8, row[8])
        worksheet.write(num, 9, row[9])
        worksheet.write(num, 10, row[10])
        num += 1
        if num % 1000 == 0:
            workbook.save("E:\桌面\恶意提示加注\新建文件夹\T_TMEDMS_TM_ANN_FILES_AUX"+str(num/1000)+".xls")
    workbook.save("E:\桌面\恶意提示加注\新建文件夹\T_TMEDMS_TM_ANN_FILES_AUX" + str(num / 1000) + ".xls")
    cursor.close()

    _result = cursor.execute("SELECT * FROM TMU_TMEDMS.T_TMEDMS_TM_ANNO_FILES A WHERE A.CREATE_USER='GAGE'")
    num = 0
    for row in _result.fetchall():
        worksheet.write(num, 0, row[0])
        worksheet.write(num, 1, row[1])
        worksheet.write(num, 2, row[2])
        worksheet.write(num, 3, row[3])
        worksheet.write(num, 4, row[4])
        worksheet.write(num, 5, row[5])
        worksheet.write(num, 6, row[6])
        worksheet.write(num, 7, row[7])
        worksheet.write(num, 8, row[8])
        worksheet.write(num, 9, str(row[9].read()))
        num += 1
        if num % 1000 == 0:
            workbook.save("E:\桌面\恶意提示加注\新建文件夹\T_TMEDMS_TM_ANNO_FILES"+str(num/1000)+".xls")
    workbook.save("E:\桌面\恶意提示加注\新建文件夹\T_TMEDMS_TM_ANNO_FILES" + str(num / 1000) + ".xls")
    cursor.close()

    connectOracle.releaseConnection("tmedms", connection)


if __name__ == '__main__':
    fun()