# -*- coding: utf-8 -*-
import os

baseth = os.path.abspath(os.path.dirname(__file__))

report_path = os.path.join(baseth + "\\reports\\")  # 报告路径
config_path = os.path.join(baseth + "\\properties\\")  # 配置文件中心
log_path = os.path.join(baseth + "\\logs\\")  # 日志目录

# 初始化测试用例集合的目录
testsuites_path = os.path.join(baseth + "\\swagger\\testsuites\\")
testcases_path = os.path.join(baseth + "\\swagger\\testcases\\")
# 测试用例生成的新旧目录
oldCase_path = os.path.join(baseth + '\\CasesGenerator\\data_old\\')
newCase_path = os.path.join(
    baseth + '\\CasesGenerator\\data_new' + '\\demo_api.xlsx')
oldJson_path = os.path.join(baseth + '\\CasesGenerator\\data_old\\')
newJson_path = os.path.join(baseth + '\\CasesGenerator\\data_new\\')

# 生成的新测试用例目录
case_path = os.path.join(baseth + "\\swagger\\baseapi\\")
# case_filename=os.path.join(baseth+"\\CasesGenerator\\")
# 备份的测试用例目录
back_path = os.path.join(baseth + "\\swagger\\baseback\\")
# swagger生成xlsx测试用例目录
xlsCase_path = os.path.join(baseth + "\\swagger\\Api_TestCases.xlsx")
xlsback_path = os.path.join(
    baseth + "\\swagger\\xlsxbak\\Api_TestCases_bak.xlsx")
