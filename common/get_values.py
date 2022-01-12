#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : get_values.py

import time
import copy


def get_type_base_value(_type):
    """Get the value of the basic test according to the type"""
    if _type == 'string':
        #  String type test, null, null, special character, script, normal character, super long character
        return ["", None, "!@#$%^&*()_+<>?:{}|~`", "<JavaScript>alert(0)</JavaScript>", "test_string","qwertyuiooasdfghjklzxcvbnmazxwsedrtfrrfugyyyfyhjjjkgughsdjgagfjdbdbsddkakdfhakjnnnnnnnnnnnnnkjguyy234567iujwertyuiosdfghjkxcvbmsdfghjkqwertyuizxcvbnasdfghjwertyui234tydfgcvdfrc c1qaz2wsx3edc4rfv5tgb6yhn7ujm8ik9ol0pqwertyuiopdfghjklzxcvbnm"]
    elif _type == 'time':
        #  Time type test error year, month, day, non time class value, current time
        return ["0000-01-01", "1600-01-01", "2010-13-30", "2010-02-30", "not_time", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())]
    elif _type == 'int':
        #  Integer test, non numeric type, overflow, 0
        return ["not_int", 12567890123456781234567123451234567, -12345678912345678912345678901234567, 0]
    elif _type == 'decimal':
        #  Floating point test, non numeric type, overflow, 0
        return ["not_decimal", 12567890123456781234567123451234567.88, -12345678912345678912345678901234567.50, 0.00]
    elif _type == 'bool':
        #  Boolean type, non boolean type, true, false
        return ["not_bool", True, False]
    elif _type == 'number':
        return ["",22,23.3,"wss",None]
    else:
        return recursive_case(_type)


return_list = []
def create_base_case(_source):
    '''After obtaining the value of type, generate a list of basic test values and generate test cases'''
    for k, v in _source.items():
        if k == "type":
            for _value in get_type_base_value(v):
                dic_cp2 = copy.deepcopy(_source)
                dic_cp2['example']=_value
                return_list.append(dic_cp2)
        else:
            recursive_case(v) #  改成 return_list.append(replace_default(dic_cp2))   Replace non test parameters with default values
    return return_list


def recursive_case(_type):
    """Used for recursion to return the value range of special types"""
    if isinstance(_type, list):
        new_list = []
        if isinstance(_type[0], dict):
            t_value_list = create_base_case(_type[0])  # Basic test case design
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