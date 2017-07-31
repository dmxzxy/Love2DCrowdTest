import json
import os
import shutil
import traceback, sys

def write_protocal_body(file_proto, context, protocal):
    segments = protocal.segments
    index = 1
    for segment in segments:
        if segment.type.name == 'map':
            file_proto.write('    %s %s<%s,%s> %s = %d;\n' % (segment.protocal_type, segment.type.name, segment.extra_type1.name, segment.extra_type2.name, segment.name, index))
        else:
            file_proto.write('    %s %s %s = %d;\n' % (segment.protocal_type, segment.type.name, segment.name, index))
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
            file_proto.write('message %s {\n' % (protocal.name))
            write_protocal_body(file_proto, context, protocal);
            file_proto.write('}\n')
            file_proto.write('\n')

        file_proto.close()    
    
def do_export_proto_configs(context):
    json_config_path = context.proto2_path + 'proto_configs.json'
    protocals = context.protocals
    export_protocals = {}
    for protocal in protocals:
        relate_protocal_id = 0
        if protocal.relate_protocal:
            relate_protocal_id = protocal.relate_protocal.protocal_id
        key = int(protocal.protocal_id)
        export_protocals[key] = { 'id':protocal.protocal_id, 'name':protocal.name, 'type':protocal.type.id, 'typeStr' : protocal.type.name, 'relateProtocal' : relate_protocal_id }
    print export_protocals
    data = json.dumps(export_protocals, sort_keys=True, indent=4)
    file_json = open(json_config_path, 'w')
    file_json.write(data)
    file_json.close()    