# -*- coding: utf-8 -*-
"""
@author: qguan
"""
import logging
import os
import time

from common import dir_config
from utils.handle_config import HandleConfig

conf = HandleConfig(file_path=dir_config.config_dir + "config.ini")
# 默认所有输出日志记录以封装的日志模块名称
# os.path.splitext(os.path.basename(__file__))[0]
FILENAME = conf.get_value("logger","logname")
logformat = conf.get_value("logger", "logformat")
LEVEL = conf.get_value("logger", "level")


class HandleLogging(object):
    '''
    classdocs
    '''

    def __init__(self, file_name):
        '''
        Constructor
        '''
        self.file_name = file_name
        self.logger = logging.getLogger(file_name)
        self.logger.setLevel(LEVEL)

        #         在控制台打印日志
        out_console = logging.StreamHandler()
        out_console.setLevel(LEVEL)
        out_console.setFormatter(logging.Formatter(logformat))
        self.logger.addHandler(out_console)

        # 定义记录日志输出路径+文件
        path = dir_config.log_dir + self.file_name + '_' + time.strftime('%Y-%m-%d') + '.log'
        if not os.path.exists(dir_config.log_dir):
            os.mkdir(dir_config.log_dir)
        # 设置日志输出渠道
        out_file = logging.FileHandler(path, encoding='utf-8')
        # 日志拆分处理器
        # logging.handlers.RotatingFileHandler(self.__file, maxBytes=1024*1024, backupCount=5)
        # 日志传什么就收集什么级别的日志,不默认
        out_file.setLevel(LEVEL)
        out_file.setFormatter(logging.Formatter(logformat))
        # 日志输出对接那个渠道
        self.logger.addHandler(out_file)
        self.logger.removeFilter(out_file)

    def getlog(self):
        return self.logger


log = HandleLogging(file_name=FILENAME).getlog()

if __name__ == '__main__':
    log.error("我是测试日志！{}".format(FILENAME))
    pass
