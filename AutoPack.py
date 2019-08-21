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
import wrapper

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
matchJsonFile = baseAbsPath + 'generateAPK/match.json'

# 声明全局字典,通过读取match.txt为字典赋值
match = {}
# mactch字典中的key列表
app_name_list = []

# 本地配置
local_config = {
    "drawable_path": '',  # 项目的资源目录
    "local_drawable_path": baseAbsPath + "generateAPK/pics",  # 本地的资源目录
    "strings_xml": ''  # values下strings.xml
}

# 项目中的图片资源
project_drawable = {
    "logo1": "logo1.png"  # 应用图标
}

drawable_path = {
    'ic_launcher': ['mipmap-', 'logo1'],
    'splash_launcher': ['drawable-', 'startload_page_picture_new']
}


# -r 阻止反编译resource，不修改resources.arsc，若仅仅修改java（smail），建议使用该选项。
def deCompileExceptionHandle(apk):
    print('反编译失败')
    cmd = "echo {0}>>{1}".format(apk, "反编译失败")
    os.system(cmd)
    pass


def decompile(apk):
    apkname = obtain_apk_name(apk)
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


# 生成反编译输出apk文件的name
def create_output_apk_name(name_family):
    output_apk_name = []
    if name_family.appname:
        output_apk_name.append(name_family.appname)
    if name_family.splash_pic_name:
        output_apk_name.append(name_family.splash_pic_name)
    if name_family.app_icon:
        output_apk_name.append(name_family.app_icon)

    if len(output_apk_name) > 0:
        return '-'.join(output_apk_name)

    return ''

    pass


def recompile(appname, appicon, apkname, splash_pic_name):
    apkList = os.listdir(apkPath)
    print('开始重新编译回包')
    for apk in apkList:
        if apk.find('.DS_Store') > -1:
            continue
        if not apkname == apk:
            continue
        eachapkPath = os.path.join(apkPath, apk)
        output_apk_name = create_output_apk_name(
            wrapper.Name_family.Builder().appname(appname).splash_picname(splash_pic_name).app_icon(appicon).build())
        # apkOutPath = recompileApkPath + apkname + os.sep + appname + '-' + splash_pic_name + '-' + appicon + '.apk'
        apkOutPath = recompileApkPath + apkname + os.sep + output_apk_name + '.apk'
        sys = platform.system()
        if sys.find('Windows') > -1:
            cmd = "apktool b {0} -f -o {1} <nul".format(eachapkPath, apkOutPath)
        else:
            cmd = "apktool b {0} -f -o {1}".format(eachapkPath, apkOutPath)
        try:
            os.system(cmd)
            print('完成重新编译回包')
            input("下一个...............")
        except:
            print('重新编译回包异常')
            cmd = "echo {0}>>{1}".format(apkOutPath, "重新编译回包异常")
            os.system(cmd)
            continue
    pass


# 遍历修改替换apk反编译项目文件夹内容(limit res dir)
def modifyapp(apkname):
    icon_wrapper_list = []
    for name in app_name_list:
        if name in match:
            replace_app_name(name)
            icon_list = match.get(name)
            for o in range(len(icon_list)):
                icon_item_dict = icon_list[o]
                if len(icon_item_dict) == 0:
                    continue
                # replace_theme()
                print('eeeee   ', icon_item_dict)
                splash_target_icon_name = ''
                if 'splash_launcher' in icon_item_dict:
                    splash_icon_wrapper = wrapper.Icon('splash_launcher', icon_item_dict['splash_launcher'],
                                                       drawable_path['splash_launcher'][1],
                                                       drawable_path['splash_launcher'][0])
                    replace_drawable(splash_icon_wrapper)
                    splash_target_icon_name = splash_icon_wrapper.target_icon_name
                    # icon_wrapper_list.append(splash_icon_wrapper)
                if 'ic_launcher' in icon_item_dict and len(icon_item_dict['ic_launcher']) > 0:
                    for i in range(len(icon_item_dict['ic_launcher'])):
                        icon_wrapper = wrapper.Icon('ic_launcher', icon_item_dict['ic_launcher'][i],
                                                    drawable_path['ic_launcher'][1], drawable_path['ic_launcher'][0])
                        replace_drawable(icon_wrapper)
                        # icon_wrapper_list.append(icon_wrapper)
                        recompile(name, icon_wrapper.target_icon_name, apkname, splash_target_icon_name)
                else:
                    recompile(name, '', apkname, splash_target_icon_name)

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
def replace_app_name(targetAppName):
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
        print('**********在strings.xml中没有定义app_name，导致无法替换，请检查strings.xml文件**********')
    pass


