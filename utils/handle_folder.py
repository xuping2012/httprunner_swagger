#!/usr/bin/python3
"""
@File: handle_folder.py
"""

import difflib
from hashlib import md5
import os
import shutil
import sys

from common.dir_config import REPORTDIR, BACKUPDIR, SWAGGERDIR
from utils.logger import log


# If the directory does not exist, create a folder
if not os.path.exists(REPORTDIR):
    os.makedirs(REPORTDIR)
if not os.path.exists(SWAGGERDIR):
    os.makedirs(SWAGGERDIR)
    
diffFile = os.path.join(REPORTDIR, 'Compare_the_file_diff.html')
backupDiffFile = os.path.join(REPORTDIR, 'Compare_the_file_diff_back.html')


class HandleDirFile(object):
    """
    The tool class for processing files (folders) mainly uses the shutil third-party library
    """

    #     def __init__(self,src_path,dest_path):
    #         self.srcPath=src_path
    #         self.destPath=dest_path

    def read_json(self, filename):
        """
        Read the data of JSON format file for content segmentation
        """
        try:
            with open(filename, 'r', encoding='utf-8') as fileHandle:
                text = fileHandle.read().splitlines()
            return text
        except IOError as e:
            log.error("File read failed:" + e)
            sys.exit()

    def md5_file(self, filename):
        """
        Generate HTML by comparing the MD5 values of the contents of the two files
        """
        m = md5()
        try:
            with open(filename, 'rb') as a_file:    # The contents of the file need to be read in binary format
                m.update(a_file.read())
        except Exception as e:
            log.error("File read failed:" + e)
        return m.hexdigest()

    def diff_json(self, filename1, filename2):
        """
        Compare the MD5 values of the contents of the two files; Compare the two files and output them to an HTML file
        """
        file1Md5 = self.md5_file(filename1)
        file2Md5 = self.md5_file(filename2)

        if file1Md5 != file2Md5:
            # log.info('The two JSON data files MD5 are different:')
            text1_lines = self.read_json(filename1)
            text2_lines = self.read_json(filename2)
            d = difflib.HtmlDiff()
            # When context = true, only the context of the difference is displayed. By default, 5 lines are displayed, \
            # controlled by the numlines parameter. When context = false, the full text is displayed, and the color of the difference part is highlighted. \
            # By default, the full text is displayed
            result = d.make_file(
                text1_lines, text2_lines, filename1, filename2, context=True)

            # Save the content to result HTML file
            try:
                with open(diffFile, 'a', encoding='utf-8') as result_file:
                    result_file.write(result)
            except Exception as e:
                log.error("fail to write to file:" + e)

    def move_file(self, srcPath, destPath):
        """
        Move files (folders) can be moved and overwritten
        Srcpath: source file (folder) path
        Destpath: destination file (folder) path
        return:
        """
        try:
            shutil.move(srcPath, destPath)
        except Exception as e:
            raise e

    def copy_dir(self, srcPath, destPath):
        """
        Copytree: the file (folder) is moved and cannot be overwritten
        Srcpath: source file (folder) path
        Destpath: the destination file (folder) path must not exist
        return: 
        """
        # Determine whether the directory exists
        if os.path.isdir(destPath):
            log.info("{}Delete if EXIT".format(destPath))
            shutil.rmtree(destPath)
        try:
            shutil.copytree(srcPath, destPath)
        except Exception as e:
            raise e

    def copy_file(self, srcPath, destPath):
        """
        Srcpath: source file (folder) path
        Destpath: the destination file (folder) path must not exist
        return: 
        """

        destfile = self.get_file_list(destPath)
        srcfile = self.get_file_list(srcPath)

        file_list = []
        for df in destfile:
            file_list.append(df.split("\\")[len(df.split("\\")) - 1])

        for sf in srcfile:
            if sf.split("\\")[len(sf.split("\\")) - 1] not in file_list:
                log.info(
                    "{}The file does not exist in the backup directory".format(sf.split("\\")[len(sf.split("\\")) - 1]))
                #                 print(config.back_path + sf.split("\\")[len(sf.split("\\")) - 2] + '\\' + sf.split("\\")[len(sf.split("\\")) - 1])
                destDir = BACKUPDIR + \
                          sf.split("\\")[len(sf.split("\\")) - 2] + "\\"
                if not os.path.exists(destDir):
                    os.makedirs(destDir)
                shutil.copyfile(
                    sf, destDir + sf.split("\\")[len(sf.split("\\")) - 1])

    def diff_dir_file(self, srcPath, destPath):
        """
        Compare the files in two folders and subdirectories
        """
        if os.path.isfile(diffFile):
            try:
                # Back up files before deleting them
                shutil.copyfile(diffFile, backupDiffFile)
                os.remove(diffFile)
            except Exception as e:
                log.error("Backup OR delete file:%s, failed!" % diffFile)
                raise e
        else:
            log.info("no such file:%s" % diffFile)

        # Get all the files in the directory and return list
        srcfile = self.get_file_list(srcPath)
        destfile = self.get_file_list(destPath)

        for sf in srcfile:
            for df in destfile:
                if sf.split("\\")[len(sf.split("\\")) - 1] == df.split("\\")[len(df.split("\\")) - 1]:
                    self.diff_json(sf, df)
                # log.info("They have the same name, the content can be compared：{}=={}".format(sf.split("\\")[len(sf.split("\\"))-1],df.split("\\")[len(df.split("\\"))-1]))

    def get_file_list(self, filepath):
        """
        Get all file names under the folder
        filepath：
        return：file_list
        """
        filepath_list = []
        for root_dir, sub_dir, files in os.walk(filepath):
            # log.info('root_dir:', root_dir)  # Current directory path
            # log.info('sub_dirs:', sub_dir)  # All subdirectories under the current path
            log.info(sub_dir)
            # log.info('file_name:', files)  # All non directory sub files under the current path
            for i in range(0, len(files)):
                filepath_list.append(root_dir + "\\" + files[i])

        return filepath_list

# INIT OBJ
handlefile = HandleDirFile()