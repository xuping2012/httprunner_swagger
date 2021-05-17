# -*- coding: utf-8 -*-
import os

baseth = os.path.abspath(os.path.dirname(__file__))

# 工程根目录下的文件夹
report_dir = baseth.replace("common", "reports")  # 报告路径
config_dir = baseth.replace("common", "properties\\")  # 配置文件中心
log_dir = baseth.replace("common", "logs\\")  # 日志目录
swagger_dir = baseth.replace("common", "swagger")

back_dir=swagger_dir.replace("swagger","swaggerbak")
# 初始化测试用例集合的目录
testsuites_dir = os.path.join(swagger_dir + "\\testsuites")
testcases_dir = os.path.join(swagger_dir + "\\testcases")
# 生成的新测试用例目录
case_dir = os.path.join(swagger_dir + "\\api")

# swagger生成xlsx测试用例目录
xlsCase_file_path = os.path.join(swagger_dir + "\\Api_TestCases.xlsx")
bakCase_file_path = os.path.join(swagger_dir + "\\Api_TestCases_bak.xlsx")

if __name__ == '__main__':
    if not os.path.exists(case_dir):
        os.makedirs(case_dir)
    else:
        print(case_dir)
