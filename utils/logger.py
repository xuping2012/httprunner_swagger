# -*- coding: utf-8 -*-
"""
@author: qguan
@File: logger.py
"""
import logging
import os
import time

from common import dir_config
from common.dir_config import log_file_path
from utils.handle_config import HandleConfig


conf = HandleConfig(file_path=dir_config.config_file_path)
# By default, all output log records are encapsulated by the log module name
# os.path.splitext(os.path.basename(__file__))[0]
logformat = conf.get_value("logger", "logformat")
LEVEL = conf.get_value("logger", "level")


class HandleLogging(object):
    '''
    classdocs:logger
    '''

    def __init__(self, file_name):
        '''
        Constructor
        '''
        self.file_name = file_name
        self.logger = logging.getLogger(file_name)
        self.logger.setLevel(LEVEL)

        #  Print log in console       
        out_console = logging.StreamHandler()
        out_console.setLevel(LEVEL)
        out_console.setFormatter(logging.Formatter(logformat))
        self.logger.addHandler(out_console)

        # Define log output path _ file
        path = self.file_name + '_' + time.strftime('%Y-%m-%d') + '.log'
        if not os.path.exists(dir_config.log_dir):
            os.mkdir(dir_config.log_dir)
        # Set log output channel
        out_file = logging.FileHandler(path, encoding='utf-8')
        # Log split processor
        # logging.handlers.RotatingFileHandler(self.__file, maxBytes=1024*1024, backupCount=5)
        # The level of logs is collected according to what logs are transmitted. It is not default
        out_file.setLevel(LEVEL)
        out_file.setFormatter(logging.Formatter(logformat))
        # Which channel is log output connected to
        self.logger.addHandler(out_file)
        self.logger.removeFilter(out_file)

    def getlog(self):
        return self.logger


log = HandleLogging(file_name=log_file_path).getlog()

if __name__ == '__main__':
    log.error("test log....{}".format(log_file_path))