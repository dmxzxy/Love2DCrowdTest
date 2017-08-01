import json
import os
import shutil
import traceback, sys

def write_protocal_body(file_proto, context, protocal):
    segments = protocal.segments
    index = 1
    for segment in segments:
        if segment.type.name == 'map':
            file_proto.write('    %s %s<%s,%s> %s = %d;' % (segment.protocal_type, segment.type.name, segment.extra_type1.name, segment.extra_type2.name, segment.name, index))
        else:
            file_proto.write('    %s %s %s = %d;' % (segment.protocal_type, segment.type.name, segment.name, index))

        file_proto.write('      // ')
        file_proto.write(segment.desc.encode('utf-8'))
        file_proto.write('\n');
        index = index + 1


def do_export_protocal(context):
    modules = context.modules
    for module in modules:
        proto_path = context.proto2_path + module.name + '.proto'
        file_proto = open(proto_path, 'w')
        file_proto.write('syntax = "proto2";\n\n')

        file_proto.write('package %s;\n' % (module.namespace))
        file_proto.write('\n')

        for protocal in module.protocals:
            file_proto.write('// ')
            file_proto.write(protocal.desc.encode('utf-8'))
            file_proto.write('\n')
            file_proto.write('message %s {\n' % (protocal.name))
            write_protocal_body(file_proto, context, protocal)
            file_proto.write('}\n')
            file_proto.write('\n')

        file_proto.close()    