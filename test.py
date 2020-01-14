import os
import json
import sys
import traceback
from typing import List

import lxml
from lxml import etree
import wrapper
import LogUtil
from urllib.parse import urlparse

t = ['见面', '相亲', '本地寻爱', '附近约会']

matchFile = 'generateAPK/match.txt'
oneFile = 'generateAPK/loading1.jpg'
one2File = 'generateAPK/recompileApk/loading1.png'
matchJsonFile = 'generateAPK/match.json'
matchJsonFile22 = 'generateAPK/matchtest2.json'
manifest = 'generateAPK/apkOut/10000_TCYJClient-skinPeeler-release_v3.3.1_20191017/AndroidManifest.xml'
xmlFile = 'Manifest.xml'
xmlFile3 = '222.xml'
match = {}

apkPath = 'generateAPK/apkOut/'
xmlConfigPath = 'generateAPK/config.xml'

appNameList = []

dict22 = {
    t[0]: ('见面',),
    t[1]: ('相亲', '333', '444', '666'),
    t[2]: ('见面',),
    t[3]: ('555',)
}
dict1 = {
    '见面': ('见面',),
    '相亲': ('相亲', '333', '444', '666'),
    '本地寻爱': ('见面',),
    '附近约会': ('555',)
}

testDir = 'generateAPK'
testFile = 'generateAPK/pics/000.png'

local_config = {
    "drawable_path": '',  # 项目的资源目录
    "local_drawable_path": "generateAPK/pics",  # 本地的资源目录
    "strings_xml": '',  # values下strings.xml
    "line_number_record": 0
}


def generateDict2():
    print('读取match.txt开始')
    try:
        with open(matchFile, "r", encoding="utf-8", errors='ignore') as f:
            lineData = f.readlines()
            s = lineData.split('*********')
            s1 = f.split('*********')
            print(s1)
            # for line in lineData:
            #     tmpline = line.strip()
            #     key, value = tmpline.split('=')
            #     logoList = value.split(',')
            #     appNameList.append(key)
            #     if not key in match:
            #         match[key] = logoList
        print('读取match.txt完成')
    except:
        print('读取match.txt异常,请检查文件')
    pass


def dictQuery():
    for m in appNameList:
        print(m)
    pass


# generateDict()

# dictQuery()

import tempfile
import os
import shutil

sourceApkPath = 'generateAPK/apks/'


def createDir():
    tmp = ''
    with tempfile.TemporaryDirectory() as tmpdir:
        print('Created temporary directory ', tmpdir)
        tmp = tmpdir
        print(os.path.exists(tmpdir))
        shutil.copy(matchFile, tmpdir)
        print(os.path.exists(tmpdir + os.sep + 'match.txt'))

    print(tmp)
    print(os.path.exists(tmp))
    pass


# createDir()
def copy():
    src = testFile
    dst = testDir
    shutil.copy2(src, dst)

    pass


def syncQueueControl():
    sourceApkList = os.listdir(sourceApkPath)
    for apkName in sourceApkList:
        if apkName.find('.DS_Store') > -1:
            continue
        print('输出：  ' + apkName)

    print("all work is done!")
    pass


# 根据读取appName与logo对应文件match.txt生成python字典
def generateDict():
    print('读取match.txt开始')
    try:
        with open(matchFile, "r", encoding="utf-8", errors='ignore') as f:
            lineData = f.readlines()
            startLineIndex = local_config['line_number_record']
            # startLineIndex = lineNumber
            indexList = [i for i in range(len(lineData)) if lineData[i].startswith('***')]
            print('包含指定行分隔符的行下标：', indexList)
            for j in range(len(indexList) + 1):
                if (not startLineIndex == 0) and (j > 0):
                    startLineIndex = indexList[j - 1] + 1

                if j == len(indexList):
                    endLineIndex = len(lineData) + 1
                else:
                    endLineIndex = indexList[j]

                for line in lineData[startLineIndex:endLineIndex]:
                    startLineIndex += 1
                    if line in ['\n', '\r\n']:
                        continue
                    if line.strip() == "":
                        continue
                    tmpline = line.strip()
                    # if tmpline.startswith('***'):
                    #     # lineData[0, lineNumber]
                    #     local_config['line_number_record'] = int(lineNumber)
                    #     print('行号   ' + str(local_config['line_number_record']))
                    #     print('截取内容：', lineData[0:lineNumber])
                    if tmpline.find('=') < 0:
                        continue
                    key, value = tmpline.split('=')
                    key = key.strip()
                    value = value.strip()
                    logoList = value.split(',')
                    appNameList.append(key)
                    if not key in match:
                        match[key] = logoList
                print(match)
                match.clear()
        print('读取match.txt完成')
    except:
        print('读取match.txt异常,请检查文件')
    pass


# 根据读取appName与logo对应文件match.txt生成python字典
def queryIndex(startLineIndex, indexList):
    for i in range(indexList):
        if startLineIndex > indexList[i] and startLineIndex < indexList[i + 1]:
            return indexList[i + 1]
    pass


