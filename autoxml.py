#!/usr/bin/env python
# coding=utf-8
# Author   :  yanke
# Date     :  2019-07-126
# function :  1. decompile apks 2. modify the AndroidManifest.xml file
#          :  3. recompile the apks


import datetime
import json
import os
import platform
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
from enum import Enum
from typing import List

import LogUtil
import wrapper
from lxml import etree
from config import baseAbsPath
from config import local_config
import logging

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
# 十六进制颜色值正则表达式   8位是带透明度的ARGB值，6位和3位是RGB值
# 以#开头，后面是数字和a-f的字符（大写或小写），这个值是8位、6位或3位。要匹配一个3为是为了符合css颜色的简写规则："#abc"=="#aabbcc"
COLOR_HEX_REGULAR = '^#([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3})$'

Leave_Type = Enum('Leave_Type', ('goon', 'exit'))

apkPath = baseAbsPath + 'generateAPK/apkOut/'
sourceApkPath = baseAbsPath + 'generateAPK/apks/'
recompileApkPath = baseAbsPath + 'generateAPK/recompileApk/'
repackagedAppPath = baseAbsPath + 'generateAPK/repackage/repackagedAPK/'
matchJsonFile = baseAbsPath + 'generateAPK/matchtest.json'
xmlConfigPath = baseAbsPath + 'generateAPK/config.xml'

ELEMENT_TAG_APPLICATION_ID = 'application-id'
ELEMENT_TAG_THEME = 'theme'
ELEMENT_TAG_SUBJECT_COLOR = 'subject-color'
ELEMENT_TAG_NOTIFICATION_COLOR = 'notification-color'
ELEMENT_TAG_APP_NAME = 'app-name'
ELEMENT_TAG_APP_ICON = 'app-icon'
ELEMENT_TAG_SPLASH_ICON = 'splash-icon'
ELEMENT_TAG_UMENG_CHANNEL = 'umeng-channel'
ELEMENT_TAG_APP_VERSION = 'app-version'
ELEMENT_TAG_DOMAIN_GROUP = 'domain-group'
ELEMENT_TAG_SERVER_HOST = 'server-host'
ELEMENT_TAG_SERVER_HOST_TEMP = 'server-host-temp'
ELEMENT_TAG_RETRIEVE_HOST = 'retrieve-host'
ELEMENT_TAG_RETRIEVE_HOST_TEMP = 'retrieve-host-temp'

THEME_COLOR_SUBJECT = 'subject-color'
THEME_COLOR_NOTIFICATION = 'notification-color'

NAMESPACE_MANIFEST = 'http://schemas.android.com/apk/res/android'

# match.json中package_info列表下jsonObject中的dict
domain = {
    ELEMENT_TAG_SERVER_HOST: 'SERVER_HOST',
    ELEMENT_TAG_SERVER_HOST_TEMP: 'SERVER_HOST_TEMP',
    ELEMENT_TAG_RETRIEVE_HOST: 'RETRIEVE_HOST',
    ELEMENT_TAG_RETRIEVE_HOST_TEMP: 'RETRIEVE_HOST_TEMP'
}

drawable_replaced = False

boss2 = {}

# 本地配置
# local_config = {
#     "drawable_path": '',  # 项目的资源目录
#     "local_drawable_path": baseAbsPath + "generateAPK/pics",  # 本地的资源目录
#     "strings_xml": '',  # values下strings.xml
#     "colors_xml": '',  # values下color.xml
#     "manifest_xml": ''  # AndroidManifest.xml
# }

# 动态生成当前每个不同项目包名,key为文件夹目录(apkOut下)名称,value是当前包名
current_packages = {

}

drawable_path = {
    'ic_launcher': ['mipmap-', 'logo1'],
    'splash_launcher': ['drawable-', 'startload_page_picture_new']
}
drawable_dict = {
    ELEMENT_TAG_APP_ICON: ['mipmap-', 'logo1'],
    ELEMENT_TAG_SPLASH_ICON: ['drawable-', 'startload_page_picture_new']
}

import sourcecache

