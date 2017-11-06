import os
import traceback, sys
from protocal.utils import cmd_call
import zipfile

TOOL_PATH = "D:/workspace/yuyu/program/Tools/ConfigExport"
XLS_PATH = "D:/workspace/yuyu/data/yh_170931_dev(M1)"
VERSION = "1.0"

def do_export(ex_path):
    the_export_path = ex_path + '/config'

    cmd = 'svn update "%s"'%(XLS_PATH)
    cmd_call(cmd)

    if not os.path.exists(the_export_path):
        os.mkdir(the_export_path) 

    zip_archive_path = the_export_path + '/archive/'
    if not os.path.exists(zip_archive_path):
        os.mkdir(zip_archive_path) 

    cmd = 'cd "%s" && D: && python xls2luas.py %s %s %s'%(TOOL_PATH,XLS_PATH,the_export_path,VERSION)
    cmd_call(cmd)

    file_zip = zipfile.ZipFile(zip_archive_path+'config_lua.zip','w',zipfile.ZIP_DEFLATED) 
    startdir = the_export_path + '/lua/'
    for dirpath, dirnames, filenames in os.walk(startdir): 
        for filename in filenames: 
            tozipfile = os.path.relpath(os.path.join(dirpath,filename), startdir)  
            file_zip.write(os.path.join(dirpath,filename), tozipfile) 
    file_zip.close() 

