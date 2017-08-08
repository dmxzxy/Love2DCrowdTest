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

#// 0 is reserved for errors.
#// Order is weird for historical reasons.
#TYPE_DOUBLE         = 1;
#TYPE_FLOAT          = 2;
#// Not ZigZag encoded.  Negative numbers take 10 bytes.  Use TYPE_SINT64 if
#// negative values are likely.
#TYPE_INT64          = 3;
#TYPE_UINT64         = 4;
#// Not ZigZag encoded.  Negative numbers take 10 bytes.  Use TYPE_SINT32 if
#// negative values are likely.
#TYPE_INT32          = 5;
#TYPE_FIXED64        = 6;
#TYPE_FIXED32        = 7;
#TYPE_BOOL           = 8;
#TYPE_STRING         = 9;
#TYPE_GROUP          = 10;  // Tag-delimited aggregate.
#TYPE_MESSAGE        = 11;  // Length-delimited aggregate.

# New in version 2.
#TYPE_BYTES          = 12;
#TYPE_UINT32         = 13;
#TYPE_ENUM           = 14;
#TYPE_SFIXED32       = 15;
#TYPE_SFIXED64       = 16;
#TYPE_SINT32         = 17;  // Uses ZigZag encoding.
#TYPE_SINT64         = 18;  // Uses ZigZag encoding.

class FieldType:
    TYPE_DOUBLE         = 1
    TYPE_FLOAT          = 2
    TYPE_INT64          = 3
    TYPE_UINT64         = 4
    TYPE_INT32          = 5
    TYPE_FIXED64        = 6
    TYPE_FIXED32        = 7
    TYPE_BOOL           = 8
    TYPE_STRING         = 9
    TYPE_GROUP          = 10
    TYPE_MESSAGE        = 11
    TYPE_BYTES          = 12
    TYPE_UINT32         = 13
    TYPE_ENUM           = 14
    TYPE_SFIXED32       = 15
    TYPE_SFIXED64       = 16
    TYPE_SINT32         = 17
    TYPE_SINT64         = 18

FName = {
    FieldType.TYPE_DOUBLE   : 'double',
    FieldType.TYPE_FLOAT    : 'float',
    FieldType.TYPE_INT64    : 'int64',
    FieldType.TYPE_UINT64   : 'uint64',
    FieldType.TYPE_INT32    : 'int32',
    FieldType.TYPE_FIXED64  : 'fixed64',
    FieldType.TYPE_FIXED32  : 'fixed32',
    FieldType.TYPE_BOOL     : 'bool',
    FieldType.TYPE_STRING   : 'string',
    FieldType.TYPE_GROUP    : '',
    FieldType.TYPE_MESSAGE  : '',
    FieldType.TYPE_BYTES    : 'bytes',
    FieldType.TYPE_UINT32   : 'uint32',
    FieldType.TYPE_ENUM     : '',
    FieldType.TYPE_SFIXED32 : 'sfixed32',
    FieldType.TYPE_SFIXED64 : 'sfixed64',
    FieldType.TYPE_SINT32   : 'sint32',
    FieldType.TYPE_SINT64   : 'sint64',
}

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
    segment_name = enumvalue_dict['name']
    segment_desc = enumvalue_dict['desc']
    segment_namespace = enumvalue_dict['fullname']
    segment_value = enumvalue_dict['number']

    try:
        enum_segment = EnmuSegment.objects.filter(namespace = segment_namespace)[0]
    except IndexError:
        enum_segment = None

    if enum_segment:
        enum_segment.update( name = strip(segment_name),
                            value = segment_value,
                            desc = segment_desc,
                            belong = enum,
                            )
    else:
        enum_segment = EnmuSegment(  name = strip(segment_name),
                                    value = segment_value,
                                    desc = segment_desc,
                                    belong = enum,
                                    )

        enum_segment.save()


