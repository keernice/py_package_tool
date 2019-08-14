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
repackagedAppPath = "/Users/yanke/cimob/generateAPK/repackage/repackagedAPK/"

# 本地配置
local_config = {
    "local_path": "/xxx/xxx/xxx",  # 本地路径
    "new_city": "xxx",
    "config_path": "/xxx/xxx/xxx/Config.java",
    "qq_appid": "qq12345678",  # QQ的APPID
    "weibo_appkey": "wb12345678",  # 微博的APPKEY
    "weichat_appid": "wcz123456789012345",  # 微信的APPID
    "weichat_appsecret": "wc123456789012345678901234567890",  # 微信的APPSECRET
    "appid": "12345678901234567890123456789012",  # 应用的APPID
    "drawable_path": "/Users/yanke/cimob/generateAPK/apkOut/10000/res",  # 项目的资源目录
    "local_drawable_path": "/Users/yanke/cimob/generateAPK/pic",  # 本地的资源目录
    "gradle_path": "/xxx/xxx/xxx/app/build.gradle",  # 应用gradle的路径
    "new_package_name": "xxx.xxx.xxx",  # 新的包名
    "old_package_name": "xxx.xxx.xxx",  # 原来的包名
    "strings_path": "/xxx/xxx/xxx/app/src/main/res/values/strings.xml",  # string资源
    "app_name": "xxxx",  # 新的appname
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


def recompile():
    apkList = os.listdir(apkPath)

    for apk in apkList:
        eachapkPath = os.path.join(apkPath, apk)

        cmd = "apktool b {0}".format(eachapkPath)
        try:
            os.system(cmd)
        except:
            cmd = "echo {0}>>{1}".format(apk, "重新编译回包异常")
            os.system(cmd)
            continue


# 对反编译后的res资源文件夹下的资源进行修改替换
def modifyapp():
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


def replaceAppName2(f_dir, nodeName):
    tree = ET.parse(f_dir)
    root = tree.getroot()
    for child in root.findall('string'):
        if child.attrib['name'] == nodeName:
            child.text = str('111')

    tree.write(f_dir, "UTF-8")


# 查找本地资源文件
def search_drawable_in_local(source_id):
    (sourcename, srextension) = os.path.splitext(source_id)
    path = local_config["local_drawable_path"]
    if os.path.isdir(path):
        # 根据要替换的文件名找到新文件并返回
        listfile = os.listdir(path)
        for file in listfile:
            # ic_launcher.png
            (filename, extension) = os.path.splitext(file)
            if filename == sourcename:
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
        # print "src: "+splitl[1]+" tar: "+targetl[1]
        if os.path.isfile(sourcedir) and targetl[1] == splitl[1]:
            shutil.copy(targetdir, sourcedir)
        return
    pass


# 修改所有资源图片
# 替换掉所有类型的mipmap包下的文件
def replace_drawable():
    print("开始替换图片资源...")
    for pr in project_drawable:
        targetfile = search_drawable_in_local(project_drawable[pr])
        if targetfile is not None:
            # 递归查找
            # (filename,extension) = os.path.splitext(targetfile)
            targetdir = local_config["local_drawable_path"] + "/" + targetfile
            print("将替换的图片资源: %s " % (targetdir))
            search_drawable_in_project(local_config["drawable_path"], targetdir)
    print("图片资源替换完成.")
    pass


fileDir = '/Users/yanke/cimob/generateAPK/apkOut/10000/res/values/strings.xml'
decompile()
# modifyapp()
# rename()
replaceAppName2(fileDir, 'app_name')
replace_drawable()

recompile()
# sign_apk()
print("all work is done!")