# json字段和colors字段映射
theme = {
    ELEMENT_TAG_SUBJECT_COLOR: 'subject_color',
    ELEMENT_TAG_NOTIFICATION_COLOR: 'custom_notification_layout_color'
}


# -r 阻止反编译resource，不修改resources.arsc，若仅仅修改java（smail），建议使用该选项。
def deCompileExceptionHandle(apk):
    print('反编译失败')
    cmd = "echo {0}>>{1}".format(apk, "反编译失败")
    os.system(cmd)
    pass


def decompile(apkname):
    apk = apkname + '.apk'
    eachappPath = os.path.join(sourceApkPath, apk)
    deCompileCompletehPath = os.path.join(apkPath, apkname)
    sys = platform.system()
    print('开始反编译')
    if sys.find('Windows') > -1:
        cmd = "apktool d -f -s -o {0} {1} <nul".format(deCompileCompletehPath, eachappPath)
    else:
        cmd = "apktool d -f -s -o {0} {1}".format(deCompileCompletehPath, eachappPath)
    try:
        os.system(cmd)
        # 检查反编译文件是否存在标识反编译是否真正完成，避免未进入except的反编译失败场景
        if os.path.exists(deCompileCompletehPath):
            set_current_package(apkname)
            sourcecache.backup(apkname)
            print('完成反编译')
            return True
        else:
            cmd = "echo {0}>>{1}".format(eachappPath, "反编译失败")
            os.system(cmd)
            return False

    except Exception as e:
        cmd = "echo {0}>>{1}".format(eachappPath, "反编译失败")
        os.system(cmd)
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


def recompile2(is_recovery: bool, appname, appicon, apkname, splash_pic_name, umeng_channel):
    try:
        apkList = os.listdir(apkPath)
        print('开始重新编译回包')
        for apk in apkList:
            if apk.find('.DS_Store') > -1:
                continue
            if not apkname == apk:
                continue
            eachapkPath = os.path.join(apkPath, apk)
            output_apk_name = wrapper.Name_family.Builder().appname(appname).splash_picname(splash_pic_name).app_icon(appicon).umeng_channel(umeng_channel).build().append()
            apkOutPath = recompileApkPath + apkname + os.sep + boss2[ELEMENT_TAG_APPLICATION_ID] + os.sep + output_apk_name + '.apk'
            sys = platform.system()
            if sys.find('Windows') > -1:
                cmd = "apktool b -f -o {0} {1} <nul".format(apkOutPath, eachapkPath)
            else:
                cmd = "apktool b -f -o {0} {1}".format(apkOutPath, eachapkPath)

            os.system(cmd)
            if is_recovery:
                set_current_package(apkname)
                sourcecache.recovery(apkname)
            print('完成重新编译回包')
    except Exception as e:
        LogUtil.error('重新编译回包失败')
        logging.exception(e)
        cmd = "echo {0}>>{1}".format(apkOutPath, "重新编译回包失败")
        os.system(cmd)
        raise

    pass


# 处理3、6位rgb颜色值
def obtain_color(color_value):
    if len(color_value) == 6:
        color = ''.join(['#ff', color_value])
    elif len(color_value) == 3:
        char_double_list = ['#']
        for char in color_value:
            char_double_list.append(char * 2)
        color = ''.join(char_double_list)
    else:
        color = '#' + color_value
    return color
    pass


def replace_real_skin(key, color_except_prefix):
    print('开始替换主题颜色')
    num = 0
    tree = ET.parse(local_config['colors_xml'])
    root = tree.getroot()
    for child in root.findall('color'):
        if child.attrib['name'] == theme[key]:
            child.text = obtain_color(color_except_prefix)
            num += 1

    if num == 1:
        tree.write(local_config['colors_xml'], "UTF-8")
        print('完成替换主题颜色')
    else:
        LogUtil.warning('在colors.xml中没有定义subject_color和notification_color，导致无法替换，请检查colors.xml文件')
    pass


# 替换主题color
def replace_theme2():
    try:
        if ELEMENT_TAG_THEME not in boss2:
            return

        theme_dict = boss2[ELEMENT_TAG_THEME]

        for k, v in theme_dict.items():
            if not v:
                continue
            # color_except_prefix标识除去'#'前缀的颜色值
            if re.match(COLOR_HEX_REGULAR, v) is None:
                LogUtil.error('十六进制主题颜色值不正确,请检查')
                sys.exit()

            color_except_prefix = v[1:len(v)]
            replace_real_skin(k, color_except_prefix)
    except Exception as e:
        logging.exception(e)
        raise
    pass