#inner_type 0:global 1:protocal 2:customtype
def doSyncEnum(context, module, message, enum_dict, inner_type = 0):
    cur_project = context.cur_project
    enum_name = enum_dict['name']
    enum_desc = enum_dict['desc']
    enum_namespace = enum_dict['fullname']
    inner_protocal = None;
    inner_customtype = None;
    if inner_type == 1:
        inner_protocal = message;
    elif inner_type == 2:
        inner_customtype = message;

    try:
        enum = Enum.objects.filter(namespace = segment_namespace)[0]
    except IndexError:
        enum = None

    if enum == None:   
        enum = Enum(name = strip(enum_name),
                    desc = enum_desc,
                    module = module,
                    namespace = enum_namespace,
                    belong = inner_protocal,
                    belong_ct = inner_customtype,
                    )
        enum.save()

        segment_type = SegmentType(name = strip(enum_name),
                                   desc = enum_desc,
                                   module = module,
                                   protocal = inner_protocal,
                                   is_basic = False,
                                   project = cur_project,
                                   provider_type = 1,
                                   )
        segment_type.save()
        Enum.objects.filter(id=enum.id).update(type = segment_type)
    else:
        Enum.objects.filter(pk=enum_id).update(name = strip(enum_name),
                                                desc = enum_desc,
                                                module = module,
                                                namespace = enum_namespace,
                                                belong = inner_protocal,
                                                belong_ct = inner_customtype,
                                                )

        segment_type = SegmentType.objects.filter(id = cur_enum.type.id)
        if segment_type:
            segment_type.update(name = strip(enum_name),desc = enum_desc)


    valuelist = enum_dict['valuelist']
    for value in valuelist:
        doSyncEnumValue(context, module, enum, value)


def doSyncCustomTypeField(context, module, message, field_dict):
    customtype_segment_name = field_dict['name']
    customtype_segment_desc = field_dict['desc']
    customtype_segment_namespace = field_dict['fullname']
    customtype_segment_protocal_type_id = field_dict['label']

    customtype_segment_type = None
    customtype_segment_default_enum_segment = None
    if segment_type_type == FieldType.TYPE_ENUM:
        segment_type_name = field_dict['type_name'][1:]
        customtype_segment_type = get_object_or_404(Enum, namespace=segment_type_name).type
        if field_dict.has_key('default_value'):
            default_value_namespace = segment_type_name + '.' + field_dict['default_value']
            customtype_segment_default_enum_segment = get_object_or_404(EnmuSegment, namespace=default_value_namespace)
    elif segment_type_type == FieldType.TYPE_MESSAGE:
        segment_type_name = field_dict['type_name']
        customtype_segment_type = get_object_or_404(CustomType, namespace=segment_type_name).type
    else:
        customtype_segment_type = get_object_or_404(SegmentType, name=FName[segment_type_type])


    customtype_segment_protocal_type = get_object_or_404(SegmentProtoType, pk=customtype_segment_protocal_type_id) 

    try:
        customtype_segment = CustomTypeSegment.objects.filter(namespace = customtype_segment_namespace)[0]
    except IndexError:
        customtype_segment = None
            
    if customtype_segment:
        customtype_segment.update(name = strip(customtype_segment_name),
                            namespace = customtype_segment_namespace,
                            desc = customtype_segment_desc,
                            belong = message,
                            protocal_type = customtype_segment_protocal_type,
                            type = customtype_segment_type,
                            defaultEnum = customtype_segment_default_enum_segment
                            )
    else:
        customtype_segment = CustomTypeSegment(name = strip(customtype_segment_name),
                            namespace = customtype_segment_namespace,
                            desc = customtype_segment_desc,
                            belong = message,
                            protocal_type = customtype_segment_protocal_type,
                            type = customtype_segment_type,
                            defaultEnum = customtype_segment_default_enum_segment
                            )

        customtype_segment.save()

