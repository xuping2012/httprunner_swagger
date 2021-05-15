#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json

import yaml

from utils.HandleLogging import log as logger


def get_json(path, field=''):
    """
    获取json文件中的值，data.json和res.json可共用
    :param path:
    :param field:
    :return:
    """
    with open(path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        if field:
            data = json_data.get(field)
            return data
        else:
            return json_data


def write_data(res, json_path):
    """
            把处理后的参数写入json文件
    :param res:
    :param json_path:
    :return:
    """
    if isinstance(res, dict) or isinstance(res, list):
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, sort_keys=True, indent=4)
        logger.info('Interface Params Total：{} ,write to json file successfully!'.format(len(res)))
    else:
        logger.error('\n:{} Params is not dict.\n'.format(write_data.__name__))


def json_to_yaml(json_file):
    """
    支持json格式转yaml
    """
    if json_file.endswith("json"):
        with open(json_file, "r") as pf:
            json_to_dict = json.loads(pf.read())
        yaml_file = json_file.replace(".json", ".yaml")
        with open(yaml_file, "w") as fp:
            yaml.safe_dump(json_to_dict, stream=fp, default_flow_style=False)
            print("json转yaml成功!!!")
    else:
        print("不是json结尾的文件!!!")


def yaml_to_yaml(yaml_file):
    """
    支持json格式转yaml
    """
    if yaml_file.endswith("yaml"):
        with open(yaml_file, "r") as pf:
            # 先将yaml转换为dict格式
            yaml_to_dict = yaml.load(pf, Loader=yaml.FullLoader)
            dict_to_json = json.dumps(yaml_to_dict, sort_keys=False, indent=4, separators=(',', ': '))
        json_file = yaml_file.replace(".yaml", ".json")
        with open(json_file, "w") as fp:
            fp.write(dict_to_json)
            print("yaml转json成功!!!")
    else:
        print("不是yaml结尾的文件!!!")
