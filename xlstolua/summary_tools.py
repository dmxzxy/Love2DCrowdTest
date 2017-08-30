#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import time
import platform
from stat import *
import pickle


class summary_info:
    def __init__(self):
        self.path = ""
        self.time = 0
    def __repr__(self):
        return "[time = %d,path = %s]\n"%(self.time,self.path)

def write_file_summary(summary,summary_path):
    f = file(summary_path, 'w') 
    pickle.dump(summary,f)
    f.close()

def read_file_summary(summary_path):
    file_summary = {}
    if not os.path.exists(summary_path):
        print "File[" + summary_path + "] not exits."
    else:
        f = file(summary_path, 'r') 
        file_summary = pickle.load(f) 
        f.close()
    return file_summary

def generate_file_sumary(excel_folder):
    file_sumary = {}
    for root, dirs, files in os.walk(excel_folder): 
        for f in files: 
            file_path = os.path.join(root, f) 
            file_name = os.path.basename(f)
            file_name,file_suffix = os.path.splitext(file_name)
            if cmp(file_name[:2],"~$") == 0:
                print "Excel temp file:" + file_name
            else:
                if file_suffix == ".xlsx" or file_suffix == ".xlsl" or file_suffix == ".xls" or file_suffix == ".xlsm":
                    info = summary_info()
                    info.time = os.stat(file_path)[ST_MTIME]
                    info.path = file_path
                    file_sumary[file_name] = info
    return file_sumary

# return the excel files modified
def compare_file_summary(cur_summary,last_summary):
    summary_diff = { }
    updated = {}
    unused = {}
    
    for k,v in cur_summary.iteritems():
        if not last_summary.has_key(k):
            updated[k] = v
        else:
            if last_summary[k].time != v.time:
                updated[k] = v
    summary_diff["updated"] = updated
    
    
    for k,v in last_summary.iteritems():
        if not cur_summary.has_key(k):
            unused[k] = v
    summary_diff["unused"] = unused
    
    return summary_diff