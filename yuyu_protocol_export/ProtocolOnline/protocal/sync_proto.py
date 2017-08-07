import os
import traceback, sys
from protocal.utils import cmd_call
from protocal.utils import get_file_list
from string import strip
from django.shortcuts import get_object_or_404

import json
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
    	cmd += f
    	cmd += ' '
    cmd_call(cmd)

def doSyncEnumValue(context, module, enum, enumvalue_dict):
    pass

def doSyncEnum(context, module, message, enum_dict):
    pass

def doSyncMessageField(context, module, message, field_dict):
    pass

def doSyncCustomType(context, module, message, message_dict):
    pass

def doSyncMessage(context, module, message_dict):
    cur_project = context.cur_project
    protocal_name = message_dict['name'];
    protocal_desc = '';
    protocal_namespace = module.namespace + '.' + protocal_name
    protocal_protocal_id = 0;
    protocal_protocal_unique_id = cur_project.id + protocal_protocal_id
    protocal_type = get_object_or_404(ProtocalType, pk=1) 

    try:
        message = Protocal.objects.filter(namespace = protocal_namespace)[0]
    except IndexError:
        message = None
    if message == None:
        message = Protocal(name = strip(protocal_name),
                            desc = protocal_desc,
                            module = module,
                            protocal_id = protocal_protocal_id,
                            protocal_unique_id = protocal_protocal_unique_id,
                            type = protocal_type,
                            namespace = strip(protocal_namespace),
                            relate_protocal = None,
                            )
        message.save()
    else:
        Protocal.objects.filter(pk = message.id).update(name = strip(protocal_name),
                        desc = protocal_desc,
                        module = module,
                        protocal_id = protocal_protocal_id,
                        protocal_unique_id = protocal_protocal_unique_id,
                        type = protocal_type,
                        namespace = strip(protocal_namespace),
                        relate_protocal = None,
                        )

    enumlist = message_dict['enumlist'];
    for e in enumlist:
        doSyncEnum(context, module, message, e);

    fieldlist = message_dict['fieldlist'];
    for field in fieldlist:
        doSyncMessageField(context, module, message, field)

    nestedtypelist = message_dict['nestedtypelist'];
    for n in nestedtypelist:
        doSyncCustomType(context, module, message, n)

def doSyncModule(context, module_dict):
    namespace = context.namespace;
    module_namespace = module_dict['package'];
    module_modulename = module_namespace.replace(namespace+'.','');
    module_name = module_modulename
    module_desc = module_modulename

    if namespace == module_namespace:
        pass
    else:
        try:
            module = Module.objects.filter(namespace = module_namespace)[0]
        except IndexError:
            module = None

        if module == None:
            module = Module(
                name = module_modulename,
                namedesc = strip(module_name),
                desc = module_desc,
                project = context.cur_project,
                namespace = module_namespace)
            module.save()
        else:
            Module.objects.filter(pk=module.id).update(
                name = module_modulename,
                namedesc = strip(module_name),
                desc = module_desc,
                project = context.cur_project,
                namespace = module_namespace)
        enumlist = module_dict['enumlist']
        for e in enumlist:
            doSyncEnum(context, module, None, e);
        messagelist = module_dict['messagelist']
        for m in messagelist:
            doSyncMessage(context, module, m);
            


def doSync(project):
    context = cls_context()
    context.namespace = project.namespace
    context.cur_project = project
    context.proto_sync_path = 'E:/workspace/Love2DCrowdTest/SyncProto';
    bin_path = os.path.dirname(__file__)
    context.bin_path = os.path.join(bin_path, 'export_bin/' )
    #step 1: git download server proto files
    #step 2: parse proto files get module{ add, del, update }
    #step 3: for add edit sql
    #step 4: for del edit sql
    #step 4: for update edit sql

    parse_proto_files(context)
    with open(proto_parse_plugin_outputpath+'/'+'parse.json','r') as load_f:
    	proto_parse_dict = json.load(load_f);
        context.proto_parse_dict = proto_parse_dict;
    	for m in proto_parse_dict['modulelist']:
    		doSyncModule(context, m)