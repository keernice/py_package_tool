import os
import json
import sys
import traceback

t = ['见面', '相亲', '本地寻爱', '附近约会']

matchFile = 'generateAPK/match.txt'
matchJsonFile = 'generateAPK/match.json'
match = {}

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


if __name__ == '__main__':
    # generateDict()
    # generateDict3()
    # with open(matchJsonFile, encoding='utf-8', errors='ignore') as f:
    #     data = json.load(f)
    # handleJson(data)

    # dirtest()
    testPoint()
