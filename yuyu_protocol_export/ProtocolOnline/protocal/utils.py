# -*- coding: utf-8 -*-

import json
import os
from shutil import copystat, Error
import shutil
import subprocess
import traceback, sys

from django.http.response import HttpResponse


def try_parse_int(s):
    try:
        return int(s)
    except ValueError:
        pass

    try:
        import unicodedata
        return unicodedata.numeric(s)
    except (TypeError, ValueError):
        pass

    return False

def print_trace():
    import sys, traceback
    (exc_type, exc_info, tb) = sys.exc_info()
    response = "%s\n" % exc_type.__name__
    response += "%s\n\n" % exc_info
    response += "TRACEBACK:\n"    
    for tb in traceback.format_tb(tb):
        response += "%s\n" % tb
        
    print response
    
def cmd_call(cmd):
    print 'Executing cmd:[%s]'%cmd
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)  
    (stdoutput,erroutput) = p.communicate()
    p.wait()
    rc = p.returncode
    if rc <> 0:
        erroutput = erroutput.decode(sys.getfilesystemencoding())
        stdoutput = stdoutput.decode(sys.getfilesystemencoding())
        if erroutput == u'':
            raise Exception(stdoutput.encode('utf-8'))
        else:
            raise Exception(erroutput.encode('utf-8'))


def copytree(src, dst, symlinks=False):  
    names = os.listdir(src)  
    if not os.path.isdir(dst):  
        os.makedirs(dst)  
          
    errors = []  
    for name in names:  
        srcname = os.path.join(src, name)  
        dstname = os.path.join(dst, name)  
        try:  
            if symlinks and os.path.islink(srcname):  
#                 linkto = os.readlink(srcname)  
#                 os.symlink(linkto, dstname) 
                pass 
            elif os.path.isdir(srcname):  
                copytree(srcname, dstname, symlinks)  
            else:  
                if os.path.isdir(dstname):  
                    os.rmdir(dstname)  
                elif os.path.isfile(dstname):  
                    os.remove(dstname)  
                shutil.copy2(srcname, dstname)  
            # XXX What about devices, sockets etc.?  
        except (IOError, os.error) as why:  
            errors.append((srcname, dstname, str(why)))  
        # catch the Error from the recursive copytree so that we can  
        # continue with other files  
        except OSError as err:  
            errors.extend(err.args[0])  
    try:  
        copystat(src, dst)  
    except WindowsError:  
        # can't copy file access times on Windows  
        pass  
    except OSError as why:  
        errors.extend((src, dst, str(why)))  
    if errors:  
        raise Error(errors)  

def is_sub_string(SubStrList,Str):  
    flag=True  
    for substr in SubStrList:
        if not(substr in Str):
            flag=False  
  
    return flag  

def get_file_list(FindPath,FlagStr=[]):  
    FileList=[]  
    FileNames=os.listdir(FindPath)  
    if (len(FileNames)>0):  
       for fn in FileNames:  
           if (len(FlagStr)>0):  
               if (is_sub_string(FlagStr,fn)):  
                   fullfilename=os.path.join(FindPath,fn)
                   FileList.append(fullfilename)  
           else:  
               fullfilename=os.path.join(FindPath,fn)  
               FileList.append(fullfilename)  
  
    if (len(FileList)>0):  
        FileList.sort()
  
    return FileList  