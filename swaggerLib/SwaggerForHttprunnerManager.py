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

from utils.handle_config import conf
from utils.handle_json import write_data
from utils.logger import log


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
        self.url = url    # Initialize and resolve swagger interface document address
        self.interface = {}    # JSON interface test case type
        self.case_list = []    # Test case name
        self.tags_list = []    # Test module label
        self.testcase_steps = {"tests":[]}
        # Define test case set format
        self.http_suite = {"config": {"name": "", "base_url": "", "variables": {}},
                           "testcases": []}
        # Define test case format
        self.http_testcase = {"name": "", "testcase": "", "variables": {}}

    def analysis_json_data(self):
        """
        Main function for parsing JSON format data
        :return:
        """
        # Swagger interface document address, including the interface address of the operation background, request sub module, full volume or other service menus
        host = self.url
        try:
            res = requests.get(host).json()
            write_data(res, 'swagger-api.json')
        except Exception as e:
            log.error('Error requesting swagger address The exceptions are as follows: {}'.format(e))
            raise e

        self.data = res['paths']    # Take the path data returned from the interface address, including the requested path
        self.basePath = res['basePath']    # Gets the root path of the interface
        # First, the swagger document is an IP address. If you use HTTPS protocol, you will make an error. Pay attention to the request protocol of the interface address
        self.url = 'http://' + res['host']
        self.title = res['info']['title']    # Gets the title of the interface
        self.http_suite['config']['name'] = self.title    # Update values in the initialization case set dictionary
        self.http_suite['config']['base_url'] = self.url    # GLOBAL url

        self.definitions = res['definitions']    # Body parameter
        
        # Append module name
        for tag_dict in res['tags']:
            # Friendly tips: when you don't pay attention to development, you will use some special symbols, such as space, colon, dollar sign and backslash
            tag_name = tag_dict.get("name")#.replace('/', '_').replace(" ", "_").replace(":", "_")
            tag = re_pattern(tag_name)
            self.tags_list.append(tag)

        i = 0
        for tag in self.tags_list:
            # Rich test suite
            self.http_suite['testcases'].append({"name": "", "testcase": "", "variables": {}})
            self.http_suite['testcases'][i]['name'] = tag
            self.http_suite['testcases'][i]['testcase'] = 'testcases/' + tag + '.json'
            i += 1

        # Parse case parameters
        if isinstance(self.data, dict):    # Judge whether the paths data type returned by the interface is dict type
            # Previously, the result tags returned by the interface have been written into tags respectively_ List empty list, \ 
            # and then insert data from the tag corresponding to JSON
            for tag in self.tags_list:
                # Test case JSON format initialization
                self.http_case = {"config": {"name": "", "base_url": "", "variables": {}}, "teststeps": []}
                for key, value in self.data.items():
                    for method in list(value.keys()):
                        # Analyze the initial data and find the corresponding API through tag identification
                        params = value[method]
                        # Filter, replace special symbols with connectors
                        p_tag = params['tags'][0]#.replace('/', '_').replace(" ", "_").replace(":", "_")
                        p_tag = re_pattern(p_tag)
                        # Identifier of the deprecated field: whether the interface is abandoned or not can not be determined temporarily. Use consumers to steal it
                        if not 'deprecated' in value.keys():
                            if p_tag == tag:
                                self.http_case['config'][
                                    'name'] = params['tags'][0]
                                self.http_case['config']['base_url'] = self.url
                                # Parameter cleaning and test case generation
                                self.wash_params(params, key, method, tag)
        
                        else:
                            log.info(
                                'interface path: {}, if name: {}, is deprecated.'.format(key, params['operationId']))
                            break


        else:
            log.error('Exception parsing interface data! The URL return value is not dict in paths.')
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
        # Define interface data format
        http_interface = {"name": "", "variables": {},
                          "request": {"url": "", "method": "", "headers": {}, "json": {}, "params": {}}, "validate": []}
        # Data format of test case:
        http_api_testcase = {"name": "", "api": "", "variables": {
        }, "validate": [], "extract": []}

        # The problems here need to be analyzed in detail. Sometimes the development outline uses other symbols to split / / the split symbols need to be replaced
        case_name = params['summary']#.replace('/', '_').replace(" ", "_").replace(":", "_")
        case_name=re_pattern(case_name)
        # Case name
        http_interface['name'] = case_name
        http_api_testcase['name'] = case_name
        # This is the name written under testcasejson, not the directory where the API is generated
        http_api_testcase['api'] = 'api/{}/{}.json'.format(tag, case_name)
        # All methods capitalize
        http_interface['request']['method'] = method.upper()
        # This is the splicing method of replacing the / get request in the URI. Some are? Parameter = &amp; parameter splicing, need additional parsing
        http_interface['request']['url'] = api.replace(
            '{', '$').replace('}', '')
        parameters = params.get('parameters')    # Unresolved request parameters
        responses = params.get('responses')    # Unresolved response parameters
        if not parameters:    # Add the parsed parameters to the test case dictionary
            parameters = {}
            
        # Add the parsed parameters to the test case dictionary
        for each in parameters:
            if each.get('in') == 'body':    # Body and query will not appear at the same time
                schema = each.get('schema')
                if schema:
                    ref = schema.get('$ref')
                    if ref:
                        # This URI is split and the number of / backslashes is taken according to the actual situation
                        param_key = ref.split('/', 2)[-1]
                        param = self.definitions[param_key]['properties']
                        for key, value in param.items():
                            if 'example' in value.keys():
                                http_interface['request']['json'].update(
                                    {key: value['example']})
                            else:
                                http_interface['request'][
                                    'json'].update({key: ''})
            
            # It is actually the request method or the format of the request parameter
            elif each.get('in') == 'query':
                name = each.get('name')
                for key in each.keys():
                    if not 'example' in key:    # Take the inverse, and write the parameters in query into the JSON test case
                        http_interface['request'][
                            'params'].update({name: each[key]})
        
        # Parsing interface document request parameters
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
                                
        # Resolve interface document response parameters
        for key, value in responses.items():
            schema = value.get('schema')
            if schema:
                ref = schema.get('$ref')
                if ref:
                    param_key = ref.split('/',2)[-1]
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
        
        # Judge that if the assertion is empty, the HTTP status assertion will be added by default
        if http_interface.get("validate"):
            http_interface.get("validate")[0].update({"eq":["status_code", 200]})
        
        # If the request parameter of the test case is an empty dictionary, delete these keys
        if http_interface['request']['json'] == {}:
            del http_interface['request']['json']
        if http_interface['request']['params'] == {}:
            del http_interface['request']['params']

        # Write a method here to put all http_ Interface writes a test list set: testcases = {"tests": [{}, {}]}; {} is HTTP one by one_ interface
        self.testcase_steps.get("tests").append(http_interface)
        with open("httprunnerManager_api.json", "w+", encoding="utf8") as pf:
            pf.write(json.dumps(self.testcase_steps, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    url = conf.get_value("swaggerUrl", "baseSever_url")
    js = AnalysisSwaggerJson(url)
    js.analysis_json_data(isDuplicated=False)