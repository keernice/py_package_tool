#!/usr/bin/python3

# -*-coding:utf-8 -*-

# Reference:**********************************************

# @Time    : 2019/9/12 5:17 下午

# @Author  : yanke

# @File    : config.py

# @Software: PyCharm

# Reference:**********************************************

# 本地配置
import os
import sys

baseAbsPath = os.path.dirname(os.path.abspath(sys.argv[0])) + os.sep
local_config = {
    "drawable_path": '',  # 项目的资源目录
    "local_drawable_path": baseAbsPath + "generateAPK/pics",  # 本地的资源目录
    "strings_xml": '',  # values下strings.xml
    "colors_xml": '',  # values下color.xml
    "manifest_xml": ''  # AndroidManifest.xml
}
