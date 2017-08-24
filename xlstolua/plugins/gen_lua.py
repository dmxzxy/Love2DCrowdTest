
import sys
import os
from cStringIO import StringIO

ALL_CONFIG_NAME = "GameConfigs"

INDENT = '    '
INDENT_LEN = len(INDENT)

_files = {}

def type_name():
    return 'lua'

def my_path():
    return '/lua/Config/GameConfigs'

def dev_folder_rel():
    return "Config.GameConfig"

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
        self.__indent += INDENT
        return self

    def __exit__(self, type, value, trackback):
        self.__indent = self.__indent[:-INDENT_LEN]

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

def gen_all_config(lua_folder):
    lua_all_config_path = lua_folder + "/" + ALL_CONFIG_NAME + ".lua"
    all_lua_name = []
    
    for root, dirs, files in os.walk(lua_folder): 
        for f in files: 
            file_path = os.path.join(root, f) 
            file_name = os.path.basename(f)
            file_name,file_suffix = os.path.splitext(file_name)
            if file_suffix == ".lua":
                if file_name != ALL_CONFIG_NAME :
                    all_lua_name.append(file_name)
    f = file(lua_all_config_path,"w")
    f.write("%s = {}\n"%(ALL_CONFIG_NAME))
    for name in all_lua_name:
        f.write("%s = require \"%s.%s\"\n"%(name,dev_folder_rel(),name))
        f.write(addHepler(name));
        f.write("%s.%s = %s\n"%(ALL_CONFIG_NAME,name,name))
    f.close()


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
        
    return 0

def try_format_string( data ) :
    try:
        array_value = eval(data);
        return array_value;
    except:
        a_str_value = ''
        try:
            a_str_value = str(data)
        except:
            return a_str_value
        return a_str_value

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

def code_gen_field(key, value, context):
    with context:
        if key == None :
            if type(value) == type(1) or type(value) == type(1.0):
                context('%d,\n'%int(value))
            elif type(value) == type("s"):
                context('"%s",\n'%(value))
            elif type(value) == type(u's'):
                context(('"%s",\n'%(value)).encode('utf-8'))
            elif type(value) == type(list()):
                context('{\n')
                for v in value:
                    code_gen_field(None, v, context)
                context('},\n')
        else:
            if type(value) == type(1):
                context('["%s"] = %d,\n'%(key,value))
            elif type(value) == type("s"):
                context('["%s"] = "%s",\n'%(key,value))
            elif type(value) == type(u's'):
                context(('["%s"] = "%s",\n'%(key,value)).encode('utf-8'))
            elif type(value) == type(list()):
                context(('["%s"] = {\n'%(key)).encode('utf-8'))
                for v in value:
                    code_gen_field(None, v, context)
                context('},\n')

def code_gen_datas(data_desc, config_desc, context):
    with context:
        version = data_desc.version
        key = data_desc.key
        content = data_desc.content
        context(('["%s"] = {\n'%key).encode('utf-8'))
        for j in range(0, len(config_desc.attrs)):
            attrs = config_desc.attrs[j]
            attr_type = attrs.type
            attr_name = attrs.name
            if is_skip(attr_type):
                continue
            code_gen_field(attr_name, try_format_value(attr_type, attr_name, content[j]), context)
        context('},\n')

def code_gen_config(config_desc):
    context = Writer()
    write_header(context)
    context('local %s = {\n'%config_desc.name)
    with context:
        context('["items"] = {\n')
        for (k,v) in config_desc.attr_datas.items():
            code_gen_datas(v, config_desc, context)
        context('}\n')
    context('}\n')
    context('return %s\n'%config_desc.name)
    return context.getvalue();


def code_gen_file(file_desc):
    for config in file_desc.configs:
        _files[config.name + '.lua'] = code_gen_config(config)

def gen_code(req, toPath):
    print '.........start gen type : '+type_name()+'..........'
    gen_path = toPath + my_path()
    if not os.path.exists( gen_path ) :
        os.makedirs(gen_path)

    #clean up dir
    for filename in os.listdir(gen_path) :
        name, suffix = filename.split( '.' )
        if  suffix == 'lua' :
            os.remove(gen_path+"/"+filename)

    for file_desc in req.files:
        code_gen_file(file_desc)

    for k,v in _files.iteritems():
        print 'gen code [%s] file = %s'%(type_name(), k)
        f = file(gen_path+'/'+k,"w")
        f.write(v);
        f.close()

    gen_all_config(gen_path)
    print '.........end gen type : '+type_name()+'............'


if __name__ == "__main__" :
    from descriptor import *
    files = ['../xls/test.xlsm']
    code_gen_requrest = CodeGenerateRequest(files, '1.1')
    gen_code(code_gen_requrest, './')