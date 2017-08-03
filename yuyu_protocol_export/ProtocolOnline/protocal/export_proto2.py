import json
import os
import shutil
import traceback, sys

def write_enum(file_proto, context, enum, indent=''):
    segments = enum.segments
    if len(segments) == 0:
        return;

    file_proto.write(indent+'// ')
    file_proto.write(enum.desc.encode('utf-8'))
    file_proto.write('\n')
    file_proto.write(indent+'enum %s {\n' % (enum.name))
    for segment in segments:
        segIndent = indent + '    '
        file_proto.write(segIndent+'%s = %d;' % (segment.name, segment.value))

        file_proto.write('      // ')
        file_proto.write(segment.desc.encode('utf-8'))
        file_proto.write('\n');

    file_proto.write(indent+'}\n')
    file_proto.write('\n')

def write_customtype(file_proto, context, customtype, indent=''):
    file_proto.write(indent+'// ')
    file_proto.write(customtype.desc.encode('utf-8'))
    file_proto.write('\n')
    file_proto.write(indent+'message %s {\n' % (customtype.name))

    segments = customtype.segments
    index = 1
    for segment in segments:
        segIndent = indent + '    '
        if segment.type.name == 'map':
            file_proto.write(segIndent+'%s %s<%s,%s> %s = %d;' % (segment.protocal_type, segment.type.name, segment.extra_type1.name, segment.extra_type2.name, segment.name, index))
        else:
            if segment.defaultEnum == None or (segment.defaultEnum and segment.defaultEnum.id == 0):
                file_proto.write(segIndent+'%s %-15s %s = %d;' % (segment.protocal_type, segment.type.name, segment.name, index))
            else:
                file_proto.write(segIndent+'%s %-15s %s = %d [ default = %s ];' % (segment.protocal_type, segment.type.name, segment.name, index, segment.defaultEnum.name))

        file_proto.write('      // ')
        file_proto.write(segment.desc.encode('utf-8'))
        file_proto.write('\n');
        index = index + 1

    file_proto.write(indent+'}\n')
    file_proto.write('\n')

def write_protocal(file_proto, context, protocal, indent=''):
    file_proto.write(indent+'// ')
    file_proto.write(protocal.desc.encode('utf-8'))
    file_proto.write('\n')
    file_proto.write(indent+'message %s {\n' % (protocal.name))

    segIndent = indent + '    '
    innerenums = protocal.innerenums
    for innerenum in innerenums:
        write_enum(file_proto, context, innerenum, segIndent);

    innercustomtypes = protocal.innercustomtypes
    for innercustomtype in innercustomtypes:
        write_customtype(file_proto, context, innercustomtype, segIndent);

    segments = protocal.segments
    index = 1
    for segment in segments:
        if segment.type.name == 'map':
            file_proto.write(segIndent+'%s %s<%s,%s> %s = %d;' % (segment.protocal_type, segment.type.name, segment.extra_type1.name, segment.extra_type2.name, segment.name, index))
        else:
            if segment.defaultEnum == None or (segment.defaultEnum and segment.defaultEnum.id == 0):
                file_proto.write(segIndent+'%s %-15s %s = %d;' % (segment.protocal_type, segment.type.name, segment.name, index))
            else:
                file_proto.write(segIndent+'%s %-15s %s = %d [ default = %s ];' % (segment.protocal_type, segment.type.name, segment.name, index, segment.defaultEnum.name))


        file_proto.write('      // ')
        file_proto.write(segment.desc.encode('utf-8'))
        file_proto.write('\n');
        index = index + 1

    file_proto.write(indent+'}\n')
    file_proto.write('\n')



def do_export_protocal(context):
    global_module = context.global_module
    if global_module:
        proto_path = context.proto2_path + global_module.name + '.proto'
        file_proto = open(proto_path, 'w')
        file_proto.write('syntax = "proto2";\n\n')

        file_proto.write('package %s;\n' % (global_module.namespace))
        file_proto.write('\n')

        file_proto.write('//  \n')
        file_proto.write('// enums \n')
        file_proto.write('//  \n')
        for enum in global_module.enums:
            write_enum(file_proto, context, enum)

        file_proto.write('//  \n')
        file_proto.write('// custom type \n')
        file_proto.write('//  \n')
        for customtype in global_module.customtypes:
            write_customtype(file_proto, context, customtype)

        file_proto.write('//  \n')
        file_proto.write('// protocal \n')
        file_proto.write('//  \n')
        for protocal in global_module.protocals:
            write_protocal(file_proto, context, protocal)

        file_proto.close()    

    modules = context.modules
    for module in modules:
        proto_path = context.proto2_path + module.name + '.proto'
        file_proto = open(proto_path, 'w')
        file_proto.write('syntax = "proto2";\n\n')

        file_proto.write('package %s;\n' % (module.namespace))
        file_proto.write('\n')

        if global_module:
            file_proto.write('import "%s.proto";\n\n' % (global_module.name))


        file_proto.write('//  \n')
        file_proto.write('// enums \n')
        file_proto.write('//  \n')

        for enum in module.enums:
            write_enum(file_proto, context, enum)

        file_proto.write('//  \n')
        file_proto.write('// custom type \n')
        file_proto.write('//  \n')

        for customtype in module.customtypes:
            write_customtype(file_proto, context, customtype)

        file_proto.write('//  \n')
        file_proto.write('// protocal \n')
        file_proto.write('//  \n')

        for protocal in module.protocals:
            write_protocal(file_proto, context, protocal)

        file_proto.close()    