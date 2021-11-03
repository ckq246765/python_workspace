import xlrd
import xlwt

def excel_copy(dir_from, dir_to, sheet_name):
    '''从一个excel写入到另外一个excel'''
    wb = xlrd.open_workbook(dir_from)
    # 选择sheet页
    sheet1 = wb.sheet_by_index(0)
    # 打印每个sheet页的行数
    print("sheet1行数：%d" % sheet1.nrows)
    # 创建写入文件
    workbook = xlwt.Workbook(encoding="ascii")
    # # 创建写入sheet页
    worksheet = workbook.add_sheet(sheet_name)
    # 写入excel
    for i in range(0, sheet1.nrows):
        values_row1 = sheet1.row_values(i)
        print(values_row1)
        for s in range(len(values_row1)):
            worksheet.write(i, s, values_row1[s])

        val = values_row1[1].split("\\")
        for v in range(0, len(val)):
            worksheet.write(i, len(values_row1) + v, val[v])

    workbook.save(dir_to)


if __name__ == '__main__':
    print(len(("zcWrt.getRecName()" + "&#" + "zcWrt.getRecAddr()"
                + "&#" + "zcWrt.getRecZip()" + "&#" + "barCode" + "&#"
                + "zcWrt.getAppAgentId()" + "&#" + "zcWrt.getRegionalId()" + "&#&#" + "oppperList.get(0).getUniqueCode()" + "&#&#&#&#&#&#").split('&#')))