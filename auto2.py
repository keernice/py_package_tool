#!/usr/bin/env python
# coding=utf-8
# Author   :  yanke
# Date     :  2019-07-126
# function :  1. decompile apks 2. modify the AndroidManifest.xml file
#          :  3. recompile the apks


import os
import re
import shutil
import xml.etree.ElementTree as ET
import tempfile
import xml.dom.minidom
from xml.dom.minidom import parse
# import time
import sys
# import pyautogui
import subprocess

'''
步骤：
1、反编译apk
2、修改apk内容(applicationId、logo、appName)
3、回包
4、利用360渠道打包工具多渠道打包并重新签名(一定要重新签名)
'''

keyPath = "/Users/yanke/cimob/generateAPK/repackage/skinsign.jks"

appPath = "/Users/yanke/cimob/generateAPK/apks/"
apkPath = "/Users/yanke/cimob/generateAPK/apkOut/"
recompileApkPath = "/Users/yanke/cimob/generateAPK/recompileApk/"
repackagedAppPath = "/Users/yanke/cimob/generateAPK/repackage/repackagedAPK/"

stringsXML = '/Users/yanke/cimob/generateAPK/apkOut/10000/res/values/strings.xml'
matchFile = '/Users/yanke/cimob/generateAPK/match.txt'

# 声明全局字典,通过读取match.txt为字典赋值
match = {}
# mactch字典中的key列表
appNameList = []

# 本地配置
local_config = {
    "local_path": "/xxx/xxx/xxx",  # 本地路径
    "drawable_path": "/Users/yanke/cimob/generateAPK/apkOut/10000/res",  # 项目的资源目录
    "local_drawable_path": "/Users/yanke/cimob/generateAPK/pics",  # 本地的资源目录
    "strings_path": "/xxx/xxx/xxx/app/src/main/res/values/strings.xml",  # strings资源
}

# 项目中的图片资源
project_drawable = {
    "logo1": "logo1.png",  # 应用图标
}

if not os.path.exists(apkPath):
    os.makedirs(apkPath)


# -r 阻止反编译resource，不修改resources.arsc，若仅仅修改java（smail），建议使用该选项。
def decompile():
    appList = os.listdir(appPath)

    for app in appList:
        eachappPath = os.path.join(appPath, app)
        apkname = app.split(".")[0]
        apktoolPath = os.path.join(apkPath, apkname)

        cmd = "apktool d {0} -o {1}".format(eachappPath, apktoolPath)
        try:
            os.system(cmd)
        except:
            cmd = "echo {0}>>{1}".format(app, "反编译异常")
            os.system(cmd)
            continue


def recompile(appName, logoName):
    apkList = os.listdir(apkPath)
    print('开始重新编译回包')
    for apk in apkList:
        eachapkPath = os.path.join(apkPath, apk)

        cmd = "apktool b {0} -o {1}".format(eachapkPath, recompileApkPath + appName + logoName + '.apk')
        try:
            os.system(cmd)
            print('开始重新编译回包')
        except:
            cmd = "echo {0}>>{1}".format(apk, "重新编译回包异常")
            os.system(cmd)
            continue


# 遍历修改替换apk反编译项目文件夹内容(limit res dir)
def modifyapp():
    for aName in appNameList:
        if aName in match:
            logoList = match.get(aName)
            for logo in logoList:
                replaceAppName2(aName)
                replace_drawable(logo)
                recompile(aName, logo)
    pass


# appName替换 需要提供原appName即name1，替换为name2
def replaceAppName(t_path, name1, name2):
    with open(t_path, 'r', encoding='utf-8') as r:
        s = r.read()
        replace = s.replace(name1, name2)
    with open(t_path, 'w', encoding='utf-8') as w:
        w.write(replace)
    r.close()
    w.close()


def sign_apk():
    repackappList = os.listdir(apkPath)

    for repackapp in repackappList:
        print(repackappList[1])
        repackName = repackapp + ".apk"
        resign_appName = repackapp + "_sign" + ".apk"
        repackAppPath = os.path.join(apkPath, repackapp, "dist", repackName)
        sign_apk = os.path.join(repackagedAppPath, resign_appName)

        read, write = os.pipe()
        os.write(write, '111111'.encode('utf-8'))
        os.close(write)
        # jarsigner -verbose -keystore keystore文件路径 -signedjar 签名后生成的apk路径 待签名的apk路径 别名
        cmd = "jarsigner -verbose -keystore {0} -signedjar {1} {2} {3}".format(keyPath, sign_apk, repackAppPath,
                                                                               "keyou")
        #        subprocess.call(cmd,stdin=read)
        cmd1 = "echo '111111\r'|{0} ".format(cmd)
        cmd2 = "zipalign -f -v 4 {0} {1}".format(repackAppPath, sign_apk)
        cmd3 = "zipalign -c -v 4 {0}".format(sign_apk)
        try:
            os.system(cmd1)
            os.system(cmd2)
            os.system(cmd3)
        except:
            cmd = "echo {0} >>{1}".format(repackapp, "wrongSign")
            continue


