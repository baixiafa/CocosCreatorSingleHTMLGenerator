#!/usr/bin/python3

import tinify
import os
  
# Please reset the root directory Path !  
ImageFilePath = "build/web-mobile/assets"

apiKey = "GRJ2NhGy1NzDnK4ky7Wg5dYWMVMVMpP6"
assert len(apiKey) > 0, "API KEY is necessary, goto https://tinypng.com, sign up and get your own."
tinify.key = apiKey

fileType = [".png", ".jpg", ".webp"]
  
def isSupportedFile(filename):
    name, ext = os.path.splitext(filename)
    if ext in fileType:
        return True
    return False

def tinifyPic(targetPath):
    for filename in os.listdir(targetPath):
        filepath = os.path.join(targetPath, filename)
        if os.path.isdir(filepath):  
            tinifyPic(filepath) 
        else:  
            if isSupportedFile(filepath):
                print("Compressing: ", filepath)
                compressed_file = tinify.from_file(filepath)
                compressed_file.to_file(filepath)


if __name__ == '__main__':
    tinifyPic(ImageFilePath)