# 更改包名
def replace_applicationID2(apkname):
    target_applicationid = boss2[ELEMENT_TAG_APPLICATION_ID]
    if not target_applicationid:
        return

    print('开始替换包名流程')

    current_package = current_packages[apkname]
    manifest_xml = local_config['manifest_xml']
    grammar = '//*[starts-with(@*,{package})]'.format(package=current_package)

    try:
        tree = etree.parse(manifest_xml)
        doc = tree.xpath(grammar)
        for ele in doc:
            attributes = ele.attrib
            for n in attributes.items():
                if n[1].startswith(current_package):
                    newValue = n[1].replace(current_package, target_applicationid)
                    ele.set(n[0], newValue)
        tree.write(manifest_xml, pretty_print=True, encoding='utf-8', xml_declaration=True)
        set_current_package(apkname, target_applicationid)
        print('完成包名替换流程')
    except:
        LogUtil.error('包名替换流程异常')
        sys.exit()
    pass


def replace_umeng_channel(umeng_channel: str):
    # //title[@lang='eng']
    try:
        print('开始友盟渠道号替换流程')
        namespace_in_attrib_key = '{' + NAMESPACE_MANIFEST + '}'
        etree.register_namespace('android', NAMESPACE_MANIFEST)

        success = False
        manifest_xml = local_config['manifest_xml']
        grammar = '//meta-data[@*]'
        tree = etree.parse(manifest_xml)
        doc = tree.xpath(grammar)
        umeng_channel_ele = None
        for ele in doc:
            for n in ele.attrib.items():
                if not n[1].startswith('UMENG_CHANNEL'):
                    continue
                umeng_channel_ele = ele
                break
            if umeng_channel_ele is not None:
                break

        if umeng_channel_ele is not None:
            for m in umeng_channel_ele.attrib.items():
                if m[0].endswith('value'):
                    umeng_channel_ele.set(m[0], umeng_channel)
                    success = True
        if not success:
            raise RuntimeError('友盟渠道号替换流程异常')
        else:
            tree.write(manifest_xml, pretty_print=True, encoding='utf-8', xml_declaration=True)
            print('完成友盟渠道号替换流程')
    except Exception as e:
        logging.exception(e)
        LogUtil.error('友盟渠道号替换流程异常')
        sys.exit()

    pass


def replace_umeng_channel2(umeng_channel: str):
    # //title[@lang='eng']
    try:
        print('开始友盟渠道号替换流程')
        namespace_in_attrib_key = '{' + NAMESPACE_MANIFEST + '}'
        etree.register_namespace('android', NAMESPACE_MANIFEST)

        success = False
        manifest_xml = local_config['manifest_xml']
        grammar = '//meta-data[@*]'
        tree = etree.parse(manifest_xml)
        doc = tree.xpath(grammar)
        for ele in doc:
            if ele.attrib[namespace_in_attrib_key + 'name'] == 'UMENG_CHANNEL':
                ele.attrib[namespace_in_attrib_key + 'value'] = umeng_channel
                success = True

        if not success:
            raise RuntimeError('友盟渠道号替换流程异常')
        else:
            tree.write(manifest_xml, pretty_print=True, encoding='utf-8', xml_declaration=True)
            print('完成友盟渠道号替换流程')
    except Exception as e:
        logging.exception(e)
        raise
    pass


def replace_domain(key, value: str):
    try:
        print('开始替换domain: ' + domain[key])
        isFinish = False
        tree = ET.parse(local_config['strings_xml'])
        root = tree.getroot()
        for child in root.findall('string'):
            if child.attrib['name'] == domain[key]:
                child.text = value.strip()
                isFinish = True

        if isFinish:
            tree.write(local_config['strings_xml'], "UTF-8")
            print('完成替换domain: ' + domain[key])
        else:
            raise RuntimeError('在strings.xml中没有定义' + domain[key] + '，导致无法替换，请检查strings.xml文件')
    except Exception as e:
        logging.exception(e)
        raise
    pass


