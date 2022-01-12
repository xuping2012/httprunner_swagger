#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : dir_config.py
import os
import sys
import time


# Get the root path of the project under different system environments
if "win" in sys.platform:
    BASEDIR = os.path.dirname(os.path.dirname(__file__))
elif "linux" in sys.platform:
    BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
# Equipped with httprunner2 X frame; Project catalogue
SWAGGERDIR = os.path.join(BASEDIR, "swagger")   
TESTSUITEDIR = os.path.join(SWAGGERDIR, "testsuites")
TESTCASEDIR = os.path.join(SWAGGERDIR, "testcases")
APIDIR = os.path.join(SWAGGERDIR, "api")

# REPORT PATH
REPORTDIR = os.path.join(BASEDIR, "reports")

# Profile path
PROFILEDIR = os.path.join(BASEDIR, "properties") 
PROFILEPATH = os.path.join(PROFILEDIR, "config.ini")
  
# Log path
LOGDIR = os.path.join(BASEDIR, "logs")
LOGFILEPATH = os.path.join(LOGDIR, "AllServer.log")
  
# Backup path
BACKUPDIR = os.path.join(BASEDIR, "swaggerBackUp")    

# Test case data file
CSVFILEPATH = os.path.join(SWAGGERDIR, "Api_TestCases.csv")
EXCELFILEPATH = os.path.join(SWAGGERDIR, "Api_TestCases.xlsx")
BACKTESTCASEPATH = os.path.join(SWAGGERDIR, "Api_TestCases_bak_{}.xlsx".format(time.strftime('%Y-%m-%d_%H-%m')))


if __name__ == '__main__':
    print(SWAGGERDIR)
