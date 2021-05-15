#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @desc    : 对比接口excel

import time

import xlrd
import xlwt

from common import dir_config
from utils.HandleLogging import log


class DiffExcelFile():

    def __init__(self, wb_name="Excel_Workbook.xlsx", sheet_name="Sheet1"):
        #         创建工作簿对象
        self.workbook = xlwt.Workbook()  # encoding = 'ascii'本身就是默认值
#         实例属性
        self.wb_name = wb_name
        self.sheet_name = sheet_name
#         添加表单对象
        self.worksheet = self.workbook.add_sheet(self.sheet_name)

    def write_excel(self, row, col, content, style='pattern: pattern solid, fore_colour yellow; font: bold on'):
        #     设置表单样式
        style = xlwt.easyxf(style)
    #     写入表单
        # Apply the Style to the Cell
        self.worksheet.write(row, col, label=content, style=style)
    #     保存表单
        self.save_excel()

    def save_excel(self):
        self.workbook.save(self.wb_name)


xw = DiffExcelFile(wb_name=dir_config.data_path + "test124.xlsx")

# 往日志文件中追加内容函数#个人感觉这个很鸡肋，实际以日志输出就可以


def write_file(filename, content):
    '''
           写入文件，将对比不同的测试用例写入日志
    '''
    if not isinstance(content, str):
        content = str(content)

    with open(filename, 'a', encoding='utf-8') as file:  # 以追加方式打开日志文件
        time_now = time.strftime("%Y-%m-%d", time.localtime())  # 系统时间格式化
        file.write(time_now + ':变更的接口及参数==>' + content + '\n')  # 写入内容


def read_excel(file_path, sheet_name="Sheet1"):
    '''读取excel表格'''
    datas = []  # 储存xlsx文件的所有数据
    xlsx_file = {}  # 存储源xls文件
    wb = xlrd.open_workbook(file_path)  # 打开目标文件
#     sheet_num = len(wb.sheets())     #获取xlsx表单数量
    sheet_name_list = wb.sheet_names()  # 获取xlsx表单名字

    if sheet_name in sheet_name_list:
        sheet_name = wb.sheet_by_name(sheet_name)
        for rows in range(0, sheet_name.nrows):
            orign_list = sheet_name.row_values(rows)  # 源表i行数据
            xlsx_file[rows] = orign_list  # 源表写入字典
    else:
        log.info("{}子表名不存在{}文件中！".format(sheet_name, file_path))

    for row in range(1, len(xlsx_file)):
        data = dict(zip(xlsx_file[0], xlsx_file[row]))
        datas.append(data)

    return datas


def diff_excel(src_file, des_file, check="caseid,url,params"):
    '''对比文件的数据某个字段的值，默认sheet_name=Sheet1'''
    fail = 0  # 记录变更的数据
    res1 = read_excel(src_file)
    res2 = read_excel(des_file)

    lis1 = check.split(",")
    index = lis1[0]
    check1 = lis1[1]
    check2 = lis1[2]

    data = []
    for i in range(len(res2)):
        data.append([res2[i][check1], res2[i][check2]])

    datas = []
    for r1 in range(len(res1)):
        case = [res1[r1][check1], res1[r1][check2]]
        if case not in data:
            log.info("新增/变更数据：{}".format(case))
            fail += 1
            case_id = str(res1[r1][index])
            content = "".join([case_id, str(case)])
            datas.append(content)
            write_file(dir_config.log_path + "diff_data.log", content)

    for i in range(len(datas)):
        xw.write_excel(i + 1, 0, datas[i])