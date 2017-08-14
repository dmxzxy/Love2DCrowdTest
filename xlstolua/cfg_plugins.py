
import os
import sys
import xlrd

CONST_SHEET_ATTRIBUTE_TYPE_ROW = 0
CONST_SHEET_ATTRIBUTE_NAME_ROW = 1
CONST_INFO_ROWS = 3
CONST_INFO_COLS = 1

CONST_VERSION_COLS = 0

class DescriptorFile:
    name = None
    configs = None

class DescriptorConfig:
    name = None
    nrows = None
    ncols = None
    attr_types = None
    attr_names = None
    attr_datas = None


class CodeGenerateRequest():
    files = None
    version = None
    sheets = None
    def __init__(self, files, version):
        self.version = version
        self.files = []
        for f in files:
            self.add_file(f)

    def is_file_can_add(self, file_desc):
        if file_desc.nrows <= CONST_INFO_COLS and file_desc.ncols <= 1:
            return False
        return True


    def add_file(self, f):
        _cfgFile = DescriptorFile()
        _cfgFile.name = f
        _cfgFile.configs = [];

        _workbook = xlrd.open_workbook(f)
        worksheets = _workbook.sheets()
        for worksheet in worksheets :
            _cfg = DescriptorConfig()
            _cfg.name = worksheet.name;
            _cfg.nrows = worksheet.nrows
            _cfg.ncols = worksheet.ncols
            _cfg.attr_types = []
            _cfg.attr_names = []
            for i in range(CONST_INFO_COLS,_cfg.ncols):
                attr_type_str = worksheet.cell_value(CONST_SHEET_ATTRIBUTE_TYPE_ROW,i)
                attr_name = worksheet.cell_value(CONST_SHEET_ATTRIBUTE_NAME_ROW,i)
                _cfg.attr_types.append(attr_type_str)
                _cfg.attr_names.append(attr_name)
            _cfgFile.configs.append(_cfg)
        self.files.append(_cfgFile)

if __name__ == "__main__" :
    files = ['xls/test.xlsm']
    req = CodeGenerateRequest(files, '1.1')




# step1 export all excel data into dict 
# 

# step2 