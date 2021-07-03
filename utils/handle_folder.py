#!/usr/bin/python3

import difflib
import os
import shutil
import sys
from hashlib import md5

from common import dir_config
from utils.logger import log

diffFile = os.path.join(dir_config.report_dir, '比较文件内容异同_diff.html')
backupDiffFile = os.path.join(dir_config.report_dir, '比较文件内容异同_diff_back.html')


class HandleDirFile(object):
    """
    处理文件(夹)的工具类,主要用到shutil第三方库
    """

    #     def __init__(self,src_path,dest_path):
    #         self.srcPath=src_path
    #         self.destPath=dest_path

    def read_json(self, filename):
        '''
        读取json格式文件的数据,进行内容分割
        '''
        try:
            with open(filename, 'r', encoding='utf-8') as fileHandle:
                text = fileHandle.read().splitlines()
            return text
        except IOError as e:
            log.error("文件读取失败:" + e)
            sys.exit()

    def md5_file(self, filename):
        '''
        通过比较两个文件内容的md5值，来生成html异同
        '''
        m = md5()
        try:
            with open(filename, 'rb') as a_file:  # 需要使用二进制格式读取文件内容
                m.update(a_file.read())
        except Exception as e:
            log.error("文件读取失败:" + e)
        return m.hexdigest()

    def diff_json(self, filename1, filename2):
        '''
        比较两个文件内容的md5值；比较两个文件并输出到html文件中
        '''
        file1Md5 = self.md5_file(filename1)
        file2Md5 = self.md5_file(filename2)

        if file1Md5 != file2Md5:
            #             log.info('两个json数据文件md5不一样:')
            text1_lines = self.read_json(filename1)
            text2_lines = self.read_json(filename2)
            d = difflib.HtmlDiff()
            # context=True时只显示差异的上下文，默认显示5行，由numlines参数控制，context=False显示全文，差异部分颜色高亮，默认为显示全文
            result = d.make_file(
                text1_lines, text2_lines, filename1, filename2, context=True)

            # 内容保存到result.html文件中
            try:
                with open(diffFile, 'a', encoding='utf-8') as result_file:
                    result_file.write(result)
            except Exception as e:
                log.error("写入文件失败:" + e)

    def move_file(self, srcPath, destPath):
        '''
        move文件(夹)移动，可覆盖
        srcPath:源文件(夹)路径
        destPath:目标文件(夹)路径
        return:
        '''
        try:
            shutil.move(srcPath, destPath)
        except Exception as e:
            raise e

    def copy_dir(self, srcPath, destPath):
        '''
        copytree:文件(夹)移动，不可覆盖
        srcPath:源文件(夹)路径
        destPath:目标文件(夹)路径,必须不存在
        return: 
        '''
        #         判断目录是否存在
        if os.path.isdir(destPath):
            log.info("{}存在则删除".format(destPath))
            shutil.rmtree(destPath)
        try:
            shutil.copytree(srcPath, destPath)
        except Exception as e:
            raise e

    def copy_file(self, srcPath, destPath):
        '''
        srcPath:源文件(夹)路径
        destPath:目标文件(夹)路径,必须不存在
        return: 
        '''

        destfile = self.get_file_list(destPath)
        srcfile = self.get_file_list(srcPath)

        file_list = []
        for df in destfile:
            file_list.append(df.split("\\")[len(df.split("\\")) - 1])

        for sf in srcfile:
            if sf.split("\\")[len(sf.split("\\")) - 1] not in file_list:
                log.info(
                    "{}文件不存在于备份目录才执行".format(sf.split("\\")[len(sf.split("\\")) - 1]))
                #                 print(config.back_path + sf.split("\\")[len(sf.split("\\")) - 2] + '\\' + sf.split("\\")[len(sf.split("\\")) - 1])
                destDir = dir_config.back_dir + \
                          sf.split("\\")[len(sf.split("\\")) - 2] + "\\"
                if not os.path.exists(destDir):
                    os.makedirs(destDir)
                shutil.copyfile(
                    sf, destDir + sf.split("\\")[len(sf.split("\\")) - 1])

    def diff_dir_file(self, srcPath, destPath):
        '''
        比较两个文件夹及子目录下的文件
        '''

        if os.path.isfile(diffFile):
            try:
                #                 删除文件前先备份文件
                shutil.copyfile(diffFile, backupDiffFile)
                os.remove(diffFile)
            except Exception as e:
                log.error("备份/删除文件:%s,失败!" % diffFile)
                raise e
        else:
            log.info("no such file:%s" % diffFile)

        #         获取目录下的所有文件,返回list
        srcfile = self.get_file_list(srcPath)
        destfile = self.get_file_list(destPath)

        for sf in srcfile:
            for df in destfile:
                if sf.split("\\")[len(sf.split("\\")) - 1] == df.split("\\")[len(df.split("\\")) - 1]:
                    self.diff_json(sf, df)
                #                     log.info("他们名字一样,内容才可以比较：{}=={}".format(sf.split("\\")[len(sf.split("\\"))-1],df.split("\\")[len(df.split("\\"))-1]))

    def get_file_list(self, filepath):
        '''
                    获取文件夹下所有文件名
        filepath：文件路径
        return：返回文件夹下及子目录的所有文件
        '''
        filepath_list = []
        for root_dir, sub_dir, files in os.walk(filepath):
            #             print('root_dir:', root_dir)  # 当前目录路径
            #             print('sub_dirs:', sub_dir)  # 当前路径下所有子目录
            log.info(sub_dir)
            #             print('file_name:', files)  # 当前路径下所有非目录子文件
            for i in range(0, len(files)):
                filepath_list.append(root_dir + "\\" + files[i])

        return filepath_list