def replace_app_version(version_code: str):
    try:
        print('开始版本号替换流程')
        namespace = '{' + NAMESPACE_MANIFEST + '}'
        ET.register_namespace("android", NAMESPACE_MANIFEST)
        tree = ET.parse(local_config['manifest_xml'])
        root = tree.getroot()
        root.attrib[namespace + 'versionCode'] = version_code
        root.attrib[namespace + 'versionName'] = ('.'.join(version_code))
        tree.write(local_config['manifest_xml'], "UTF-8")
        print('完成版本号替换流程')
    except Exception as e:
        logging.exception(e)
        raise
    pass


def modifyapp2(apkname):
    replace_applicationID2(apkname)

    replace_theme2()

    if ELEMENT_TAG_APP_NAME in boss2:
        replace_app_name(boss2[ELEMENT_TAG_APP_NAME])
    if ELEMENT_TAG_APP_ICON in boss2:
        icon_wrapper = wrapper.Icon(ELEMENT_TAG_APP_ICON, boss2[ELEMENT_TAG_APP_ICON], drawable_dict[ELEMENT_TAG_APP_ICON][1], drawable_dict[ELEMENT_TAG_APP_ICON][0])
        replace_drawable2(icon_wrapper)
    if ELEMENT_TAG_SPLASH_ICON in boss2:
        splash_icon_wrapper = wrapper.Icon(ELEMENT_TAG_SPLASH_ICON, boss2[ELEMENT_TAG_SPLASH_ICON], drawable_dict[ELEMENT_TAG_SPLASH_ICON][1], drawable_dict[ELEMENT_TAG_SPLASH_ICON][0])
        replace_drawable2(splash_icon_wrapper)

    if ELEMENT_TAG_APP_VERSION in boss2:
        replace_app_version(boss2[ELEMENT_TAG_APP_VERSION])

    if ELEMENT_TAG_DOMAIN_GROUP in boss2:
        domain_dict: dict = boss2[ELEMENT_TAG_DOMAIN_GROUP]
        for k, v in domain_dict.items():
            replace_domain(k, v)

    if ELEMENT_TAG_UMENG_CHANNEL in boss2:
        umeng_channel_list: List[str] = boss2[ELEMENT_TAG_UMENG_CHANNEL]
        for umeng_channel in umeng_channel_list:
            LogUtil.error('umeng_channel  ' + umeng_channel)
            replace_umeng_channel2(umeng_channel)
            index = umeng_channel_list.index(umeng_channel)
            # 使用三木运算符
            is_recovery = False if (index < len(umeng_channel_list) - 1) else True
            recompile2(is_recovery, boss2[ELEMENT_TAG_APP_NAME], icon_wrapper.target_icon_name, apkname, splash_icon_wrapper.target_icon_name, umeng_channel)

    else:
        recompile2(True, boss2[ELEMENT_TAG_APP_NAME], icon_wrapper.target_icon_name, apkname, splash_icon_wrapper.target_icon_name)

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
    try:
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
    except Exception as e:
        logging.exception(e)
        raise
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
                LogUtil.error(target_file_path)
                os.remove(sourcedir)
                shutil.copy(target_file_path, os.path.split(sourcedir)[0])
            global drawable_replaced
            drawable_replaced = True
            print('图片资源替换完成')
    pass


def replace_drawable2(icon_wrapper):
    print("开始替换图片资源...")
    # 从pics文件夹下搜索指定name图片文件
    try:
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

                tmp_new_target_file_path = tmpdir + os.sep + icon_wrapper.source_icon_name + os.path.splitext(target_file)[1]

                os.rename(tmp_target_file_path, tmp_new_target_file_path)
                search_drawable_in_project(local_config["drawable_path"], tmp_new_target_file_path, icon_wrapper)
                global drawable_replaced
                if not drawable_replaced:
                    drawable_replaced = False
                    raise RuntimeError('图片替换失败,没有找到要替换的图片,请检查应用内和脚本中定义的图片名称')
        else:
            # pics中没有给定target_icon_name目标的图片资源
            raise RuntimeError('pics文件夹中没有config配置文件中指定的图片资源,请检查')
    except Exception as e:
        logging.exception(e)
        raise
        pass


