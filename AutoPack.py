#!/usr/bin/env python
# coding=utf-8
# Author   :  yanke
# Date     :  2019-07-126
# function :  1. decompile apks 2. modify the AndroidManifest.xml file
#          :  3. recompile the apks


import os
import shutil
import sys
import xml.etree.ElementTree as ET
import tempfile
import platform
import json
import traceback
import datetime

'''
步骤：
1、反编译apk
2、修改apk内容(applicationId、logo、appName)
3、回包
4、利用360渠道打包工具多渠道打包并重新签名(一定要重新签名)
'''
'''
Author : yanke
Date   : 2019-08-07

To be fix:
1、通过回编译完成后再次检查apk文件是否生成标识回包是否成功，因为回编译异常并不都会进入exception块中执行

'''
baseAbsPath = os.path.dirname(os.path.abspath(sys.argv[0])) + os.sep
apkPath = baseAbsPath + 'generateAPK/apkOut/'
sourceApkPath = baseAbsPath + 'generateAPK/apks/'
recompileApkPath = baseAbsPath + 'generateAPK/recompileApk/'
repackagedAppPath = baseAbsPath + 'generateAPK/repackage/repackagedAPK/'
matchFile = baseAbsPath + 'generateAPK/match.txt'
matchJsonFile = baseAbsPath + 'generateAPK/match.json'

# 声明全局字典,通过读取match.txt为字典赋值
match = {}
# mactch字典中的key列表
appNameList = []

# 本地配置
local_config = {
    "drawable_path": '',  # 项目的资源目录
    "local_drawable_path": baseAbsPath + "generateAPK/pics",  # 本地的资源目录
    "strings_xml": '',  # values下strings.xml
    "line_number_record": 0
}

# 项目中的图片资源
project_drawable = {
    "logo1": "logo1.png"  # 应用图标
}


# -r 阻止反编译resource，不修改resources.arsc，若仅仅修改java（smail），建议使用该选项。
def deCompileExceptionHandle(apk):
    print('反编译失败')
    cmd = "echo {0}>>{1}".format(apk, "反编译失败")
    os.system(cmd)
    pass


def decompile(apk):
    apkname = getApkFileName(apk)
    if not apkname:
        print('读取apks文件夹下apk文件出错')
        return False
    eachappPath = os.path.join(sourceApkPath, apk)
    deCompileCompletehPath = os.path.join(apkPath, apkname)
    sys = platform.system()
    print('开始反编译')
    if sys.find('Windows') > -1:
        cmd = "apktool d {0} -f -o {1} <nul".format(eachappPath, deCompileCompletehPath)
    else:
        cmd = "apktool d {0} -f -o {1}".format(eachappPath, deCompileCompletehPath)
    try:
        os.system(cmd)
        # 检查反编译文件是否存在标识反编译是否真正完成，避免未进入except的反编译失败场景
        if os.path.exists(deCompileCompletehPath):
            print('完成反编译')
            return True
        else:
            deCompileExceptionHandle(apk)
            return False

            # data_file = '//var/folders/c6/9591_tjd321fgx_4hs6hqmxm0000gn/T/1.apk'
    # # 如果类型是文件则进行删除
    # if os.path.is_file(data_file):
    #     os.remove(data_file)
    #     print('删除1.apk成功')
    # else:
    #     print(f'Error: {data_file} not a valid filename')

    except:
        deCompileExceptionHandle(apk)
        return False


pass


def recompile(appName, logoName, apkOutDirName):
    apkList = os.listdir(apkPath)
    print('开始重新编译回包')
    for apk in apkList:
        if apk.find('.DS_Store') > -1:
            continue
        if not apkOutDirName == apk:
            continue
        eachapkPath = os.path.join(apkPath, apk)
        sys = platform.system()
        apkOutPath = recompileApkPath + apkOutDirName + os.sep + appName + '_' + logoName + '.apk'
        if sys.find('Windows') > -1:
            cmd = "apktool b {0} -f -o {1} <nul".format(eachapkPath, apkOutPath)
        else:
            cmd = "apktool b {0} -f -o {1}".format(eachapkPath, apkOutPath)
        try:
            os.system(cmd)
            print('完成重新编译回包')
            input('请按下任意键退出控制台窗口...')
        except:
            print('重新编译回包异常')
            cmd = "echo {0}>>{1}".format(apk, "重新编译回包异常")
            os.system(cmd)
            continue
    pass


