#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : swagger3.py
"""
Library import order: priority basic library \ third party library \ custom encapsulation
Format suggestion: import one line at a time
From import can be separated by commas after import
"""
import json
import os
import re

import jsonpath
import requests

from common.dir_config import testsuites_dir, xlsCase_file_path, testcases_dir, case_dir, \
    config_file_path
from common.get_file import original_data, change_data
from utils.handle_config import HandleConfig
from utils.handle_excel import Writexcel
from utils.handle_folder import HandleDirFile
from utils.handle_json import write_data
from utils.logger import log


# 创建可操作配置文件的对象
conf = HandleConfig(config_file_path)
# 创建可操作目录及文件的对象
handlefile = HandleDirFile()
# 创建可操作xlsx文件的对象
w = Writexcel(xlsCase_file_path)
api_list = []


def re_pattern(content, pattern=r'[^\*" /:?\\|<>]'):
    """
    Remove characters matching rules
    """
    text = re.findall(pattern, content, re.S)
    content = "".join(text)
    return content


def featch_body(path, rescomponents):
    """Get parameter path # / components / parameters / accept resolution"""
    data = rescomponents
    arr = path.split('/')
    ress = data
    for item in arr:
        ress = ress[item]
    return ress


class AnalysisSwaggerJson(object):
    """
    Swagger automatically generates tool classes for interface test cases, which are used to generate test cases in JSON format
    """

    def __init__(self, url):
        """
        Initialize the class and specify the address of the requested swagger interface
        """
        self.url = url    # 初始化解析swagger接口文档地址
        self.interface = {}    # json接口测试用例类型
        self.case_list = []    # 测试用例名称
        self.tags_list = []    # 测试模块标签

        # 定义测试用例集格式
        self.http_suite = {"config": {"name": "", "base_url": "", "variables": {}}, "testcases": []}
        # 定义测试用例格式
        self.http_testcase = {"name": "", "testcase": "", "variables": {}}

    def analysis_json_data(self, isDuplicated=False):
        """
        Main function for parsing JSON format data
        :return:
        """
        # swagger接口文档地址,其中运营后台的接口地址,请求分模块,全量或者其他服务菜单
        try:
            res = requests.get(self.url+"/v3/api-docs").json()
            write_data(res, '/swagger-api.json')
        except Exception as e:
            log.error('Error requesting swagger address The exceptions are as follows: {}'.format(e))
            raise e


        self.data = res['paths']    # 取接口地址返回的path数据,包括了请求的路径
        self.url = res['servers']    # 获取接口的根路径
        self.title = res['info']['title']    # 获取接口的标题
        self.http_suite['config']['name'] = self.title    # 在初始化用例集字典更新值
        self.http_suite['config']['base_url'] = self.url    # 全局url
        self.tags = jsonpath.jsonpath(res, '$..tags')

        # 追加模块名
        for tag_dict in self.tags:
            # 在开发不注意的时候会使用一些特殊符号，如空格、冒号、美元符、反斜杠
            tag_name = str(tag_dict).replace("['", "").replace("']", "")
            tag = re_pattern(tag_name)
            self.tags_list.append(tag)

        i = 0
        for tag in self.tags_list:
            # 丰富测试套件
            self.http_suite['testcases'].append({"name": "", "testcase": "", "variables": {}})
            self.http_suite['testcases'][i]['name'] = tag
            self.http_suite['testcases'][i]['testcase'] = 'testcases/' + tag + '.json'
            i += 1

        # 测试用例集目录不存在,则创建
        if not os.path.exists(testsuites_dir):
            os.makedirs(testsuites_dir)

        # 拼接用例套件路径
        testsuite_json_path = os.path.join(testsuites_dir, '{}_testsuites.json'.format(self.title))
        # 测试套件数据写入json
        write_data(self.http_suite, testsuite_json_path)

        # 解析用例参数
        if isinstance(self.data, dict):    # 判断接口返回的paths数据类型是否dict类型
            # 前面已经把接口返回的结果tags分别写入了tags_list空列表,再从json对应的tag往里面插入数据
            for tag in self.tags_list:
                # 测试用例json格式初始化
                self.http_case = {"config": {"name": "", "base_url": "", "variables": {}}, "teststeps": []}
                for key, value in self.data.items():
                    for method in list(value.keys()):
                        # 从初始数据解析，通过tag标识找到对应的api
                        params = value[method]
                        # 过滤，特殊符号替换成连接符
                        p_tag = params['tags'][0]
                        p_tag = re_pattern(p_tag)
                        # deprecated字段标识：接口是否被弃用，暂时无法判断，使用consumes偷换
                        if not 'deprecated' in value.keys():
                            if p_tag == tag:
                                self.http_case['config']['name'] = params['tags'][0]
                                self.http_case['config']['base_url'] = self.url
                                # 参数清洗，生成测试用例
                                case = self.wash_params(params, key, method, tag, res)
                                self.http_case['teststeps'].append(case)
                        else:
                            log.info(
                                'interface path: {}, if name: {}, is deprecated.'.format(key, params['operationId']))
                            break

                # testcases目录不存在则创建
                if not os.path.exists(testcases_dir):
                    os.makedirs(testcases_dir)
                # 拼接测试用例路径
                testcase_json_path = os.path.join(
                    testcases_dir, tag + '.json')
                # 生成json用例文件
                write_data(
                    self.http_case, testcase_json_path)

        else:
            log.error('解析接口数据异常！url 返回值 paths 中不是dict.')
            return 'error'

    def wash_params(self, params, api, method, tag, res):
        """
        Clean the data JSON and add each interface data to a dictionary
        :param params:
        :param params_key:
        :param method:
        :param key:
        :return:
        replace('false', 'False').replace('true', 'True').replace('null','None')
        """
        # 定义接口数据格式
        http_interface = {"name": "", "variables": {}, "request": {"url": "", "method": "", "headers": {}, "json": {}, "params": {}}, "validate": [], "output": []}
        # 测试用例的数据格式:
        http_api_testcase = {"name": "", "api": "", "variables": {}, "validate": [], "extract": [], "output": []}
        # 这里的问题需要具体来分析,开发有时概要使用其他符号分割///分割符号需要替换
        case_name = params['summary']    # .replace('/', '_').replace(" ", "_").replace(":", "_")
        case_name = re_pattern(case_name)
        # 用例名称
        http_interface['name'] = case_name
        http_api_testcase['name'] = case_name
        # 这是写入testcasejson下的名字,不是生成api的目录
        http_api_testcase['api'] = 'api/{}/{}.json'.format(tag, case_name)
        # 所有方法大写
        http_interface['request']['method'] = method.upper()
        # 这个是替换uri中的/get请求的拼接方式,有些是?参数=&参数拼接,需要另外解析
        http_interface['request']['url'] = api.replace('{', '$').replace('}', '')
        parameters = params.get('parameters')    # 未解析的请求参数
        print(parameters)
        requestBody = params.get('requestBody')    # 未解析的body
        responses = params.get('responses')    # 未解析的响应参数
        if not parameters:    # 确保参数字典存在
            parameters = {}

        # 解析接口文档《请求参数》
        for each in parameters:
            each = each['$ref']
            parameters = each.replace("#/", "")
            cont = featch_body(parameters, res)
            if cont.get('in') == 'header':
                name = cont.get('name')
                for key in cont.keys():
                    if 'example' in key:
                        http_interface['request']['headers'].update({name: cont[key]})
                    else:
                        if name == 'Authorization':
                            http_interface['request']['headers'].update({name: '$Authorization'})
                        else:
                            http_interface['request']['headers'].update({name: ''})
            if cont.get('in') == 'path':
                name = cont.get('name')
                for key in cont.keys():
                    if 'schema' in key:
                        http_interface['request']['params'].update({name: cont[key]})
        if not requestBody:    # 确保参数字典存在
            requestBody = {}
        else:
            # 解析接口文档《请求参数》
            requestBody = requestBody['$ref'].replace("#/", "")
            cont = featch_body(requestBody, res)
            if 'content' in cont:
                requestBody = requestBody + "/content"
                cont = featch_body(requestBody, res)
                schema = cont.get('application/x-www-form-urlencoded')
                properties = schema.get('schema')
                reqbody = properties.get('properties')
                http_interface['request']['json'] = reqbody

        for key, value in responses.items():
            schema = value.get('schema')
            if schema:
                ref = schema.get('$ref')
                if ref:
                    param_key = ref.split('/')[-1]
                    res = self.components[param_key]['properties']
                    i = 0
                    for k, v in res.items():
                        if 'example' in v.keys():
                            http_interface['validate'].append({"eq": []})
                            http_interface['validate'][i]['eq'].append('content.' + k)
                            http_interface['validate'][i]['eq'].append(v['example'])
                            http_api_testcase['validate'].append({"eq": []})
                            http_api_testcase['validate'][i]['eq'].append('content.' + k)
                            http_api_testcase['validate'][i]['eq'].append(v['example'])
                            i += 1
                else:
                    if len(http_interface['validate']) != 1:
                        http_interface['validate'].append({"eq": []})
            else:
                if len(http_interface['validate']) != 1:
                    http_interface['validate'].append({"eq": []})

        # 判断如果断言为空，则默认添加http状态断言
        if http_interface.get("validate"):
            http_interface.get("validate")[0].update({"eq": ["status_code", 200]})

        # 测试用例的请求参数为空字典，则删除这些key
        if http_interface['request']['json'] == {}:
            del http_interface['request']['json']
        if http_interface['request']['params'] == {}:
            del http_interface['request']['params']

        # 定义接口测试用例
        tags_path = os.path.join(case_dir, tag).replace(" ", "_")
        # 创建不存在的文件目录,递归创建
        if not os.path.exists(tags_path):
            os.makedirs(tags_path)

        # 拼接api用例路径
        json_path = os.path.join(tags_path, case_name + '.json')
        # testcases/写入数据
        write_data(http_interface, json_path)
        path = json_path
        orig_data = original_data(path)
        change_data(orig_data, path)

        return http_api_testcase

    def write_excel(self, url, filelist):
        """
        Convert the generated JSON format data into xlsx and write it to a file
        """
        li1 = url.split(":")
        host = li1[1].split("/")[2]
        host = "https://" + host
        # port = li1[2][:4]
        # uri = li1[2][4:]

        count = 1
        caseId = 0

        for file in filelist:
            caseId += 1
            count += 1
            # 获取接口测试用例的上级目录名称：组成name-tag的用例title
            inter_name = file.split("\\")[-2]
            with open(file, 'r+', encoding='utf8') as rdfile:
                text = json.load(rdfile)
                title = inter_name + '-' + text['name']
                method = text['request']['method'].upper()
                w.write(count, 1, "TestCase_" + str(caseId))
                w.write(count, 2, title)
                w.write(count, 4, method)
                w.write(count, 5, host)
                # w.write(count, 6, port)
                if 'json' in text['request'].keys():    # post请求的接口相关数据写入excel
                    url = text['request']['url']
                    params = text['request']['json']
                    w.write(count, 7, url)
                    w.write(count, 8, json.dumps(params))
                elif 'params' in text['request'].keys():    # get请求的接口参数写入
                    url = text['request']['url']
                    jsonp = str(text['request']['params'])
                    join_text = jsonp.replace("{", "").replace("}", "").replace(
                        ":", "=").replace("'", "").replace(",", "&").replace(" ", "")
                    # w.write(count, 7, uri + url)
                    w.write(count, 8, join_text)
                else:    # 将url中包含$符号的get请求的参数单独提取出来写入params
                    url = text['request']['url'].replace(
                        '{', '$').replace('}', '')
                    start_index = url.find("$")
                    url1 = url[:start_index]
                    params = url[start_index:]
                    w.write(count, 7, url1)
                    if "$" in params:
                        w.write(count, 8, params)
        # last save file
        w.save()


if __name__ == '__main__':
    url = conf.get_value("swaggerUrl", "baseSever_url")
    js = AnalysisSwaggerJson(url)
    js.analysis_json_data(isDuplicated=False)
    js.write_excel(url, handlefile.get_file_list(case_dir))
    w.xlsx_to_csv_pd()