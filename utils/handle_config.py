#!/usr/bin/python3
"""
Created on 2019年9月29日
@author: qguan
@File: handle_config.py
"""
from configparser import ConfigParser
import configparser

from common.dir_config import config_dir, config_file_path


class HandleConfig(object):
    """
    This class is suitable for novices. Generally, you only need to inherit configparser, 
    and then you can silently call all the methods to obtain the configuration file information
    """

    def __init__(self, file_path, encoding="utf-8"):
        """Initialize read configuration file and instantiate file parameters"""
        self.file_path = file_path
        self.conf = configparser.ConfigParser()
        self.encoding = encoding
        self.conf.read(self.file_path, encoding=self.encoding)

    def get_value(self, section, option):
        """Gets the value of the INI \ conf configuration file"""
        return self.conf.get(section, option,raw=True)

    def get_boolean(self, section, option):
        """gets the value of the ini\conf configuration file"""
        return self.conf.getboolean(section, option)

    def get_int(self, section, option):
        """gets the value of the ini\conf configuration file"""
        return self.conf.getint(section, option)

    def get_float(self, section, option):
        """gets the value of the ini\conf configuration file"""
        return self.conf.getfloat(section, option)

    def set_section_value(self, section, option, value):
        """set section：option value"""
        if not self.conf.has_section(section):
            self.conf.add_section(section)
            self.conf.set(section, option, value)
            self.conf.write(open(self.file_path, "w"))
        else:
            self.conf.set(section, option, value)
            self.conf.write(open(self.file_path, "w"))

    def remove_section(self, section, option):
        """remove section before remove option"""
        if section in self.conf.sections():
            self.remove_option(section, option)
            self.conf.remove_section(section)
            self.conf.write(open(self.file_path, "r+"))
        else:
            print("{} not in ！".format(section))

    def remove_option(self, section, option):
        """move option"""
        print(self.conf.sections())
        if section in self.conf.sections():
            if option in self.conf.options(section):
                self.conf.remove_option(section, option)
                self.conf.write(open(self.file_path, "r+"))
            else:
                print("{}not in ！".format(option))
        else:
            print("{}not in ！".format(section))




class SimplerConfig(ConfigParser):
    """
    Optimize the above configuration file reading class
    """

    def __init__(self, config_file, encoding="utf-8"):
        # Create a configparser resolution object and inherit configparser
        super().__init__()
        self.config_file = config_file
        self.encoding = encoding
        # Read the specified configuration file
        self.read(self.config_file, encoding=self.encoding)


if __name__ == '__main__':
    conf = SimplerConfig(config_file=config_file_path)
    text = conf.get("logger", "level")
    print(text)