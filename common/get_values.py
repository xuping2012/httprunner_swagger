#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : get_values.py

import time
import copy


def get_type_base_value(_type):
    """根据类型获取基础测试的值"""
    if _type == 'string':
        #  string类型测试，空，NULL，特殊字符，脚本，正常字符，超长字符
        return ["", None, "!@#$%^&*()_+<>?:{}|~`", "<JavaScript>alert(0)</JavaScript>", "test_string","qwertyuiooasdfghjklzxcvbnmazxwsedrtfrrfugyyyfyhjjjkgughsdjgagfjdbdbsddkakdfhakjnnnnnnnnnnnnnkjguyy234567iujwertyuiosdfghjkxcvbmsdfghjkqwertyuizxcvbnasdfghjwertyui234tydfgcvdfrc c1qaz2wsx3edc4rfv5tgb6yhn7ujm8ik9ol0pqwertyuiopdfghjklzxcvbnm"]
    elif _type == 'time':
        #  时间类型测试 错误的年，月，日，非时间类值, 当前时间
        return ["0000-01-01", "1600-01-01", "2010-13-30", "2010-02-30", "not_time", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())]
    elif _type == 'int':
        #  整型测试 非数字类型，溢出, 0
        return ["not_int", 12567890123456781234567123451234567, -12345678912345678912345678901234567, 0]
    elif _type == 'decimal':
        #  浮点测试 非数字类型，溢出, 0
        return ["not_decimal", 12567890123456781234567123451234567.88, -12345678912345678912345678901234567.50, 0.00]
    elif _type == 'bool':
        #  布尔类型 非布尔类型, True, False
        return ["not_bool", True, False]
    elif _type == 'number':
        return ["",22,23.3,"wss",None]
    else:
        #  递归方法
        return recursive_case(_type)


return_list = []
def create_base_case(_source):
    '''获取到type的值后生成基础测试值的列表,生成测试用例'''
    for k, v in _source.items():
        if k == "type":
            for _value in get_type_base_value(v):
                dic_cp2 = copy.deepcopy(_source)
                dic_cp2['example']=_value
                return_list.append(dic_cp2)
        else:
            recursive_case(v)#  改成 return_list.append(replace_default(dic_cp2))   非测试参数替换成替换默认值
    return return_list


def recursive_case(_type):
    """递归,返回特殊类型的取值范围"""
    if isinstance(_type, list):
        new_list = []
        if isinstance(_type[0], dict):
            t_value_list = create_base_case(_type[0])  # 基础测试用例设计
            for t_value in t_value_list:
                new_list.append([t_value])
        else:
            for _value in get_type_base_value(_type[0]):
                new_list.append([_value])
        return new_list
    elif isinstance(_type, dict):
        return create_base_case(_type)
    else:
        return [None]