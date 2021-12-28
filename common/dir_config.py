#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : dir_config.py
import os
import time


# py文件当前目录路径
baseth = os.path.abspath(os.path.dirname(__file__))
# 备份上一次的excel测试用例文件，以时间区分
now = time.strftime('%Y-%m-%d_%H-%m')

# 报告路径 
# 在工程路径下搭载HTTPRUNNER2.x版本执行测试用例，会在当前目录生成reports文件夹
report_dir = baseth.replace("common", "reports")    

# 配置文件中心：脚本读取配置路径
config_dir = baseth.replace("common", "properties\\")   
# 日志目录：日志的配置信息
log_dir = baseth.replace("common", "logs\\")
   
# 解析接口文档之后存放的目录
swagger_dir = baseth.replace("common", "swagger")    
# 备份路径
back_dir = swagger_dir.replace("swagger", "swaggerbak")    
# 初始化测试用例套件目录
testsuites_dir = os.path.join(swagger_dir + "\\testsuites")
# 初始化测试用例目录
testcases_dir = os.path.join(swagger_dir + "\\testcases")
# 生成的新测试用例api目录
case_dir = os.path.join(swagger_dir + "\\api")
# swagger生成xlsx测试用例文件
xlsCase_file_path = os.path.join(swagger_dir + "\\Api_TestCases.xlsx")
# 备份文件名称
bakCase_file_path = os.path.join(swagger_dir + "\\Api_TestCases_bak_{}.xlsx".format(now))
# 目录list
dir_lis = [report_dir, config_dir, log_dir, swagger_dir, back_dir]

# csv文件地址
csv_file_path = os.path.join(swagger_dir + "\\Api_TestCases.csv")
for dir_path in dir_lis: # 文件夹如果不存在则创建
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

if __name__ == '__main__':
    print(baseth)