def rename():
    appList = os.listdir(repackagedAppPath)

    for app in appList:
        oldNamePath = os.path.join(repackagedAppPath, app)
        appName = app.split("_")[0] + ".apk"
        newNamePath = os.path.join(repackagedAppPath, appName)

        os.rename(oldNamePath, newNamePath)


def replaceAppName2(targetAppName):
    tree = ET.parse(stringsXML)
    root = tree.getroot()
    for child in root.findall('string'):
        if child.attrib['name'] == 'app_name':
            child.text = targetAppName

    tree.write(stringsXML, "UTF-8")


# 查找本地资源文件
# def search_drawable_in_local(source_id):
#     (sourcename, srextension) = os.path.splitext(source_id)
#     path = local_config["local_drawable_path"]
#     if os.path.isdir(path):
#         # 根据要替换的文件名找到新文件并返回
#         listfile = os.listdir(path)
#         for file in listfile:
#             # ic_launcher.png
#             (filename, extension) = os.path.splitext(file)
#             if filename == sourcename:
#                 return file
#     else:
#         # 本地资源路径非文件夹
#         return
#     pass

# 查找本地资源文件
def search_drawable_in_local2(logo):
    # (sourcename, srextension) = os.path.splitext(source_id)
    path = local_config["local_drawable_path"]
    if os.path.isdir(path):
        # 根据要替换的文件名找到新文件并返回
        listfile = os.listdir(path)
        for file in listfile:
            # ic_launcher.png
            (filename, extension) = os.path.splitext(file)
            if filename == logo:
                return file
    else:
        # 本地资源路径非文件夹
        return
    pass


# 递归替换项目中的资源
def search_drawable_in_project(sourcedir, targetdir):
    # if sourcedir.find(".git") >= 0:
    #     return
    # print sourcedir
    if os.path.isdir(sourcedir):
        # 是文件夹，检索文件夹内文件递归
        listdir = os.listdir(sourcedir)
        for ld in listdir:
            if os.path.isdir(ld) and ld.find("mipmap") < 0:
                continue
            path = sourcedir + "/" + ld
            search_drawable_in_project(path, targetdir)
    else:
        # 是文件,判断是否是要复制的文件
        splitl = os.path.split(sourcedir)
        targetl = os.path.split(targetdir)
        if os.path.isfile(sourcedir) and targetl[1] == splitl[1]:
            shutil.copy(targetdir, sourcedir)
        return
    pass


# 修改所有资源图片
# 替换掉所有类型的mipmap包下的文件
def replace_drawable(logo):
    print("开始替换图片资源...")
    for pr in project_drawable:
        targetfile = search_drawable_in_local2(logo)
        if targetfile is not None:
            # 递归查找
            # (filename,extension) = os.path.splitext(targetfile)
            targetdir = local_config["local_drawable_path"] + os.sep + targetfile
            # 创建临时目录由上下文管理器管理(上下文管理器退出后文件目录会被自动删除)
            with tempfile.TemporaryDirectory() as tmpdir:
                print('Created temporary directory ', tmpdir)
                print(os.path.exists(tmpdir))
                shutil.copy2(targetdir, tmpdir)
                targetdir = tmpdir + os.sep + targetfile
                resultDir = tmpdir + os.sep + 'logo1.png'
                os.rename(targetdir, resultDir)
                # print("将替换的图片资源: %s " % (targetdir))
                search_drawable_in_project(local_config["drawable_path"], resultDir)
    print("图片资源替换完成.")
    pass


# 根据读取appName与logo对应文件match.txt生成python字典
def generateDict():
    print('读取match.txt开始')
    try:
        with open(matchFile, "r", encoding="utf-8", errors='ignore') as f:
            lineData = f.readlines()
            for line in lineData:
                tmpline = line.strip()
                key, value = tmpline.split('=')
                logoList = value.split(',')
                appNameList.append(key)
                if not key in match:
                    match[key] = logoList
        print('读取match.txt完成')
    except:
        print('读取match.txt异常,请检查文件')
    pass

decompile()
# rename()

generateDict()
modifyapp()
# recompile()

# sign_apk()

print("all work is done!")

'''
初步beta2支持多对多打包场景步骤：
The apks directory allows only one APK to be placed with a applicationId.
Condition：the number of appNames and logos must be equal.
① 循环以反编译开始的脚本执行流程,循环次数与appNames及logos数量相关。
② decompile反编译执行暂时保留对apks的循环执行，beta2主要功能任务完成后再考虑修改。
③ replaceAppName2解析strings.xml替换app_name
-------------
兼容性优化：
①多平台路径、简化目录
②路径文件夹命名优化，目的:使开发人员对自己打的apk所属分组能一目了然
③脚本执行异常后提示、是否需要退出执行脚本的评估优化
④python脚本如何封装，闭包
--------------------------
后期自拟需求：
①增加多包名、多渠道因变量进行脚本打未签名包
'''
