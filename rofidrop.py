#!/usr/bin/env python3

import os
import sys
import io

import clipboard
from rofi import Rofi
import requests

r = Rofi(lines=12,width=50,location=0,rofi_args=["-columns", "2"])

def show_recieve_dialog(file):
    options = ["Save", "Save As", "Ignore"]
    selection,key = r.select("File {} Recieved! Choose an action".format(file["name"]), options)
    if key != 0:
        return 0
    return options[selection]

def path_dialog_loop(file, dir):
    options = ["Save Here", "Go Up"]
    local_dirs = filter(lambda x: os.path.isdir(os.path.join(dir, x)), os.listdir(dir))
    options.extend(list(local_dirs))
    selection,key = r.select("Save file {}".format(file["name"]), options)
    if key != 0:
        return dir
    if selection == 0:
        return dir
    if selection == 1:
        return path_dialog_loop(file, os.path.join(dir,'../'))
    else:
        return path_dialog_loop(file, os.path.join(dir,options[selection]))

def file_dialog_loop(dir):
    options = ["Go Up"]
    options.extend(os.listdir(dir))
    selection,key = r.select("Select File to Upload", options)
    if key != 0:
        return

    if selection == 0:
        return file_dialog_loop(os.path.join(dir, '../'))
    elif os.path.isdir(os.path.join(dir, options[selection])):
        return file_dialog_loop(os.path.join(dir, options[selection]))
    else:
        return os.path.join(dir, options[selection])

def do_upload(files):
    r = requests.post(url,files=files)
    print(r.json())

def upload_file(fn):
    files = {'file': (os.path.basename(fn), open(fn, 'rb'), 'text/html', {'Expires': '0'})}
    do_upload(files)

def upload_clipboard(content):
    files = {'file': ('clip.txt', io.StringIO(content), 'text/html', {'Expires': '0'})}
    do_upload(files)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: rofidrop.py --url URL [--file FILENAME, --pick, --clipboard]")
        exit(-1)
    url = sys.argv[2]
    if sys.argv[3]=='--file':
        upload_file(sys.argv[4])
    elif sys.argv[3]=='--pick':
        fn = file_dialog_loop(os.environ["HOME"])
        upload_file(fn)
    elif sys.argv[3]=='--clipboard':
        upload_clipboard(clipboard.paste())
