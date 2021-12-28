#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : SwaggerForHttprunnerManager.py
"""
Library import order: priority basic library \ third party library \ custom encapsulation
Format suggestion: import one line at a time
From import can be separated by commas after import
"""
import re
import json

import requests

from utils.handle_config import HandleConfig
from utils.handle_json import write_data
from utils.logger import log
from common.dir_config import config_dir


# 创建可操作配置文件的对象
conf = HandleConfig(config_dir + "\config.ini")

def re_pattern(content,pattern=r'[^\*" /:?\\|<>]'):
    """
    Remove characters matching rules
    """
    text=re.findall(pattern, content, re.S)
    content="".join(text)
    return content


class AnalysisSwaggerJson(object):
    """
    Swagger automatically generates tool classes for interface test cases to generate test cases in JSON format;
    The current script is suitable for generating JSON files that conform to the httprunnermanager project to facilitate batch import.
    """

    def __init__(self, url):
        """
        Initialize the class and specify the address of the requested swagger interface
        """
        self.url = url    # 初始化解析swagger接口文档地址
        self.interface = {}    # json接口测试用例类型
        self.case_list = []    # 测试用例名称
        self.tags_list = []    # 测试模块标签
        self.testcase_steps = {"tests":[]}
        # 定义测试用例集格式
        self.http_suite = {"config": {"name": "", "base_url": "", "variables": {}},
                           "testcases": []}
        # 定义测试用例格式
        self.http_testcase = {"name": "", "testcase": "", "variables": {}}

    def analysis_json_data(self, isDuplicated=False):
        """
        Main function for parsing JSON format data
        :return:
        """
        # swagger接口文档地址,其中运营后台的接口地址,请求分模块,全量或者其他服务菜单
        host = self.url + '/v2/api-docs?group=全量接口' if "9527" in self.url else self.url + '/v2/api-docs'
        try:
            res = requests.get(host).json()
            write_data(res, 'swagger-api.json')
        except Exception as e:
            log.error('请求swagger地址错误. 异常如下: {}'.format(e))
            raise e

        # 生成完整的json测试用例之后,开始备份接口数据 ,以备作为接口变更的依据
        # if isDuplicated:
        #     # 备份文件,如果不存在备份目录则备份,否则的实现方案在其他方法内
        #     if not os.path.exists(dir_config.back_path):
        #         handlefile.copy_dir(dir_config.case_path, dir_config.back_path)

        self.data = res['paths']    # 取接口地址返回的path数据,包括了请求的路径
        self.basePath = res['basePath']    # 获取接口的根路径
        # 第一错，swagger文档是ip地址，使用https协议会错误,注意接口地址的请求协议
        self.url = 'http://' + res['host']
        self.title = res['info']['title']    # 获取接口的标题
        self.http_suite['config']['name'] = self.title    # 在初始化用例集字典更新值
        self.http_suite['config']['base_url'] = self.url    # 全局url

        self.definitions = res['definitions']    # body参数
        
        # 追加模块名
        for tag_dict in res['tags']:
            # 友情提示，在开发不注意的时候会使用一些特殊符号，如空格、冒号、美元符、反斜杠
            tag_name = tag_dict.get("name")#.replace('/', '_').replace(" ", "_").replace(":", "_")
            tag = re_pattern(tag_name)
            self.tags_list.append(tag)

        i = 0
        for tag in self.tags_list:
            # 丰富测试套件
            self.http_suite['testcases'].append({"name": "", "testcase": "", "variables": {}})
            self.http_suite['testcases'][i]['name'] = tag
            self.http_suite['testcases'][i]['testcase'] = 'testcases/' + tag + '.json'
            i += 1

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
                        p_tag = params['tags'][0]#.replace('/', '_').replace(" ", "_").replace(":", "_")
                        p_tag = re_pattern(p_tag)
                        # deprecated字段标识：接口是否被弃用，暂时无法判断，使用consumes偷换
                        if not 'deprecated' in value.keys():
                            if p_tag == tag:
                                self.http_case['config'][
                                    'name'] = params['tags'][0]
                                self.http_case['config']['base_url'] = self.url
                                # 参数清洗，生成测试用例
                                self.wash_params(params, key, method, tag)
        
                        else:
                            log.info(
                                'interface path: {}, if name: {}, is deprecated.'.format(key, params['operationId']))
                            break


        else:
            log.error('解析接口数据异常！url 返回值 paths 中不是dict.')
            return 'error'

    def wash_params(self, params, api, method, tag):
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
        http_interface = {"name": "", "variables": {},
                          "request": {"url": "", "method": "", "headers": {}, "json": {}, "params": {}}, "validate": []}
        # 测试用例的数据格式:
        http_api_testcase = {"name": "", "api": "", "variables": {
        }, "validate": [], "extract": []}

        # 这里的问题需要具体来分析,开发有时概要使用其他符号分割///分割符号需要替换
        case_name = params['summary']#.replace('/', '_').replace(" ", "_").replace(":", "_")
        case_name=re_pattern(case_name)
        # 用例名称
        http_interface['name'] = case_name
        http_api_testcase['name'] = case_name
        # 这是写入testcasejson下的名字,不是生成api的目录
        http_api_testcase['api'] = 'api/{}/{}.json'.format(tag, case_name)
        # 所有方法大写
        http_interface['request']['method'] = method.upper()
        # 这个是替换uri中的/get请求的拼接方式,有些是?参数=&参数拼接,需要另外解析
        http_interface['request']['url'] = api.replace(
            '{', '$').replace('}', '')
        parameters = params.get('parameters')    # 未解析的请求参数
        responses = params.get('responses')    # 未解析的响应参数
        if not parameters:    # 确保参数字典存在
            parameters = {}
            
        # 给测试用例字典,加入解析出来的参数
        for each in parameters:
            if each.get('in') == 'body':    # body 和 query 不会同时出现
                schema = each.get('schema')
                if schema:
                    ref = schema.get('$ref')
                    if ref:
                        # 这个uri拆分，根据实际情况来取第几个/反斜杠
                        param_key = ref.split('/', 2)[-1]
                        param = self.definitions[param_key]['properties']
                        for key, value in param.items():
                            if 'example' in value.keys():
                                http_interface['request']['json'].update(
                                    {key: value['example']})
                            else:
                                http_interface['request'][
                                    'json'].update({key: ''})
            
            # 实际是请求方法或者是请求参数的格式
            elif each.get('in') == 'query':
                name = each.get('name')
                for key in each.keys():
                    if not 'example' in key:    # 取反，要把在query的参数写入json测试用例
                        http_interface['request'][
                            'params'].update({name: each[key]})
        
        # 解析接口文档请求参数
        for each in parameters:
            if each.get('in') == 'header':
                name = each.get('name')
                for key in each.keys():
                    if 'example' in key:
                        http_interface['request'][
                            'headers'].update({name: each[key]})
                    else:
                        if name == 'token':
                            http_interface['request'][
                                'headers'].update({name: '$token'})
                        else:
                            http_interface['request'][
                                'headers'].update({name: ''})
                                
        # 解析接口文档响应参数
        for key, value in responses.items():
            schema = value.get('schema')
            if schema:
                ref = schema.get('$ref')
                if ref:
                    param_key = ref.split('/')[-1]
                    res = self.definitions[param_key]['properties']
                    i = 0
                    for k, v in res.items():
                        if 'example' in v.keys():
                            http_interface['validate'].append({"eq": []})
                            http_interface['validate'][i][
                                'eq'].append('content.' + k)
                            http_interface['validate'][i][
                                'eq'].append(v['example'])
                            http_api_testcase['validate'].append({"eq": []})
                            http_api_testcase['validate'][i][
                                'eq'].append('content.' + k)
                            http_api_testcase['validate'][
                                i]['eq'].append(v['example'])
                            i += 1
                else:
                    if len(http_interface['validate']) != 1:
                        http_interface['validate'].append({"eq": []})
            else:
                if len(http_interface['validate']) != 1:
                    http_interface['validate'].append({"eq": []})
        
        # 判断如果断言为空，则默认添加http状态断言
        if http_interface.get("validate"):
            http_interface.get("validate")[0].update({"eq":["status_code", 200]})
        
        # 测试用例的请求参数为空字典，则删除这些key
        if http_interface['request']['json'] == {}:
            del http_interface['request']['json']
        if http_interface['request']['params'] == {}:
            del http_interface['request']['params']

        # 在这里写一个方法将所有http_interface写入一个tests列表集：testcases={"tests":[{},{}]};{}就是一个个的http_interface
        self.testcase_steps.get("tests").append(http_interface)
        with open("httprunnerManager_api.json", "w+", encoding="utf8") as pf:
            pf.write(json.dumps(self.testcase_steps, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    url = conf.get_value("swaggerUrl", "baseSever_url")
    js = AnalysisSwaggerJson(url)
    js.analysis_json_data(isDuplicated=False)