# 根据match.json匹配文件生成字典
def loadconfig():
    print('读取match.json开始')
    try:
        with open(matchJsonFile, "r", encoding='utf-8') as f:
            global founder
            founder = json.load(f)
        print('读取match.json完成')
    except Exception as e:
        LogUtil.error('读取match.json异常,请检查文件')
        LogUtil.error(e)
        return False
    pass


def loadconfig2():
    print('读取config.xml')
    try:
        tree = ET.parse(xmlConfigPath)
        return tree
    except Exception as e:
        LogUtil.error('读取config.xml异常,请检查文件')
        raise
    pass


def configFilePath(apkname):
    if apkname:
        local_config['drawable_path'] = apkPath + apkname + "/res"
        local_config['strings_xml'] = apkPath + apkname + "/res/values/strings.xml"
        local_config['colors_xml'] = apkPath + apkname + "/res/values/colors.xml"
        local_config['manifest_xml'] = apkPath + apkname + "/AndroidManifest.xml"
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


# 获取apks下apk
def obtain_apk():
    sourceApkList = os.listdir(sourceApkPath)
    for f in sourceApkList:
        if f.find('.DS_Store') > -1:
            continue
        if not f.endswith('.apk'):
            continue
        apk = f
        break
    return apk

    pass


# 设置当前包名
def set_current_package(apkname, application_id=None):
    if application_id is None:
        tree = ET.parse(local_config['manifest_xml'])
        root = tree.getroot()
        attrs = root.attrib
        current_packages[apkname] = attrs['package']
    else:
        current_packages[apkname] = application_id
    pass


# 去掉空格、换行符
def format_something(text: str):
    if text:
        text = text.strip()
        text = text.replace(' ', '')
        text = text.replace('\n', '')

    return text

    pass


