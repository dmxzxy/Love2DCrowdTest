# -*- coding: utf-8 -*-
import base64
import commands
import json
import os
import traceback, sys
import zipfile

from django.http.response import HttpResponse

from protocal.utils import cmd_call


PROTOC_BIN_NAME = 'win32/protoc.exe'

def do_init_folder(context,output_path):
    #create proto folder
    if not os.path.exists(output_path):
        os.mkdir(output_path) 
    return output_path

def do_execute_proto(context,proto_name,output_path):
    proto_path = context.proto_path
    cmd = '%s --proto_path="%s" --descriptor_set_out="%s%s.pb" "%s.proto"'%(context.bin_path + PROTOC_BIN_NAME, proto_path,output_path,proto_name,proto_path + proto_name )
    print cmd
    cmd_call(cmd)

def load_pb_data(output_path,pb_name):
    file_pb_path = output_path + pb_name + '.pb'
    file_pb = open(file_pb_path,'rb')
    bdata = file_pb.read()
    blen = file_pb.tell()
    file_pb.close()
    data = base64.b64encode(bdata)
    return data,blen
    
def do_package_lua(context,output_path):
    file_lua_path = output_path + 'protocals.lua'
    file_lua = open(file_lua_path,'w')
        
    file_lua.write('Protocals = {\n')
    file_lua.write('  Request = {},\n')
    file_lua.write('  Response = {},\n')
    file_lua.write('  Notification = {},\n')
    file_lua.write('}\n')
    
    modules = context.modules
    for module in modules:
        protocals = module.protocals
        for protocal in protocals:
            prefix = "";
            if protocal.type.name == "Request":
                prefix = "Protocals.Request"
            elif protocal.type.name == "Response":
                prefix = "Protocals.Response"
            elif protocal.type.name == "Notification":
                prefix = "Protocals.Notification"
            file_lua.write('%s.%s = %d;\n'%(prefix,protocal.name,protocal.protocal_id))
    file_lua.write("\n");
    
    file_lua.write('ProtocalTypes = {\n')
    protocal_types = context.protocal_types
    for protocal_type in protocal_types:
        file_lua.write('    %s = %d,\n'%(protocal_type.name,protocal_type.id))
    file_lua.write('}\n')
    
    file_lua.write('ProtocalConfigs = {\n')
    file_lua.write('    version = "%s",\n'%(context.version))
    # write modules
    file_lua.write('    modules = {\n')
    for module in modules:
        pb_data,pb_len = load_pb_data(output_path, module.name)
        file_lua.write('        ["%s"] = { namespace = %s, data = "%s", len = %d },\n'%(module.name, module.namespace, pb_data, pb_len))
    file_lua.write('    },\n')   

    # write protocals
    file_lua.write('    protocals = {\n')

    for module in modules:
        protocals = module.protocals
        for protocal in protocals:
            pb_name = protocal.name
            pb_fullname = protocal.namespace
            module_name = protocal.module.name
            protocal_relate_id = 0
            if protocal.relate_protocal:
                protocal_relate_id = protocal.relate_protocal.protocal_id
            file_lua.write('        [%d] = { id = %d, module = "%s", name = "%s", type = %s, ref = %d, full_name = "%s"},\n'%( \
                        int(protocal.protocal_id),int(protocal.protocal_id),module_name,pb_name,"ProtocalTypes."+protocal.type.name,int(protocal_relate_id), pb_fullname))
    file_lua.write('    },\n')   
    file_lua.write('}\n')        
    file_lua.close()
    

def do_export(context):
    context.compile_path = context.root_path + 'lua/'
    output_path = context.compile_path
    do_init_folder(context,output_path)
            
    modules = context.modules
    for module in modules:
        name = module.name
        do_execute_proto(context,name,output_path)
        
    do_package_lua(context,output_path)
        
def do_zip(context):
    print 'Do zip'
    zip_src_path = context.compile_path
    file_path = context.zip_dst_path + 'protocal_lua.zip'
    file_zip = zipfile.ZipFile(file_path,'w',zipfile.ZIP_DEFLATED)
    file_zip.write(os.path.join(zip_src_path,'protocals.lua'),'protocals.lua')
    file_zip.write(context.version_path,'protocal_version.txt') 
    file_zip.close()     
    
    
    
       