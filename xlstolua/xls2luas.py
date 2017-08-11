#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import xls2lua
import shutil
from summary_tools import *

LUA_ALL_CONFIG_NAME = "GameConfigs"

def addHepler(name):
    s  = "function %s.get(id)\n"%name
    s += "  return %s[\"items\"][tostring(id)];\n"%name
    s += "end\n"
    return s

def generate_all_config_lua(lua_folder,lua_dev_folder_rel):
    print "generate_all_config_lua..."
    lua_all_config_path = lua_folder + "/" + LUA_ALL_CONFIG_NAME + ".lua"
    all_lua_name = []
    
    for root, dirs, files in os.walk(lua_folder): 
        for f in files: 
            file_path = os.path.join(root, f) 
            file_name = os.path.basename(f)
            file_name,file_suffix = os.path.splitext(file_name)
            if file_suffix == ".lua":
                if file_name != LUA_ALL_CONFIG_NAME :
                    all_lua_name.append(file_name)
    f = file(lua_all_config_path,"w")
    f.write("%s = {}\n"%(LUA_ALL_CONFIG_NAME))
    for name in all_lua_name:
        f.write("%s = require \"%s.%s\"\n"%(name,lua_dev_folder_rel,name))
        f.write(addHepler(name));
        f.write("%s.%s = %s\n"%(LUA_ALL_CONFIG_NAME,name,name))
    f.close()

def main() :
    xlspath = sys.argv[1]
    luapath = sys.argv[2]
    ver = sys.argv[3]
    # 检查目录是否存在
    if not os.path.exists( xlspath ) :
        print xlspath, " is not exist !"
        exit(0)
    if not os.path.exists( luapath ) :
        os.mkdir(luapath)
        print luapath, " is not exist ! create it"

    file_sumary = generate_file_sumary(xlspath)
    summary_path = xlspath + "/summary.txt"
    last_file_summary = read_file_summary(summary_path)
    summary_diff = compare_file_summary(file_sumary,last_file_summary)

    # 遍历xlspath
    for filename in os.listdir(luapath) :
        name, suffix = filename.split( '.' )
        if  suffix == 'lua' :
            os.remove(luapath+"/"+filename)

    # 遍历xlspath
    for k,v in summary_diff["updated"].iteritems():
        print 'Convert ' + v.path 
        exportor = xls2lua.xlsExport2Lua( v.path, luapath, ver )
        luaList = exportor.export()

    generate_all_config_lua(luapath, "Config.GameConfig")
    #write_file_summary(file_sumary,summary_path)
    print "\n\n\n\nDone.........................."

if __name__ == "__main__" :
    main()
