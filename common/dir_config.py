# -*- coding: utf-8 -*-
import os
import time

baseth = os.path.abspath(os.path.dirname(__file__))

# 工程根目录下的文件夹
report_dir = baseth.replace("common", "reports")    # 报告路径
config_dir = baseth.replace("common", "properties\\")    # 配置文件中心
log_dir = baseth.replace("common", "logs\\")    # 日志目录
swagger_dir = baseth.replace("common", "swagger")    # 解析接口文档之后存放的目录
back_dir = swagger_dir.replace("swagger", "swaggerbak")    # 备份路径

# 初始化测试用例套件目录
testsuites_dir = os.path.join(swagger_dir + "\\testsuites")
# 初始化测试用例目录
testcases_dir = os.path.join(swagger_dir + "\\testcases")
# 生成的新测试用例api目录
case_dir = os.path.join(swagger_dir + "\\api")

# swagger生成xlsx测试用例文件
xlsCase_file_path = os.path.join(swagger_dir + "\\Api_TestCases.xlsx")
# 备份上一次的excel测试用例文件，以时间区分
now = time.strftime('%Y-%m-%d_%H-%m')
bakCase_file_path = os.path.join(swagger_dir + "\\Api_TestCases_bak_{}.xlsx".format(now))

dir_lis = [report_dir, config_dir, log_dir, swagger_dir, back_dir]

csv_file_path=os.path.join(swagger_dir + "\\Api_TestCases.csv")

for dir_path in dir_lis:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)