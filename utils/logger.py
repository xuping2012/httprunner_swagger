# -*- coding: utf-8 -*-
"""
@author: qguan
@File: logger.py
"""
import logging
from logging.handlers import TimedRotatingFileHandler 

from utils.handle_config import conf
from common.dir_config import LOGFILEPATH


# By default, all output log records are encapsulated by the log module name
# os.path.splitext(os.path.basename(__file__))[0]
FORMATTER = conf.get_value("logger", "formatter")
LEVEL = conf.get_value("logger", "level")
OUTLEVEL = conf.get_value("logger", "outLevel")

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
        out_console.setFormatter(logging.Formatter(FORMATTER))
        self.logger.addHandler(out_console)

        # Define log output path _ file
        # Set log output channel
        out_file = TimedRotatingFileHandler(filename=LOGFILEPATH, when="D", interval=1, backupCount=3, encoding='utf-8')
        # Log split processor
        # logging.handlers.RotatingFileHandler(self.__file, maxBytes=1024*1024, backupCount=5)
        # The level of logs is collected according to what logs are transmitted. It is not default
        out_file.setLevel(OUTLEVEL)
        out_file.setFormatter(logging.Formatter(FORMATTER))
        # Which channel is log output connected to
        self.logger.addHandler(out_file)
        self.logger.removeFilter(out_file)

    def getlog(self):
        return self.logger


log = HandleLogging(file_name=LOGFILEPATH).getlog()