def doSyncCustomType(context, module, message, message_dict, inner_type = 0):
    cur_project = context.cur_project
    customtype_name = message_dict['name']
    customtype_desc = message_dict['desc']
    customtype_namespace = message_dict['fullname']
    inner_protocal = None;
    inner_customtype = None;
    if inner_type == 1:
        inner_protocal = message;
    elif inner_type == 2:
        inner_customtype = message;

    try:
        customtype = CustomType.objects.filter(namespace = segment_namespace)[0]
    except IndexError:
        customtype = None

    if cur_customtype:          
        CustomType.objects.filter(pk=customtype_id).update(name = strip(customtype_name),
                                                            desc = customtype_desc,
                                                            module = module,
                                                            namespace = customtype_namespace,
                                                            belong = inner_protocal,
                                                            belong_ct = inner_customtype,
                                                            )

        segment_type = SegmentType.objects.filter(id = cur_enum.type.id)
        if segment_type:
            segment_type.update(name = strip(customtype_name),desc = customtype_desc)
    else:
        customtype = CustomType(name = strip(customtype_name),
                    desc = customtype_desc,
                    module = module,
                    namespace = customtype_namespace,
                    belong = inner_protocal,
                    belong_ct = inner_customtype,
                    )

        customtype.save()

        segment_type = SegmentType(name = strip(customtype_name),
                                   desc = customtype_desc,
                                   module = module,
                                   protocal = inner_protocal,
                                   is_basic = False,
                                   project = cur_project,
                                   provider_type = 2,
                                   )
        segment_type.save()
        CustomType.objects.filter(id=customtype.id).update(type = segment_type)

    enumlist = message_dict['enumlist'];
    for e in enumlist:
        doSyncEnum(context, module, customtype, e, 2);

    nestedtypelist = message_dict['nestedtypelist'];
    for n in nestedtypelist:
        doSyncCustomType(context, module, customtype, n, 2)

    fieldlist = message_dict['fieldlist'];
    for field in fieldlist:
        doSyncCustomTypeField(context, module, customtype, field)


def doSyncMessageField(context, module, message, field_dict):
    segment_name = field_dict['name']
    segment_desc = field_dict['desc']
    segment_type_type = field_dict['type']

    segment_protocal_type_id = field_dict['label']
    segment_namespace = message.namespace + '.' + segment_name

    segment_type = None
    segment_default_enum_segment = None
    if segment_type_type == FieldType.TYPE_ENUM:
        segment_type_name = field_dict['type_name'][1:]
        segment_type = get_object_or_404(Enum, namespace=segment_type_name).type
        if field_dict.has_key('default_value'):
            default_value_namespace = segment_type_name + '.' + field_dict['default_value']
            segment_default_enum_segment = get_object_or_404(EnmuSegment, namespace=default_value_namespace)
    elif segment_type_type == FieldType.TYPE_MESSAGE:
        segment_type_name = field_dict['type_name']
        segment_type = get_object_or_404(CustomType, namespace=segment_type_name).type
    else:
        customtype_segment_type = get_object_or_404(SegmentType, name=FName[segment_type_type])

    segment_extra_type1 = None
    segment_extra_type2 = None
    segment_protocal_type = get_object_or_404(SegmentProtoType, pk=segment_protocal_type_id) 

    try:
        segment = Segment.objects.filter(namespace = segment_namespace)[0]
    except IndexError:
        segment = None

    if segment == None:
        segment = Segment(name = strip(segment_name),
                            desc = segment_desc,
                            protocal = message,
                            protocal_type = segment_protocal_type,
                            type = segment_type,
                            extra_type1 = segment_extra_type1,
                            extra_type2 = segment_extra_type2,
                            namespace = strip(segment_namespace),
                            defaultEnum = segment_default_enum_segment
                            )

        segment.save()
    else:
        cur_segment.update(name = strip(segment_name),
                            desc = segment_desc,
                            protocal = message,
                            protocal_type = segment_protocal_type,
                            type = segment_type,
                            extra_type1 = segment_extra_type1,
                            extra_type2 = segment_extra_type2,
                            namespace = strip(segment_namespace),
                            defaultEnum = segment_default_enum_segment
                            )


def doSyncMessage(context, module, message_dict):
    cur_project = context.cur_project
    protocal_name = message_dict['name'];
    protocal_desc = message_dict['desc'];
    protocal_namespace = module.namespace + '.' + protocal_name
    if not message_dict.has_key('id'):
        return doSyncCustomType(context, module, None, message_dict)

    protocal_protocal_id = message_dict['id'];
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
        doSyncEnum(context, module, message, e, 1);

    nestedtypelist = message_dict['nestedtypelist'];
    for n in nestedtypelist:
        doSyncCustomType(context, module, message, n, 1)

    fieldlist = message_dict['fieldlist'];
    for field in fieldlist:
        doSyncMessageField(context, module, message, field)


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