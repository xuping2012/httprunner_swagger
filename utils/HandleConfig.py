'''
Created on 2019年9月29日
@author: qguan
'''

import configparser
from utils.HandleLogging import log


class HandleConfig(object):
    """
    这个类封装的适合新手，一般情况下，只需要继承configparser，然后就可以默默的调用其中所有获取配置文件信息的方法
    """

    def __init__(self, file_path, encoding="utf-8"):
        '''初始化读取配置文件，实例化文件参数'''
        self.file_path = file_path
        self.conf = configparser.ConfigParser()
        self.encoding = encoding
        self.conf.read(self.file_path, encoding=self.encoding)

    def get_value(self, section, option):
        '''获取ini\conf配置文件的值'''
        return self.conf.get(section, option)

    def get_boolean(self, section, option):
        '''获取ini\conf配置文件的值为bool类型'''
        return self.conf.getboolean(section, option)

    def get_int(self, section, option):
        '''获取ini\conf配置文件的值为int类型'''
        return self.conf.getint(section, option)

    def get_float(self, section, option):
        '''获取ini\conf配置文件的值为float类型'''
        return self.conf.getfloat(section, option)

    def set_section_value(self, section, option, value):
        '''设置section：option的值'''
        if not self.conf.has_section(section):
            log.info("{}不存在，需要新增！".format(section))
            self.conf.add_section(section)
            self.conf.set(section, option, value)
            self.conf.write(open(self.file_path, "w"))
        else:
            self.conf.set(section, option, value)
            self.conf.write(open(self.file_path, "w"))

    def remove_section(self, section, option):
        '''移除section先移除option'''
        if section in self.conf.sections():
            self.remove_option(section, option)
            self.conf.remove_section(section)
            self.conf.write(open(self.file_path, "r+"))
        else:
            print("{}不存在！".format(section))

    def remove_option(self, section, option):
        '''移除option'''
        print(self.conf.sections())
        if section in self.conf.sections():
            if option in self.conf.options(section):
                self.conf.remove_option(section, option)
                self.conf.write(open(self.file_path, "r+"))
            else:
                print("{}不存在！".format(option))
        else:
            print("{}不存在！".format(section))


from configparser import ConfigParser


class SimplerConfig(ConfigParser):
    """
    优化上面配置文件读取类
    """

    def __init__(self, config_file, encoding="utf-8"):
        # 创建ConfigParser解析对象,继承ConfigParser
        super().__init__()
        self.config_file = config_file
        self.encoding = encoding
        # 读取指定配置文件
        self.read(self.config_file, encoding=self.encoding)