def generateDict3():
    print('读取match.txt开始')
    try:
        with open(matchJsonFile, "r", encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
            handleJson(data)

        print('读取match.txt完成')
    except Exception as e:
        print('读取match.txt异常,请检查文件')
        print(traceback.print_exc())
    pass


def handleJson(data):
    for (k, v) in data.items():
        if isinstance(v, dict):
            for (k1, v1) in v.items():
                if isinstance(v1, list):
                    for listitem in v1:
                        for (k1, v1) in listitem.items():
                            print('key :', k1, '  value: ', v1)
                            k1 = k1.strip()
                            appNameList.append(k1)
                            if not k1 in match:
                                match[k1] = v1
    print('appNameList: ', appNameList)
    print('match: ', match)

    pass


def dirtest():
    baseAbsPath = os.path.abspath(sys.argv[0])
    dirpath = os.path.dirname(baseAbsPath)
    print('dirpath:  ', dirpath)
    pass


def testPoint():
    apk = '10000_TCYJClient-skinPeeler-release_v3.3.1_20190806.apk'
    lastIndex = apk.rindex('.')

    apkname = apk[0:lastIndex]
    print(apkname)
    pass


def create_output_apk_name(name):
    print(name.splash_pic_name)
    print(name.apk_name)
    pass


def testListDir():
    create_output_apk_name(wrapper.Name_family.Builder().apkname('111').splash_picname('222').build())
    pass


def method1():
    pass


def create_output_apk_name():
    output_apk_name = ''

    output_apk_name.join(['111'])

    print(output_apk_name)

    output_apk_name.join(['222'])

    print(output_apk_name)

    # print('333')

    print('-'.join(['aa']))

    LogUtil.error('图片资源替换完成')
    LogUtil.warning('图片资源替换完成')

    pass


import xmltodict
import json
import collections
import xml.etree.ElementTree as ET

xml2file = '111.xml'


def paresXML():
    with open(xmlFile) as f:
        manifest = xmltodict.parse(f.read(), encoding='UTF-8')
        # print(dict(manifest))
        # json.loads(manifest, object_pairs_hook=collections.OrderedDict)
        print(xmltodict.unparse(manifest, encoding='UTF-8'))
    pass


# from lxml import etree
# import lxml

# ns = {"d": "http://schemas.android.com/apk/res/android"}

path = '//*[starts-with(@*,"com.keyou.jxyhclient")]'
path2 = '//*[contains(@*,{package})]'.format(package='com.keyou.jxyhclient')
path3 = '//*[@d:name="UMENG_CHANNEL"]'
print(path3)


def paresXML2():
    # print(path2)
    tree = etree.parse(xmlFile)
    doc = tree.xpath(path2)
    for ele in doc:
        # print(ele)
        attributes = ele.attrib
        for n in attributes.items():
            print(n)
            if n[1].startswith('com.keyou.jxyhclient'):
                newValue = n[1].replace('com.keyou.jxyhclient', 'yanke123')
                ele.set(n[0], newValue)
                # print(ele)
    # tree.write(xmlFile, pretty_print=True, encoding='utf-8', xml_declaration=True)
    pass


def paresXML4():
    # print(path2)
    tree = etree.parse(xmlFile)
    doc = tree.xpath(path3, namespaces={'d': 'http://schemas.android.com/apk/res/android'})
    print(doc)
    for ele in doc:
        attributes = ele.attrib
        print(ele)
    pass


# 设置当前包名
def set_current_package():
    tree = ET.parse(xmlFile)
    root = tree.getroot()
    attrs = root.attrib
    local_config['current_package_name'] = attrs['package']
    print(local_config['current_package_name'])

    pass


def paresXML3():
    d = False
    for i in range(2):
        print(i)
        # if d:
        #     break
        # else:
        #     break
    pass


# from auto import local_config

grammar = {
    'manifest_package': '/manifest[@package]'
}


def readxml():
    manifest = 'generateAPK/apkOut/10000_TCYJClient-skinPeeler-publish_v3.3.1_20190822/AndroidManifest.xml'
    tree = etree.parse(manifest)
    attr_value = tree.xpath(grammar['manifest_package'])
    # print(attr_value.index('package'))
    for ele in attr_value:
        attributes = ele.attrib
        # k=attributes.get('package')
        # for n in attributes.items():
        k = attributes.has_key('package')
        print(k)

    pass


newpath = 'generateAPK/source/'

import datetime


def copytest():
    # if not os.path.exists(newpath) or not os.path.isdir(newpath):
    #     os.mkdir(newpath)
    startTime = datetime.datetime.now()
    path = 'generateAPK/apkOut/10000_TCYJClient-skinPeeler-publish_v3.3.1_20190822/res'
    dst = shutil.copytree(path, newpath)
    print(222)
    print(dst)

    endTime = datetime.datetime.now()
    print("all work is done! 总耗时/秒：", (endTime - startTime).total_seconds())

    pass


app = []

import logging


def dicttest():
    # list = ['1', '2', '3']
    # print(list.__contains__('3'))
    try:
        raise RuntimeError('999')
    except Exception as e:
        # logging.error('2222')
        raise

    pass


def dicy():
    # print(dicy1())
    k = 'start.9.png'
    v = os.path.split(k)
    print(v)
    pass


def dicy1():
    print('111')
    return dicy2()
    pass


def dicy2():
    print('2222')
    pass


if __name__ == '__main__':
    # generateDict()
    # generateDict3()
    # with open(matchJsonFile, encoding='utf-8', errors='ignore') as f:
    #     data = json.load(f)
    # handleJson(data)

    # dirtest()
    # testPoint()
    # testListDir()
    # create_output_apk_name()
    # paresXML2()

    # paresXML4()
    # copytest()
    # readxml()
    dicy()