# 解析xml
def parseXML(decompile_element: ET.Element):
    application_id_element = decompile_element.find(ELEMENT_TAG_APPLICATION_ID)
    if application_id_element is not None and isinstance(application_id_element, ET.Element):
        application_id_text: str = format_something(application_id_element.text)
        if application_id_text and len(application_id_text) > 0:
            boss2[ELEMENT_TAG_APPLICATION_ID] = application_id_text

    theme_element = decompile_element.find(ELEMENT_TAG_THEME)
    if theme_element is not None and isinstance(theme_element, ET.Element):
        isReplace: str = format_something(theme_element.attrib['isReplace'])
        if isReplace and len(isReplace) > 0 and isReplace.startswith('true'):
            subject_color_element = theme_element.find(ELEMENT_TAG_SUBJECT_COLOR)
            notification_color_element = theme_element.find(ELEMENT_TAG_NOTIFICATION_COLOR)
            theme = {}
            if subject_color_element is not None and isinstance(subject_color_element, ET.Element):
                subject_color_text: str = format_something(subject_color_element.text)
                if subject_color_text and len(subject_color_text) > 0:
                    theme[ELEMENT_TAG_SUBJECT_COLOR] = subject_color_text

            if notification_color_element is not None and isinstance(notification_color_element, ET.Element):
                notification_color_text: str = format_something(notification_color_element.text)
                if notification_color_text and len(notification_color_text) > 0:
                    theme[ELEMENT_TAG_NOTIFICATION_COLOR] = notification_color_text
            if theme.__len__() > 0:
                boss2[ELEMENT_TAG_THEME] = theme

    app_name_element = decompile_element.find(ELEMENT_TAG_APP_NAME)
    if app_name_element is not None and isinstance(app_name_element, ET.Element):
        app_name_text: str = format_something(app_name_element.text)
        if app_name_text is not None and len(app_name_text) > 0:
            boss2[ELEMENT_TAG_APP_NAME] = app_name_text

    app_icon_element = decompile_element.find(ELEMENT_TAG_APP_ICON)
    if app_icon_element is not None and isinstance(app_icon_element, ET.Element):
        app_icon_text: str = format_something(app_icon_element.text)
        if app_icon_text is not None and len(app_icon_text) > 0:
            boss2[ELEMENT_TAG_APP_ICON] = app_icon_text

    splash_icon_element = decompile_element.find(ELEMENT_TAG_SPLASH_ICON)
    if splash_icon_element is not None and isinstance(splash_icon_element, ET.Element):
        splash_icon_text: str = format_something(splash_icon_element.text)
        if splash_icon_text is not None and len(splash_icon_text) > 0:
            boss2[ELEMENT_TAG_SPLASH_ICON] = splash_icon_text

    app_version_element = decompile_element.find(ELEMENT_TAG_APP_VERSION)
    if app_version_element is not None and isinstance(app_version_element, ET.Element):
        app_version_text: str = format_something(app_version_element.text)
        if app_version_text and len(app_version_text) > 0:
            boss2[ELEMENT_TAG_APP_VERSION] = app_version_text

    # 支持中英文逗号
    umeng_channel_element = decompile_element.find(ELEMENT_TAG_UMENG_CHANNEL)
    if umeng_channel_element is not None and isinstance(umeng_channel_element, ET.Element):
        umeng_channel_text: str = umeng_channel_element.text
        umeng_channel_text = umeng_channel_text.replace('，', ',')
        umeng_channel_text = format_something(umeng_channel_text)
        if umeng_channel_text is not None and len(umeng_channel_text) > 0:
            boss2[ELEMENT_TAG_UMENG_CHANNEL] = umeng_channel_text.split(',')

    domain_group_element = decompile_element.find(ELEMENT_TAG_DOMAIN_GROUP)
    if domain_group_element is not None and isinstance(domain_group_element, ET.Element):
        domain = {}
        domain_temp = [ELEMENT_TAG_SERVER_HOST, ELEMENT_TAG_SERVER_HOST_TEMP, ELEMENT_TAG_RETRIEVE_HOST, ELEMENT_TAG_RETRIEVE_HOST_TEMP]
        child: ET.Element
        for i in range(len(list(domain_group_element))):
            child = list(domain_group_element)[i]
            content = format_something(child.text)
            if domain_temp.__contains__(child.tag) and len(content) > 0:
                domain[child.tag] = content
            if i + 1 == len(list(domain_group_element)):
                boss2[ELEMENT_TAG_DOMAIN_GROUP] = domain

    pass


def execute(decompile_element: ET.Element, apkname):
    parseXML(decompile_element)
    modifyapp2(apkname)

    pass


def control_package():
    startTime = datetime.datetime.now()
    sourceApkList = os.listdir(sourceApkPath)
    try:
        element_tree = loadconfig2()
        if element_tree is None:
            raise RuntimeError('config配置文件为空')

        first_floor_child: ET.Element
        for first_floor_child in element_tree.getroot().findall('decompile'):
            boss2.clear()
            target_attrib_value = first_floor_child.attrib['target']
            if not target_attrib_value:
                LogUtil.error('target属性不能为空,用来标识要反编译的apk,请检查config.xml')
                sys.exit()
            configFilePath(target_attrib_value)
            decompiled_folders: List[str] = os.listdir(apkPath)
            is_exist_in_apkOut = decompiled_folders.__contains__(target_attrib_value)
            # if not is_exist_in_apkOut:
            is_exist_in_apks = sourceApkList.__contains__(target_attrib_value + '.apk')
            if not is_exist_in_apks:
                LogUtil.error('apks文件夹下没有' + target_attrib_value + '这个apk文件,请检查')
                sys.exit()
            if not decompile(target_attrib_value):
                LogUtil.error(target_attrib_value + '反编译失败')
                sys.exit()
            execute(first_floor_child, target_attrib_value)
            # else:
            #     execute(first_floor_child, target_attrib_value)

        endTime = datetime.datetime.now()
        print("all work is done! 总耗时/秒：", (endTime - startTime).total_seconds())
    except Exception as e:
        logging.exception(e)
    finally:
        # 删除tmp缓存文件夹
        sourcecache.clear_tmp()
        input('请按下任意键退出控制台窗口...')

    pass


def main():
    control_package()
    pass


if __name__ == '__main__':
    main()
