import commands
import os
import traceback, sys
import zipfile

from protocal.utils import cmd_call

PROTOC_BIN_NAME = 'win32/protoc.exe'

def do_init_folder(context,output_path):
    #create proto folder
    if not os.path.exists(output_path):
        os.mkdir(output_path) 
    return output_path


def do_execute_cpp(context,proto_name,output_path):
    proto_path = context.proto_path
    cmd = "%s --proto_path=%s --cpp_out=%s %s/%s.proto "%(context.bin_path + PROTOC_BIN_NAME, proto_path,output_path,proto_path,proto_name)
    print cmd
    cmd_call(cmd)


def do_export(context):
    context.compile_cpp_path = context.root_path + 'cpp/'
    output_path = context.compile_cpp_path
    do_init_folder(context,output_path)
            
    global_module = context.global_module
    if global_module:
        name = global_module.name
        do_execute_cpp(context,name,output_path)

    modules = context.modules
    for module in modules:
        name = module.name
        do_execute_cpp(context,name,output_path)


def do_zip(context):
    print 'Do zip'
    zip_src_path = context.compile_cpp_path
    file_path = context.zip_dst_path + 'protocal_cpp.zip'
    file_zip = zipfile.ZipFile(file_path,'w',zipfile.ZIP_DEFLATED)

    global_module = context.global_module
    if global_module:
        name = global_module.name
    	file_zip.write(os.path.join(zip_src_path, global_module.name + '.pb.h'),global_module.name + '.pb.h')
    	file_zip.write(os.path.join(zip_src_path, global_module.name + '.pb.cc'),global_module.name + '.pb.cc')

    modules = context.modules
    for module in modules:
        name = module.name
    	file_zip.write(os.path.join(zip_src_path, module.name + '.pb.h'),module.name + '.pb.h')
    	file_zip.write(os.path.join(zip_src_path, module.name + '.pb.cc'),module.name + '.pb.cc')

    file_zip.close()     