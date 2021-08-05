#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @desc    : compare excel

import time

from common import dir_config
from utils.logger import log
import xlrd
import xlwt


class DiffExcelFile():
    """
    It is used to compare the contents of two files before and after excel and generate HTML report
    """

    def __init__(self, wb_name="Excel_Workbook.xlsx", sheet_name="Sheet1"):
        # Create workbook object
        self.workbook = xlwt.Workbook()  # encoding = 'ascii' default
        # Instance properties        
        self.wb_name = wb_name
        self.sheet_name = sheet_name
        # Add form object
        self.worksheet = self.workbook.add_sheet(self.sheet_name)

    def write_excel(self, row, col, content, style='pattern: pattern solid, fore_colour yellow; font: bold on'):
        # Set form style
        style = xlwt.easyxf(style)
        # Write form
        # Apply the Style to the Cell
        self.worksheet.write(row, col, label=content, style=style)
        # Save form
        self.save_excel()

    def save_excel(self):
        self.workbook.save(self.wb_name)


# The function of adding content to the log file # personally feels that this is a chicken rib. In fact, it can be output as a log


def write_file(filename, content):
    """
           Write the file and write the comparison of different test cases to the log
    """
    if not isinstance(content, str):
        content = str(content)

    with open(filename, 'a', encoding='utf-8') as file:  # Open log file in append modes
        time_now = time.strftime("%Y-%m-%d", time.localtime())  # System time formatting
        file.write(time_now + ':Changed interfaces and parameters==>' + content + '\n')  # Write content


def read_excel(file_path, sheet_name="Sheet1"):
    """Read excel table"""
    datas = []  # Store all data of xlsx file
    xlsx_file = {}  # Store source XLS files
    wb = xlrd.open_workbook(file_path)  # open the target file
    #     sheet_num = len(wb.sheets())     #Get xlsx number of forms
    sheet_name_list = wb.sheet_names()  # Get xlsx form name

    if sheet_name in sheet_name_list:
        sheet_name = wb.sheet_by_name(sheet_name)
        for rows in range(0, sheet_name.nrows):
            orign_list = sheet_name.row_values(rows)  # Source table I row data
            xlsx_file[rows] = orign_list  # Source table write dictionary
    else:
        log.info("{}The child table name does not exist in the {} file！".format(sheet_name, file_path))

    for row in range(1, len(xlsx_file)):
        data = dict(zip(xlsx_file[0], xlsx_file[row]))
        datas.append(data)

    return datas


def diff_excel(src_file, des_file, check="caseid,url,params"):
    """The value of a field in the data of the reference file，sheet_name default Sheet1"""
    fail = 0  # Record changed data
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
            log.info("New / changed data：{}".format(case))
            fail += 1
            case_id = str(res1[r1][index])
            content = "".join([case_id, str(case)])
            datas.append(content)
            write_file(dir_config.log_dir + "diff_data.log", content)

    for i in range(len(datas)):
        DiffExcelFile.write_excel(i + 1, 0, datas[i])