# -*- coding:utf-8 -*-
#!/usr/bin/python3

import os

import generate_normal
import tinify_pic

workdir = os.getcwd()
projectRootPath = workdir + "/.."
resPath = projectRootPath + '/build/web-mobile/assets'

def generate_html():
    print("=================== Start to Compress All Pictures ====================")
    tinify_pic.tinifyPic(resPath)

    print("=================== Start to Integrate Res into Html ====================")
    generate_normal.integrate(projectRootPath)

if __name__ == '__main__':
    generate_html()



