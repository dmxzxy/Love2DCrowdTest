import json
import os
import shutil
from time import sleep
import traceback, sys

from django.core.exceptions import PermissionDenied
from django.http.response import HttpResponse

from protocal import export_proto2
from protocal import export_lua
from protocal.models import SegmentType, Protocal, Module, Segment, ProtocalType


class cls_context:
    project = None
    setting = None
    def __str__(self):
        return self.project.title

class cls_candidate:
    custom_type = None
    segments = []
    namespace = ""
    
    def __str__(self):
        return self.custom_type.name
    
class cls_founded:
    level = 0
    custom_type = None
    looped_type = {}
    depend_on = {}
    def __str__(self):
        return "[name:%s,level:%d]"%(self.custom_type.name,self.level)

def calculate_type_level(cur_type_name,candidates,founded,depend_on,looped_type,level,avoid_loop,ident = ""):
    ident = ident + "    ";
    print(ident + "calculate_type_level:" + cur_type_name);
    
    level = level + 1;
    candidate = candidates[cur_type_name]
    custom_type = candidate.custom_type
    custom_type_segments = candidate.segments
    
    for custom_type_segment in custom_type_segments:
        if not custom_type_segment.type.is_basic:
            depend_on[custom_type_segment.type.name] = True
            if founded.has_key(custom_type_segment.type.name):
                founded_type = founded[custom_type_segment.type.name]
                if founded_type.level > level:
                    level = founded_type.level
            else:
#                     print 'custom_type_segment.type.name:' + custom_type_segment.type.name
                c_level = calculate_type_level(custom_type_segment.type.name, candidates,founded,depend_on,looped_type,level, avoid_loop + 1,ident)
                if c_level > level:
                    level = c_level
        else:
            if custom_type_segment.type.name == 'map':
                if custom_type_segment.extra_type1 and not custom_type_segment.extra_type1.is_basic:
                    c_level = calculate_type_level(custom_type_segment.extra_type1.name, candidates,founded,depend_on,looped_type,level, avoid_loop + 1,ident)
                    if c_level > level:
                        level = c_level
                if custom_type_segment.extra_type2 and not custom_type_segment.extra_type2.is_basic:   
                    c_level = calculate_type_level(custom_type_segment.extra_type2.name, candidates,founded,depend_on,looped_type,level, avoid_loop + 1,ident)
                    if c_level > level:
                        level = c_level
                            
        print(ident + "[ type = " + custom_type_segment.type.name + ",level = " + str(level) + " ]");
#     if looped_type.has_key(cur_type_name):
    if avoid_loop > 10:
        loop_str = str(looped_type);
        candidate = candidates[cur_type_name]
        raise Exception("Loop nested.type:" + cur_type_name + ",loop dict:" + loop_str + ",namespace:" + candidate.namespace);              
    
    instance_founded = cls_founded()
    instance_founded.level = level + 1;
    custom_type = candidate.custom_type
    custom_type_segments = candidate.segments
    custom_type.segments = custom_type_segments
    instance_founded.custom_type = custom_type
    instance_founded.depend_on = depend_on
    instance_founded.looped_type = looped_type
    founded[cur_type_name] = instance_founded
    print(ident + "set type[" + cur_type_name + "] for level = [" + str(instance_founded.level) + "]");
    
    looped_type[cur_type_name] = True          
    return instance_founded.level


def sort_segments(d):
    return d[1].level

def pre_handle_modules(context):
    project = context.project
    modules = Module.objects.filter(project = project)
        
    for module in modules:
        protocals = Protocal.objects.filter(module = module)
        segments = Segment.objects.filter(protocal__in = protocals).order_by('protocal')
        protocals_dict = {}

        for segment in segments:
            protocal_segments = None
            if not protocals_dict.has_key(segment.protocal.id):
                protocal_segments = []
                protocals_dict[segment.protocal.id] = protocal_segments
            else:
                protocal_segments = protocals_dict[segment.protocal.id]
            
            protocal_segments.append(segment)
            
        for protocal in protocals:
            if protocals_dict.has_key(protocal.id):
                protocal.segments = protocals_dict[protocal.id]
            else:
                protocal.segments = []

        module.protocals = protocals

    context.modules = modules;

def do_init_folder(context):
    print 'Do init folder'
    if not os.path.exists(context.setting.export_path):
        os.mkdir(context.setting.export_path) 
    if context.setting.export_clean:
        if os.path.exists(context.root_path):
            print 'Deleting folder:' + context.root_path
            shutil.rmtree(context.root_path)
    #create folder
    if not os.path.exists(context.root_path):
        os.mkdir(context.root_path) 
    #create proto folder
    if not os.path.exists(context.proto2_path):
        os.mkdir(context.proto2_path) 

def do_write_down_version(context,version_path):
    print 'Do write down version'
    file_version = open(version_path,'w')    
    file_version.write(context.version)
    file_version.close()



def do_export(project,version,export_setting):
    context = cls_context()
    context.version = version
    context.setting = export_setting
    context.project = project
    context.namespace = project.namespace
    context.root_path = context.setting.export_path + '/protocal/'
    context.proto2_path = context.root_path + 'proto2/'
    context.protocal_types = ProtocalType.objects.all()
    
    bin_path = os.path.dirname(__file__)
    context.bin_path = os.path.join(bin_path, 'export_bin/' )
    context.proto_path = context.proto2_path
    context.proto_exporting_tool = export_proto2
    
    pre_handle_modules(context)
    do_init_folder(context)
    
    context.version_path = context.root_path + 'protocal_version.txt'
    do_write_down_version(context,context.version_path)
    context.proto_exporting_tool.do_export_protocal(context)
        
    #context.proto_exporting_tool.do_export_proto_configs(context)

    # export for languages
    export_lua.do_export(context)