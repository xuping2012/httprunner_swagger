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

from common.get_file import original_data, change_data
from utils.handle_config import  conf
from utils.handle_excel import  w
from utils.handle_folder import  handlefile
from utils.handle_json import write_data
from utils.logger import log
from common.dir_config import TESTSUITEDIR, TESTCASEDIR, APIDIR



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
        # Initialize and resolve swagger interface document address
        self.url = url    
        # JSON interface test case type
        self.interface = {}    
        # Test case name
        self.case_list = []    
        # Test module label
        self.tags_list = []    

        # Define test case set format
        self.http_suite = {"config": {"name": "", "base_url": "", "variables": {}}, "testcases": []}
        # Define test case format
        self.http_testcase = {"name": "", "testcase": "", "variables": {}}

    def analysis_json_data(self, isDuplicated=False):
        """
        Main function for parsing JSON format data
        :return:
        """
        # Swagger interface document address, including the interface address of the operation background, request sub module, full volume or other service menus
        try:
            res = requests.get(self.url).json()
            write_data(res, 'swagger-api.json')
        except Exception as e:
            log.error('Error requesting swagger address The exceptions are as follows: {}'.format(e))
            raise e


        self.data = res['paths']    # Take the path data returned from the interface address, including the requested path
        self.url = res['servers']    # Gets the root path of the interface
        self.title = res['info']['title']    # Gets the title of the interface
        self.http_suite['config']['name'] = self.title    # Update values in the initialization case set dictionary
        self.http_suite['config']['base_url'] = self.url    # Global  url
        self.tags = jsonpath.jsonpath(res, '$..tags')

        # Append module name
        for tag_dict in self.tags:
            # When you don't pay attention to development, you will use some special symbols, such as space, colon, dollar sign and backslash
            tag_name = str(tag_dict).replace("['", "").replace("']", "")
            tag = re_pattern(tag_name)
            self.tags_list.append(tag)

        i = 0
        for tag in self.tags_list:
            # Rich test suite
            self.http_suite['testcases'].append({"name": "", "testcase": "", "variables": {}})
            self.http_suite['testcases'][i]['name'] = tag
            self.http_suite['testcases'][i]['testcase'] = 'testcases/' + tag + '.json'
            i += 1

        # If the test case set directory does not exist, it is created
        if not os.path.exists(TESTSUITEDIR):
            os.makedirs(TESTSUITEDIR)
        # testcases Create if directory does not exist
        if not os.path.exists(TESTCASEDIR):
            os.makedirs(TESTCASEDIR)
            
        # Splice case suite path
        testsuite_json_path = os.path.join(TESTSUITEDIR, '{}_testsuites.json'.format(self.title))
        # Test suite data writing json
        write_data(self.http_suite, testsuite_json_path)

        # Parse case parameters
        if isinstance(self.data, dict):    # Judge whether the paths data type returned by the interface is dict type
            # Previously, the result tags returned by the interface have been written into tags respectively_ List empty list, and then insert data from the tag corresponding to JSON
            for tag in self.tags_list:
                # Test case JSON format initialization
                self.http_case = {"config": {"name": "", "base_url": "", "variables": {}}, "teststeps": []}
                for key, value in self.data.items():
                    for method in list(value.keys()):
                        # Analyze the initial data and find the corresponding API through tag identification
                        params = value[method]
                        # Filter, replace special symbols with connectors
                        p_tag = params['tags'][0]
                        p_tag = re_pattern(p_tag)
                        # Identifier of the deprecated field: whether the interface is abandoned or not can not be determined temporarily. Use consumers to steal it
                        if not 'deprecated' in value.keys():
                            if p_tag == tag:
                                self.http_case['config']['name'] = params['tags'][0]
                                self.http_case['config']['base_url'] = self.url
                                # Parameter cleaning and test case generation
                                case = self.wash_params(params, key, method, tag, res)
                                self.http_case['teststeps'].append(case)
                        else:
                            log.info(
                                'interface path: {}, if name: {}, is deprecated.'.format(key, params['operationId']))
                            break

                # Splicing test case path
                testcase_json_path = os.path.join(
                    TESTCASEDIR, tag + '.json')
                # Generate JSON use case file
                write_data(self.http_case, testcase_json_path)

        else:
            log.error('Exception parsing interface data! The URL return value is not dict in paths.')
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
        # Define interface data format
        http_interface = {"name": "", "variables": {}, "request": {"url": "", "method": "", "headers": {}, "json": {}, "params": {}}, "validate": [], "output": []}
        # Data format of test case:
        http_api_testcase = {"name": "", "api": "", "variables": {}, "validate": [], "extract": [], "output": []}
        # The problems here need to be analyzed in detail. Sometimes the development outline uses other symbols to split / / the split symbols need to be replaced
        case_name = params['summary']    # .replace('/', '_').replace(" ", "_").replace(":", "_")
        case_name = re_pattern(case_name)
        # Case name
        http_interface['name'] = case_name
        http_api_testcase['name'] = case_name
        # This is the name written under testcasejson, not the directory where the API is generated
        http_api_testcase['api'] = 'api/{}/{}.json'.format(tag, case_name)
        # All methods capitalize
        http_interface['request']['method'] = method.upper()
        # This is the splicing method of replacing the / get request in the URI. Some are? Parameter = &amp; parameter splicing, need additional parsing
        http_interface['request']['url'] = api.replace('{', '$').replace('}', '')
        parameters = params.get('parameters')    # Unresolved request parameters
        requestBody = params.get('requestBody')    # Unresolved body
        responses = params.get('responses')    # Unresolved response parameters
        if not parameters:    # Ensure that the parameter dictionary exists
            parameters = {}

        # Parsing interface document request header parameters
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
        if not requestBody:    # Ensure that the parameter dictionary exists
            requestBody = {}
        else:
            # Parsing interface document request parameters
            requestBody = requestBody['$ref'].replace("#/", "")
            cont = featch_body(requestBody, res)
            if 'content' in cont:
                requestBody = requestBody + "/content"
                cont = featch_body(requestBody, res)
                schema = cont.get('application/x-www-form-urlencoded')
                properties = schema.get('schema')
                reqbody = properties.get('properties')
                http_interface['request']['json'] = reqbody

        # Analyze interface document response parameters
        for key, value in responses.items():
            schema = value.get('schema')
            if schema:
                ref = schema.get('$ref')
                if ref:
                    # Note the document specification. The directory level follows: # / definitions / response name
                    param_key = ref.split('/',2)[-1]
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

        # Judge that if the assertion is empty, the HTTP status assertion will be added by default
        if http_interface.get("validate"):
            http_interface.get("validate")[0].update({"eq": ["status_code", 200]})

        # If the request parameter of the test case is an empty dictionary, delete these keys
        if http_interface['request']['json'] == {}:
            del http_interface['request']['json']
        if http_interface['request']['params'] == {}:
            del http_interface['request']['params']

        # Define interface test cases
        tags_path = os.path.join(APIDIR, tag).replace(" ", "_")
        # Create a nonexistent file directory and create it recursively
        if not os.path.exists(tags_path):
            os.makedirs(tags_path)

        # Splicing API use case path
        json_path = os.path.join(tags_path, case_name + '.json')
        # testcases/write data
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
        host = li1[1].replace("/", "")
        port = li1[2][:4]
        uri = li1[2][4:]

        count = 1
        caseId = 0

        for file in filelist:
            caseId += 1
            count += 1
            # Get the name of the parent directory of the interface test case: the case title of the name tag
            inter_name = file.split("\\")[-2]
            with open(file, 'r+', encoding='utf8') as rdfile:
                text = json.load(rdfile)
                title = inter_name + '-' + text['name']
                method = text['request']['method'].upper()
                w.write(count, 1, "TestCase_" + str(caseId))
                w.write(count, 2, title)
                w.write(count, 4, method)
                w.write(count, 5, host)
                w.write(count, 6, port)
                if 'json' in text['request'].keys():    # The interface related data requested by post is written into excel
                    url = text['request']['url']
                    params = text['request']['json']
                    w.write(count, 7, url)
                    w.write(count, 8, json.dumps(params))
                elif 'params' in text['request'].keys():    # Interface parameter write of get request
                    url = text['request']['url']
                    jsonp = str(text['request']['params'])
                    join_text = jsonp.replace("{", "").replace("}", "").replace(
                        ":", "=").replace("'", "").replace(",", "&").replace(" ", "")
                    w.write(count, 7, uri + url)
                    w.write(count, 8, join_text)
                else:    # Extract the parameters of the get request containing the $symbol in the URL separately and write them to params
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
    js.write_excel(url, handlefile.get_file_list(APIDIR))
    w.xlsx_to_csv_pd()