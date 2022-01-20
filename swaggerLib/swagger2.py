#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : swagger2.py
"""
Library import order: priority basic library \ third party library \ custom encapsulation
Format suggestion: import one line at a time
From import can be separated by commas after import
"""
import json
import os
import re

import requests

from common.dir_config import APIDIR, SWAGGERDIR, BACKUPDIR, TESTSUITEDIR, \
    TESTCASEDIR
from utils.handle_config import conf
from utils.handle_excel import w
from utils.handle_folder import handlefile
from utils.handle_json import write_data
from utils.logger import log


def re_pattern(content, pattern=r'[^\*" /:?\\|<>]'):
    """
    Remove characters matching rules
    """
    text = re.findall(pattern, content, re.S)
    content = "".join(text)
    return content

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
        host = self.url
        try:
            res = requests.get(host).json()
            write_data(res, os.path.join(SWAGGERDIR, 'swagger-api.json'))
        except Exception as e:
            log.error('Error requesting swagger address The exceptions are as follows: {}'.format(e))
            raise e
        

        # After generating the complete JSON test case, start to back up the interface data as the basis for interface change
        if isDuplicated:
            # Backup files. If there is no backup directory, backup them. Otherwise, the implementation scheme is in other methods
            if not os.path.exists(BACKUPDIR):
                handlefile.copy_dir(SWAGGERDIR, BACKUPDIR)

        self.data = res['paths']    # Take the path data returned from the interface address, including the requested path
        self.basePath = res['basePath']    # Gets the root path of the interface
        # First, the swagger document is an IP address. If you use HTTPS protocol, you will make an error. Pay attention to the request protocol of the interface address
        self.url = 'http://' + res['host']
        self.title = res['info']['title']    # Gets the title of the interface
        self.http_suite['config']['name'] = self.title    # Update values in the initialization case set dictionary
        self.http_suite['config']['base_url'] = self.url    # Global URL

        self.definitions = res['definitions']    # Body parameter
        
        # Append module name
        for tag_dict in res['tags']:
            # Friendly tips: when you don't pay attention to development, you will use some special symbols, such as space, colon, dollar sign and backslash
            tag_name = tag_dict.get("name")    # .replace('/', '_').replace(" ", "_").replace(":", "_")
            tag_name = re_pattern(tag_name)
            self.tags_list.append(tag_name)

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
        # Create if the testcases directory does not exist
        if not os.path.exists(TESTCASEDIR):
            os.makedirs(TESTCASEDIR)
            
        # Splice case suite path
        testsuite_json_path = os.path.join(TESTSUITEDIR, '{}_testsuites.json'.format(self.title))
        # Write test suite data to JSON
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
                        # Analyze the initial data, find the corresponding filter through tag identification, and replace the special symbol with the API of connector
                        p_tag = params['tags'][0]    # .replace('/', '_').replace(" ", "_").replace(":", "_")
                        p_tag = re_pattern(p_tag)
                        # Identifier of the deprecated field: whether the interface is abandoned or not can not be determined temporarily. Use consumers to steal it
                        if not 'deprecated' in value.keys():
                            if p_tag == tag:
                                self.http_case['config']['name'] = params['tags'][0]
                                self.http_case['config']['base_url'] = self.url
                                # Parameter cleaning and test case generation
                                case = self.wash_params(params, key, method, tag)
                                self.http_case['teststeps'].append(case)
                        else:
                            log.info('interface path: {}, if name: {}, is deprecated.'.format(key, params['operationId']))
                            break


                # Splicing test case path
                testcase_json_path = os.path.join(TESTCASEDIR, tag + '.json')
                # Generate JSON use case file
                write_data(self.http_case, testcase_json_path)

        else:
            log.error('Exception parsing interface data! The URL return value is not dict. In paths')
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
        responses = params.get('responses')    # Unresolved response parameters
        if not parameters:    # Ensure that the parameter dictionary exists
            parameters = {}
            
        # Parsing interface document request parameters
        for each in parameters:
            if each.get('in') == 'body':    # Body and query will not appear at the same time
                schema = each.get('schema')
                if schema:
                    ref = schema.get('$ref')
                    if ref:
                        # This URI is split and the number of / backslashes is taken according to the actual situation
                        param_key = ref.split('/', 2)[-1]
                        param = self.definitions[param_key].get('properties')
                        # There may be an error that the key does not exist. Use the get method of dict, otherwise return none
                        if param:
                            for key, value in param.items():
                                if 'example' in value.keys():
                                    http_interface['request']['json'].update({key: value['example']})
                                else:
                                    http_interface['request']['json'].update({key: ''})
            
            # It is actually the request method or the format of the request parameter
            elif each.get('in') == 'query':
                name = each.get('name')
                for key in each.keys():
                    if not 'example' in key:    # Take the inverse, and write the parameters in query into the JSON test case
                        http_interface['request']['params'].update({name: each[key]})
        
        # Parsing interface document request header parameters
        for each in parameters:
            if each.get('in') == 'header':
                name = each.get('name')
                for key in each.keys():
                    if 'example' in key:
                        http_interface['request']['headers'].update({name: each[key]})
                    else:
                        if name == 'token':
                            http_interface['request']['headers'].update({name: '$token'})
                        else:
                            http_interface['request']['headers'].update({name: ''})
                                
        # Analyze interface document response parameters
        for key, value in responses.items():
            schema = value.get('schema')
            if schema:
                ref = schema.get('$ref')
                if ref:
                    # Note the document specification. The directory level follows: # / definitions / response name
                    param_key = ref.split('/', 2)[-1]
                    res = self.definitions[param_key]['properties']
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
            http_interface.get("validate")[0].update({"eq":["status_code", 200]})
        
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
        
        # Testcases / write data
        write_data(http_interface, json_path)
        
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
                    join_text = jsonp.replace("{", "").replace("}", "").replace(":", "=").replace("'", "").replace(",", "&").replace(" ", "")
                    w.write(count, 7, uri + url)
                    w.write(count, 8, join_text)
                else:    # Extract the parameters of the get request containing the $symbol in the URL separately and write them to params
                    url = text['request']['url'].replace('{', '$').replace('}', '')
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
    js.analysis_json_data(isDuplicated=True)
    js.write_excel(url, handlefile.get_file_list(APIDIR))
    w.xlsx_to_csv_pd()