# 查找本地资源文件
def search_drawable_in_local(pic_name):
    pics_path = local_config["local_drawable_path"]
    if os.path.isdir(pics_path):
        # 根据要替换的文件名找到新文件并返回
        file_list = os.listdir(pics_path)
        for file in file_list:
            (filename, extension) = os.path.splitext(file)
            if filename == pic_name:
                return file
    else:
        # 本地资源路径非文件夹
        return
    pass


# 递归替换项目中的资源
def search_drawable_in_project(sourcedir, target_file_path, icon_wrapper):
    if os.path.isdir(sourcedir):
        # 是文件夹，检索文件夹内文件递归
        listdir = os.listdir(sourcedir)
        for dir in listdir:
            if os.path.isdir(dir) and dir.find(icon_wrapper.match_icon_dir) < 0:
                continue
            path = sourcedir + os.sep + dir
            search_drawable_in_project(path, target_file_path, icon_wrapper)
    else:
        # 是文件,判断是否是要复制的文件
        source = os.path.split(sourcedir)
        target = os.path.split(target_file_path)
        source_drawable_name = source[1].split('.')[0]
        target_drawable_name = target[1].split('.')[0]
        if os.path.isfile(sourcedir) and (source_drawable_name == target_drawable_name):
            # 先删除在复制到目录
            if os.path.splitext(target_file_path) == os.path.splitext(sourcedir):
                shutil.copy2(target_file_path, sourcedir)
            else:
                os.remove(sourcedir)
                shutil.copy(target_file_path, os.path.split(sourcedir)[0])
            print('图片资源替换完成')
        return
    pass


# 修改所有资源图片
# 替换掉所有类型的mipmap包下的文件
def replace_drawable(icon_wrapper):
    print("开始替换图片资源...")
    # 从pics文件夹下搜索指定name图片文件
    target_file = search_drawable_in_local(icon_wrapper.target_icon_name)
    if target_file is not None:
        print('targetFile  ' + target_file)
        target_file_path = local_config["local_drawable_path"] + os.sep + target_file
        # 创建临时目录由上下文管理器管理(上下文管理器退出后文件目录会被自动删除)
        with tempfile.TemporaryDirectory() as tmpdir:
            print('Created temporary directory ', tmpdir)
            print(os.path.exists(tmpdir))
            shutil.copy2(target_file_path, tmpdir)
            tmp_target_file_path = tmpdir + os.sep + target_file

            tmp_new_target_file_path = tmpdir + os.sep + icon_wrapper.source_icon_name + os.path.splitext(target_file)[
                1]

            os.rename(tmp_target_file_path, tmp_new_target_file_path)
            search_drawable_in_project(local_config["drawable_path"], tmp_new_target_file_path, icon_wrapper)
    pass


# 根据match.json匹配文件生成字典
def generateDict(apkname):
    print('读取match.json开始')
    try:
        with open(matchJsonFile, "r", encoding='utf-8') as f:
            data = json.load(f)
            handleJson(data, apkname)

        print('读取match.json完成')
    except:
        sys.exit('读取match.json异常,请检查文件')
    pass


def handleJson(data, apkname):
    try:
        app_name_list.clear()
        match.clear()
        for (k, v) in data.items():
            if (apkname in v) and isinstance(v, dict):
                for (k1, v1) in v.items():
                    if (k1 == apkname) and isinstance(v1, list):
                        for item_list in v1:
                            theme_dict = item_list['theme']
                            name = item_list['name']
                            icon_list = item_list['icon']
                            name = name.strip()
                            app_name_list.append(name)
                            if not name in match:
                                match[name] = icon_list

        print('app_name_list: ', app_name_list)
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


def obtain_apk_name(apk):
    lastIndex = apk.rindex('.')
    if lastIndex == -1:
        return ''
    apkname = apk[0:lastIndex]
    if apkname:
        return apkname
    else:
        return ''
    pass


# 初始化
def data_initialization(apkname):
    configFilePath(apkname)
    generateDict(apkname)
    pass


# 同步队列
def syncQueueControl():
    startTime = datetime.datetime.now()
    sourceApkList = os.listdir(sourceApkPath)
    for apk in sourceApkList:
        if apk.find('.DS_Store') > -1:
            continue
        apkname = obtain_apk_name(apk)
        if not apkname:
            print('读取apks文件夹下apk文件出错')
            continue
        data_initialization(apkname)

        if decompile(apk):
            modifyapp(apkname)

    endTime = datetime.datetime.now()
    print("all work is done! 总耗时/秒：", (endTime - startTime).total_seconds())
    input('请按下任意键退出控制台窗口...')
    pass


def main():
    syncQueueControl()
    pass


if __name__ == '__main__':
    main()
