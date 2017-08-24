#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import xls2lua
import shutil
from summary_tools import *
from descriptor import *
import plugins

def main() :

    xlspath = sys.argv[1]
    topath = sys.argv[2]
    ver = sys.argv[3]
    # 检查目录是否存在
    if not os.path.exists( xlspath ) :
        print xlspath, " is not exist !"
        exit(0)

    file_sumary = generate_file_sumary(xlspath)
    summary_path = xlspath + "/summary.txt"
    last_file_summary = read_file_summary(summary_path)
    summary_diff = compare_file_summary(file_sumary,last_file_summary)

    # 遍历xlspath
    files = []
    for k,v in summary_diff["updated"].iteritems():
        files.append(v.path)

    print "\n\nstart gen .......................\n"
    support = []
    for name in plugins.__all__:
        plugin = getattr(plugins, name)
        try:
            type_name = plugin.type_name
        except AttributeError:
            pass
        else:
            support.append(type_name())
    print 'support export types : ' + str(support) + '\n\n'

    for name in plugins.__all__:
        code_gen_req = CodeGenerateRequest(files, ver)
        code_gen_response = CodeGenerateResponse(topath)
        plugin = getattr(plugins, name)
        try:
            gen_code = plugin.gen_code
        except AttributeError:
            pass
        else:
            gen_code(code_gen_req, code_gen_response, topath)
            code_gen_response.saveToFile()

    #write_file_summary(file_sumary,summary_path)
    print "\n\n\n\nDone.........................."

if __name__ == "__main__" :
    main()
