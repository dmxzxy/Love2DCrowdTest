import os
import traceback, sys
from protocal.utils import cmd_call
from protocal.utils import get_file_list

from protocal.models import *


PROTOC_BIN_NAME = 'win32/protoc.exe'
proto_parse_plugin_path = 'proto_parse_plugin'
proto_parse_plugin_exe = 'runparse.bat'
proto_parse_plugin_outputpath = 'protocal/proto_parse_output'

class cls_context:
    project = None
    setting = None
    def __str__(self):
        return self.project.title

def parse_proto_files(context):
    proto_sync_path = context.proto_sync_path
    l = get_file_list(proto_sync_path,['proto'])
    cmdHead = "%s -I=%s --parse_out=%s --plugin=protoc-gen-parse=%s "%(context.bin_path+PROTOC_BIN_NAME, proto_sync_path, proto_parse_plugin_outputpath, context.bin_path+proto_parse_plugin_path+'/'+proto_parse_plugin_exe)

    cmd = cmdHead
    for f in l:
    	print f
    	cmd += f
    	cmd += ' '
    cmd_call(cmd)

def doSync(project):
    context = cls_context()    
    context.proto_sync_path = 'E:/workspace/Love2DCrowdTest/SyncProto';
    bin_path = os.path.dirname(__file__)
    context.bin_path = os.path.join(bin_path, 'export_bin/' )
    #step 1: git download server proto files
    #step 2: parse proto files get module{ add, del, update }
    #step 3: for add edit sql
    #step 4: for del edit sql
    #step 4: for update edit sql

    parse_proto_files(context)