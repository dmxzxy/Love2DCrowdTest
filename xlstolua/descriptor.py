
import os
import sys
import xlrd

CONST_SHEET_ATTRIBUTE_TYPE_ROW = 0
CONST_SHEET_ATTRIBUTE_NAME_ROW = 1
CONST_INFO_ROWS = 3
CONST_INFO_COLS = 1

CONST_VERSION_COLS = 0

class DescriptorFile:
    def __init__(self,name):
        self.name = name
        self.configs = []

class DescriptorData:
    def __init__(self, version, key, content):
        self.version = version;
        self.key = key;
        self.content = content;

class DescriptorAttr:
    def __init__(self, _name, _type, start_col):
        self.name = _name
        self.type = _type
        self.cols = [start_col]
        self.item_cols = 1

class DescriptorConfig:
    def __init__(self, name, nrows, ncols):
        self.name = name
        self.nrows = nrows
        self.ncols = ncols
        self.attrs = []
        self.attr_datas = []

class CodeGenerateRequest():
    files = None
    version = None
    sheets = None
    searching_end_attr_desc = None;
    def __init__(self, files, version):
        self.version = version
        self.files = []
        for f in files:
            self.add_file(f)

    def add_file(self, f):
        file_desc = DescriptorFile(f)

        _workbook = xlrd.open_workbook(f)
        worksheets = _workbook.sheets()
        for worksheet in worksheets :
            self.add_config(worksheet,file_desc)
        self.files.append(file_desc)

    def is_file_can_add(self, cfg_desc):
        if cfg_desc.nrows <= CONST_INFO_COLS and file_desc.ncols <= 1:
            return False
        if len(cfg_desc.attrs) == 0:
            return False
        if not cfg_desc.attrs[0].type == '$':
            return False
        return True

    def add_config(self, worksheet, file_desc):
        config_desc = DescriptorConfig(worksheet.name, worksheet.nrows, worksheet.ncols)
        searching_end_attr_desc = None;
        for i in range(0,config_desc.ncols):
            attr_name = worksheet.cell_value(CONST_SHEET_ATTRIBUTE_NAME_ROW,i)
            attr_type_str = worksheet.cell_value(CONST_SHEET_ATTRIBUTE_TYPE_ROW,i)
            self.add_attr(attr_name, attr_type_str, i, config_desc)

        if self.is_file_can_add(config_desc):
            for i in range(CONST_INFO_ROWS,config_desc.nrows):
                    self.add_data(worksheet, i, config_desc)
            print config_desc.name
            file_desc.configs.append(config_desc)

    def add_attr(self, _name, _type, col, config_desc):
        if not (self.searching_end_attr_desc == None):
            self.searching_end_attr_desc.cols.append(col)
            if _name == ']':
                self.searching_end_attr_desc = None
            return

        attr_desc = None
        if _name[-2:] == ':[':
            if _name[-4:-3] == ':':
                attr_desc = DescriptorAttr(_name[:-4], _type, col)
                attr_desc.item_cols = _name[-3:-2]
            else:
                attr_desc = DescriptorAttr(_name[:-2], _type, col)
            self.searching_end_attr_desc = attr_desc

        if attr_desc == None:
            attr_desc = DescriptorAttr(_name, _type, col)

        config_desc.attrs.append(attr_desc)

    def add_data(self, worksheet, row, cfg_desc):
        version = str(worksheet.cell_value(row, CONST_VERSION_COLS))
        key = worksheet.cell_value(row, CONST_INFO_COLS)
        try:
            key = int(key)
        except:
            key = key

        contents = []
        for attr_desc in cfg_desc.attrs:
            content = None
            if len(attr_desc.cols) == 1:
                content = worksheet.cell_value(row, attr_desc.cols[0])
            else:
                content = []
                for col in attr_desc.cols:
                    content.append(worksheet.cell_value(row, col))
            contents.append(content)

        data = DescriptorData(version, key, contents)
        cfg_desc.attr_datas.append(data)

