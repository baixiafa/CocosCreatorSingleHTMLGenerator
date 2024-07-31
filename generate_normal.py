# -*- coding:utf-8 -*-
#!/usr/bin/python3

import os
import sys
from html.parser import HTMLParser
import base64
import chardet
import simplejson
import math
from shutil import copyfile

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

settingMatchKey = '{#settings}'
mainMatchKey = '{#main}'
engineMatchKey = '{#cocosengine}'
projectMatchKey = '{#project}'
resMapMatchKey = '{#resMap}'
# ttfMapMatchKey = '{#ttfMap}'
indexInternalKey = "{#indexInternal}"

fileByteList = ['.png', '.jpg', '.mp3', '.ttf', '.plist', 'txt']

base64PrefixList = {
  '.png' : 'data:image/png;base64,',
  '.jpg' : 'data:image/jpeg;base64,',
  '.webp' : 'data:image/webp;base64,',
  '.mp3' : '',
  '.ttf' : '',
  '.plist' : 'data:text/plist;base64,'
}

def read_in_chunks(filePath):
    extName = os.path.splitext(filePath)[1]
    if extName == '.webp':
        with open(filePath, 'rb') as f:
            b64bytes = base64.b64encode(f.read())
            return base64PrefixList[extName] + b64bytes.decode()
    elif extName in fileByteList:
        file_object = open(filePath, 'rb')
        base64Str = base64.b64encode(file_object.read())
        base64Prefix = base64PrefixList[extName]
        if base64Prefix != None:
            base64Str = bytes(base64Prefix, 'utf-8') + base64Str
            return base64Str
    elif extName == '':
        return None

    file_temp = open(filePath, "rb")
    result = chardet.detect(file_temp.read())
    encoding = result['encoding']

    file_object = open(filePath, encoding=encoding, errors='ignore')
    return file_object.read()

def writeToPath(path, data):
    with open(path,'w', encoding='utf-8') as f:
        f.write(data)

def getResMap(jsonObj, path, resPath):
    fileList = os.listdir(path)
    for fileName in fileList:
        absPath = path + '/' + fileName
        if (os.path.isdir(absPath)):
            getResMap(jsonObj, absPath, resPath)
        elif (os.path.isfile(absPath) and absPath.find("main/index.js") == -1):
            dataStr = read_in_chunks(absPath)
            if dataStr != None:
                absPath = absPath.replace(resPath + '/', '')
                jsonObj[absPath] = dataStr

def getResMapScript(resPath):
    jsonObj = {}
    getResMap(jsonObj, resPath, resPath)
    jsonStr = simplejson.dumps(jsonObj)
    resStr = str("window.resMap = ") + jsonStr
    return resStr

# This issue is fixed in Cocos Creator 2.x
def fixEngineError(engineStr):
    newEngineStr = engineStr.replace("t.content instanceof Image", "t.content.tagName === \"IMG\"", 1)
    return newEngineStr

def addPlistSupport(mainStr):
    newMainStr = mainStr.replace("json: jsonBufferHandler,", "json: jsonBufferHandler, plist: jsonBufferHandler,", 1)
    return newMainStr

def integrate(projectRootPath):
    htmlPath = projectRootPath + '/build/web-mobile/index.html'
    newHtmlPath = os.getcwd() + "/playable/index.html"
    settingScrPath = projectRootPath + '/build/web-mobile/src/settings.js'
    mainScrPath = projectRootPath + '/build/web-mobile/main.js'
    engineScrPath = projectRootPath + '/build/web-mobile/cocos2d-js-min.js'
    projectScrPath = projectRootPath + '/build/web-mobile/assets/main/index.js'
    resPath = projectRootPath + '/build/web-mobile/assets'
    indexInternalScrPath = projectRootPath + '/build/web-mobile/assets/internal/index.js'

    projectNamePath = os.getcwd() + "/projectName.txt"
    projectNameOriginKey = "Cocos Creator | hello_world"

    # 自动复制模版到打包目录
    print("copy html", copyfile('./template/index.html', htmlPath))
    print("copy main.js", copyfile('./template/main.js', mainScrPath))

    htmlStr = read_in_chunks(htmlPath)
    settingsStr = read_in_chunks(settingScrPath)
    htmlStr = htmlStr.replace(settingMatchKey, settingsStr, 1)

    projectStr = read_in_chunks(projectScrPath)
    htmlStr = htmlStr.replace(projectMatchKey, projectStr, 1)

    mainStr = read_in_chunks(mainScrPath)
    mainStr = addPlistSupport(mainStr)
    htmlStr = htmlStr.replace(mainMatchKey, mainStr, 1)

    engineStr = read_in_chunks(engineScrPath)
    engineStr = fixEngineError(engineStr)
    htmlStr = htmlStr.replace(engineMatchKey, engineStr, 1)

    resStr = getResMapScript(resPath)
    htmlStr = htmlStr.replace(resMapMatchKey, resStr, 1)

    # 替换项目名
    projectName = read_in_chunks(projectNamePath)
    htmlStr = htmlStr.replace(projectNameOriginKey, projectName, 1)

    # 清除未使用的替换符
    # htmlStr = htmlStr.replace(ttfMapMatchKey, '', 1)
    htmlStr = htmlStr.replace(indexInternalKey, '', 1)

    # 写入新 HTML
    dirName = os.path.dirname(newHtmlPath)
    if os.path.exists(dirName) == False:
        os.makedirs(dirName)
    writeToPath(newHtmlPath, htmlStr)

    targetFileSize = os.path.getsize(newHtmlPath)
    targetFileSizeInMegabyte = math.ceil(targetFileSize * 1000 / (1024 * 1024)) / 1000

    print("===================  All Done! =================== ")
    print("Target file = {}, with size {}M".format(newHtmlPath, targetFileSizeInMegabyte))

if __name__ == '__main__':
    workDir = os.getcwd() + "/.."
    integrate(workDir)
