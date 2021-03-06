import json
import os
import shutil
from time import sleep
import traceback, sys

from django.core.exceptions import PermissionDenied
from django.http.response import HttpResponse
from django.db.models.query_utils import Q

from protocal import export_proto2
from protocal import export_lua
from protocal import export_cpp
from protocal.models import *


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

def do_pre_handle_customtype(context, customtype, enums, customtypes, enums_dict, customtypes_dict):
    if customtypes_dict.has_key(customtype.id):
        customtype.segments = customtypes_dict[customtype.id]
    else:
        customtype.segments = []

    innerenums = enums.filter(belong_ct = customtype);
    for enum in innerenums:
        if enums_dict.has_key(enum.id):
            enum.segments = enums_dict[enum.id]
        else:
            enum.segments = []
    customtype.innerenums = innerenums

    innercustomtypes = customtypes.filter(belong_ct = customtype)
    for ct_customtype in innercustomtypes:
        do_pre_handle_customtype(context, ct_customtype, enums, customtypes, enums_dict, customtypes_dict);
    customtype.innercustomtypes = innercustomtypes


def do_pre_handle_module(context, module, null = False):
    enums = Enum.objects.filter(module = module)
    enumsegments = EnmuSegment.objects.filter(belong__in = enums).order_by('belong')

    customtypes = CustomType.objects.filter(module = module)
    customtypesegments = CustomTypeSegment.objects.filter(belong__in = customtypes).order_by('belong')

    protocals = Protocal.objects.filter(module = module)
    segments = Segment.objects.filter(protocal__in = protocals).order_by('protocal')

    if len(enums) > 0 or len(customtypes) > 0 or len(protocals) > 0:
        #write module global enum and customtype
        enums_dict = {}
        for enumsegment in enumsegments:
            enum_segments = None
            if not enums_dict.has_key(enumsegment.belong.id):
                enum_segments = []
                enums_dict[enumsegment.belong.id] = enum_segments
            else:
                enum_segments = enums_dict[enumsegment.belong.id]
            enum_segments.append(enumsegment)

        moduleEnums = enums.filter(Q(belong = None) and Q(belong_ct = None))
        for enum in moduleEnums:
            if enums_dict.has_key(enum.id):
                enum.segments = enums_dict[enum.id]
            else:
                enum.segments = []
        module.enums = moduleEnums

        customtypes_dict = {}
        for customtypesegment in customtypesegments:
            customtype_segments = None
            if not customtypes_dict.has_key(customtypesegment.belong.id):
                customtype_segments = []
                customtypes_dict[customtypesegment.belong.id] = customtype_segments
            else:
                customtype_segments = customtypes_dict[customtypesegment.belong.id]
            customtype_segments.append(customtypesegment)

        moduleCustoms = customtypes.filter(Q(belong = None), Q(belong_ct = None))
        for customtype in moduleCustoms:
            do_pre_handle_customtype(context, customtype, enums, customtypes, enums_dict, customtypes_dict)

        module.customtypes = moduleCustoms

        #write protocal
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

            innerenums = enums.filter(belong = protocal);
            for enum in innerenums:
                if enums_dict.has_key(enum.id):
                    enum.segments = enums_dict[enum.id]
                else:
                    enum.segments = []
            protocal.innerenums = innerenums

            innercustomtypes = customtypes.filter(belong = protocal)
            for customtype in innercustomtypes:
                if customtypes_dict.has_key(customtype.id):
                    customtype.segments = customtypes_dict[customtype.id]
                else:
                    customtype.segments = []

                ct_innerenums = enums.filter(belong_ct = customtype);
                for enum in ct_innerenums:
                    if enums_dict.has_key(enum.id):
                        enum.segments = enums_dict[enum.id]
                    else:
                        enum.segments = []
                customtype.innerenums = ct_innerenums

                ct_innercustomtypes = customtypes.filter(belong_ct = customtype)
                for ct_customtype in ct_innercustomtypes:
                    ct_customtype.innerenums = None;
                    ct_customtype.innercustomtypes = None;
                    if customtypes_dict.has_key(ct_customtype.id):
                        ct_customtype.segments = customtypes_dict[ct_customtype.id]
                    else:
                        ct_customtype.segments = []
                        
                customtype.innercustomtypes = ct_innercustomtypes
                    
            protocal.innercustomtypes = innercustomtypes

        module.protocals = protocals
    else:
        if null:
            return None;

    return module


def pre_handle_modules(context):
    project = context.project

    #global module----------------------------------------------------------------------
    global_module = Module(
                    id = 0,
                    name = 'global',
                    namedesc = 'global',
                    desc = '',
                    project = project,
                    namespace = project.namespace)

    context.global_module = do_pre_handle_module(context, global_module, True)
        
    #module----------------------------------------------------------------------
    modules = Module.objects.filter(project = project)
    ids = []
    for module in modules:
        m = do_pre_handle_module(context, module, True)
        if m == None:
            ids.append(module.id)
    modules = modules.exclude(pk__in=ids);

    for module in modules:
        module = do_pre_handle_module(context, module)

    context.modules = modules

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
        
    if not os.path.exists(context.zip_dst_path):
        os.mkdir(context.zip_dst_path) 

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
    context.zip_dst_path = context.root_path + 'archive/'
    context.proto2_path = context.root_path + 'proto2/'
    context.protocal_types = ProtocalType.objects.all()
    context.global_module = None
    
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
    export_lua.do_zip(context)

    export_cpp.do_export(context)
    export_cpp.do_zip(context)