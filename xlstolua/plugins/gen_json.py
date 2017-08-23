
import sys
import os
from cStringIO import StringIO
import json

_files = {}

def type_name():
    return 'json'

def my_path():
    return '/json/Config/GameConfigs'

def my_suffix():
    return 'json'

class Writer(object):
    def __init__(self, prefix=None):
        self.io = StringIO()
        self.__indent = ''
        self.__prefix = prefix

    def getvalue(self):
        return self.io.getvalue()

    def getindent(self):
        return self.__indent

    def __enter__(self):
        self.__indent += '    '
        return self

    def __exit__(self, type, value, trackback):
        self.__indent = self.__indent[:-4]

    def __call__(self, data):
        self.io.write(self.__indent)
        if self.__prefix:
            self.io.write(self.__prefix)
        self.io.write(data)

def addHepler(name):
    s  = "function %s.get(id)\n"%name
    s += "  return %s[\"items\"][tostring(id)];\n"%name
    s += "end\n"
    return s

def write_header(writer):
    writer("""-- Generated By Tool Do not Edit
""")

def is_skip( scheme ) :
    if cmp( scheme, '' ) == 0 :
        return True
    elif cmp( scheme, '$' ) == 0 :
        return True
    elif cmp( scheme.upper(), 'SKIP' ) == 0 :
        return True
    return False

def try_fromat_int( data ) :
    try:
        if type(data) == type(list()):
            for i in range(len(data)):
                if type(data[i]) == type(list()):
                    data[i] = try_fromat_int(data[i])
                else:
                    data[i] = int(data[i])
            return data

        array_value = eval(data);
        return array_value;
    except:
        a_int_value = 0
        try:
            a_int_value = int(float(data))
        except:
            return 0
    return a_int_value

def try_format_string( data ) :
    try:
        array_value = eval(data);
        return array_value;
    except:
        pass

    return data

def try_format_array( data ) :
    try:
        array_value = eval(data);
        return array_value;
    except:
        return list();

    return list();

def try_format_value( typeStr, nameStr, data ) :
    if typeStr.lower() == "int":
        return try_fromat_int(data)
    elif typeStr.lower() == "string":
        return try_format_string(data)
    elif typeStr.lower() == "lang":
        return try_format_string(data)
    elif typeStr.lower() == "array":
        return try_format_array(data)

def code_gen_field(key, value, indent=''):
    with Writer(indent) as field_context:
        if key == None :
            if type(value) == type(1) or type(value) == type(1.0):
                field_context('%d,\n'%int(value))
            elif type(value) == type("s"):
                field_context('"%s",\n'%(value))
            elif type(value) == type(u's'):
                field_context(('"%s",\n'%(value)).encode('utf-8'))
            elif type(value) == type(list()):
                field_context('{\n')
                list_fields = []
                for v in value:
                    list_fields.append(code_gen_field(None, v, indent))
                map(field_context, list_fields)
                field_context(indent+'},\n')
        else:
            if type(value) == type(1):
                field_context('["%s"] = %d,\n'%(key,value))
            elif type(value) == type("s"):
                field_context('["%s"] = "%s",\n'%(key,value))
            elif type(value) == type(u's'):
                field_context(('["%s"] = "%s",\n'%(key,value)).encode('utf-8'))
            elif type(value) == type(list()):
                field_context(('["%s"] = {\n'%(key)).encode('utf-8'))
                list_fields = []
                for v in value:
                    list_fields.append(code_gen_field(None, v, indent+field_context.getindent()))
                map(field_context, list_fields)
                field_context(indent+field_context.getindent()+'},\n')

    return field_context.getvalue()

def code_gen_datas(data_desc, config_desc):
    with Writer() as context:
        version = data_desc.version
        key = data_desc.key
        content = data_desc.content
        context(('["%s"] = {\n'%key).encode('utf-8'))
        _data = []
        for j in range(0, len(config_desc.attrs)):
            attrs = config_desc.attrs[j]
            attr_type = attrs.type
            attr_name = attrs.name
            if is_skip(attr_type):
                continue
            data = code_gen_field(attr_name, try_format_value(attr_type, attr_name, content[j]))
            _data.append(data);

        map(context, _data)
        context('},\n')

    return context.getvalue()

def code_gen_config(config_desc):
    context = Writer()
    write_header(context)
    context('local %s = {\n'%config_desc.name)

    _datas = [];
    for (k,v) in config_desc.attr_datas.items():
        _datas.append(code_gen_datas(v, config_desc))

    map(context, _datas)
    context('}\nreturn %s\n'%config_desc.name)
    return context.getvalue();


def code_gen_file(file_desc):
    export_file_names = {};
    for config in file_desc.configs:
        #context_value = code_gen_config(config)
        context_value = json.dumps(config.name, ensure_ascii = False, sort_keys=True, indent=4)
        export_file_names[config.name + '.' + my_suffix()] = context_value

    for (k,v) in export_file_names.items():
        _files[k] = v

def gen_code(req, toPath):
    print '.........start gen type : '+type_name()+'..........'
    gen_path = toPath + my_path()
    if not os.path.exists( gen_path ) :
        os.makedirs(gen_path)

    #clean up dir
    for filename in os.listdir(gen_path) :
        name, suffix = filename.split( '.' )
        if  suffix == my_suffix() :
            os.remove(gen_path+"/"+filename)

    for file_desc in req.files:
        code_gen_file(file_desc)

    for k,v in _files.iteritems():
        f = file(gen_path+'/'+k,"w")
        f.write(v);
        f.close()

    print '.........end gen type : '+type_name()+'............'