# 遍历修改替换apk反编译项目文件夹内容(limit res dir)
def modifyapp(apk):
    apkname = apk.split(".")[0]
    for aName in appNameList:
        if aName in match:
            logoList = match.get(aName)
            for logo in logoList:
                replaceAppName(aName)
                replace_drawable(logo)
                recompile(aName, logo, apkname)
    pass


def rename():
    appList = os.listdir(repackagedAppPath)

    for app in appList:
        oldNamePath = os.path.join(repackagedAppPath, app)
        appName = app.split("_")[0] + ".apk"
        newNamePath = os.path.join(repackagedAppPath, appName)

        os.rename(oldNamePath, newNamePath)
        pass


# appName替换 targetAppName标识目标appName
def replaceAppName(targetAppName):
    print('开始替换appName')
    isFinish = False
    tree = ET.parse(local_config['strings_xml'])
    root = tree.getroot()
    for child in root.findall('string'):
        if child.attrib['name'] == 'app_name':
            child.text = targetAppName
            isFinish = True

    if isFinish:
        tree.write(local_config['strings_xml'], "UTF-8")
        print('完成替换appName')
    else:
        print('在strings.xml中没有定义app_name，导致无法替换，请检查strings.xml文件')
    pass


# 查找本地资源文件
def search_drawable_in_local(logo):
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
        name = splitl[1].split('.')
        name1 = targetl[1].split('.')
        if os.path.isfile(sourcedir) and (name == name1):
            shutil.copy2(targetdir, sourcedir)
            print('图片资源替换完成')
        return
    pass


# 修改所有资源图片
# 替换掉所有类型的mipmap包下的文件
def replace_drawable(logo):
    print("开始替换图片资源...")
    for pr in project_drawable:
        targetfile = search_drawable_in_local(logo)
        if targetfile is not None:
            # 递归查找
            # (filename,extension) = os.path.splitext(targetfile)
            print('targetFile  ' + targetfile)
            targetdir = local_config["local_drawable_path"] + os.sep + targetfile
            # 创建临时目录由上下文管理器管理(上下文管理器退出后文件目录会被自动删除)
            with tempfile.TemporaryDirectory() as tmpdir:
                print('Created temporary directory ', tmpdir)
                print(os.path.exists(tmpdir))
                shutil.copy2(targetdir, tmpdir)
                targetdir = tmpdir + os.sep + targetfile
                resultDir = tmpdir + os.sep + 'logo1' + os.path.splitext(targetfile)[1]
                os.rename(targetdir, resultDir)
                search_drawable_in_project(local_config["drawable_path"], resultDir)
    pass


# 根据match.json匹配文件生成字典
def generateDict(apkname):
    print('读取match.txt开始')
    try:
        with open(matchJsonFile, "r", encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
            handleJson(data, apkname)

        print('读取match.txt完成')
    except:
        print('读取match.txt异常,请检查文件')
    pass


def handleJson(data, apkname):
    try:
        appNameList.clear()
        match.clear()
        for (k, v) in data.items():
            if (apkname in v) and isinstance(v, dict):
                for (k1, v1) in v.items():
                    if (k1 == apkname) and isinstance(v1, list):
                        for listitem in v1:
                            key = listitem['name']
                            value = listitem['icon']
                            key = key.strip()
                            appNameList.append(key)
                            if not key in match:
                                match[key] = value

        print('appNameList: ', appNameList)
        print('match: ', match)
    except Exception as e:
        # 输出异常堆栈信息
        print(traceback.print_exc())

    pass


def configFilePath(apkname):
    if apkname:
        local_config['drawable_path'] = apkPath + apkname + "/res"
        local_config['strings_xml'] = apkPath + apkname + "/res/values/strings.xml"
    pass


def getApkFileName(apk):
    lastIndex = apk.rindex('.')
    if lastIndex == -1:
        return ''
    apkname = apk[0:lastIndex]
    if apkname:
        return apkname
    else:
        return ''
    pass


# 同步队列
def syncQueueControl():
    startTime = datetime.datetime.now()
    sourceApkList = os.listdir(sourceApkPath)
    for apk in sourceApkList:
        if apk.find('.DS_Store') > -1:
            continue
        apkname = getApkFileName(apk)
        if not apkname:
            print('读取apks文件夹下apk文件出错')
            continue
        getApkFileName(apk)
        configFilePath(apkname)
        generateDict(apkname)
        if decompile(apk):
            modifyapp(apkname)

    endTime = datetime.datetime.now()
    print("all work is done! 总耗时/秒：", (endTime - startTime).total_seconds())
    pass


def main():
    syncQueueControl()
    pass


if __name__ == '__main__':
    main()
