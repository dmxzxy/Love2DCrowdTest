#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import xlrd

CONST_SHEET_ATTRIBUTE_TYPE_ROW = 0
CONST_SHEET_ATTRIBUTE_NAME_ROW = 1
CONST_INFO_ROWS = 3
CONST_INFO_COLS = 1

CONST_VERSION_COLS = 0

class XlsDocument() :
    def __init__( self, xlsfile ) :
        self._xlsfile = xlsfile
        self._workbook = xlrd.open_workbook( xlsfile )

    def get_sheets( self ) :
        return self._workbook.sheets()

    # 是否需要跳过
    def is_skip( self, scheme ) :
        if cmp( scheme, '' ) == 0 :
            return True
        elif cmp( scheme, '!' ) == 0 :
            return True
        elif cmp( scheme.upper(), 'SKIP' ) == 0 :
            return True
        return False

    # number类型与date类型的特殊处理
    def format_value( self, cell ) :
        value = cell.value
        if cell.ctype == xlrd.XL_CELL_NUMBER :
            # 如果是整数的话, 直接取整
            if cell.value == int( cell.value ) :
                value = int( cell.value )
        elif cell.ctype == xlrd.XL_CELL_DATE :
            datetuple = xlrd.xldate_as_tuple(value, self._workbook.datemode)
            # time only no date component
            if datetuple[0] == 0 and datetuple[1] == 0 and datetuple[2] == 0:
                value = "%02d:%02d:%02d" % datetuple[3:]
            # date only, no time
            elif datetuple[3] == 0 and datetuple[4] == 0 and datetuple[5] == 0:
                value = "%04d/%02d/%02d" % datetuple[:3]
            else: # full date
                value = "%04d/%02d/%02d %02d:%02d:%02d" % datetuple
        return value

    def msg_for_cur_sheet( self, info ) :
        s = "In [ Excel = \"%s\",Sheet = \"%s\"]"%(self._xlsfile,info["sheet"].name)
        return s


    def try_fromat_int( self, info ) :
        cell = info["cell"]
        value = cell.value
        if value == '':
            value = '0'
        try:
            array_value = eval(value);
            return array_value;
        except:
            a_int_value = 0
            try:
                a_int_value = int(float(value))
            except:
                print("Error in sheet:%s at column[%s] cell[%d,%d],value:%s"%(self.msg_for_cur_sheet(info),info["nameStr"],info["row"],info["col"],value))
                return 0
        return a_int_value

    def try_format_string( self, info ) :
        cell = info["cell"]
        value = cell.value
        try:
            array_value = eval(value);
            return array_value;
        except:
            pass

        if cell.ctype == xlrd.XL_CELL_DATE :
            datetuple = xlrd.xldate_as_tuple(value, self._workbook.datemode)
            # time only no date component
            if datetuple[0] == 0 and datetuple[1] == 0 and datetuple[2] == 0:
                value = "%02d:%02d:%02d" % datetuple[3:]
            # date only, no time
            elif datetuple[3] == 0 and datetuple[4] == 0 and datetuple[5] == 0:
                value = "%04d/%02d/%02d" % datetuple[:3]
            else: # full date
                value = "%04d/%02d/%02d %02d:%02d:%02d" % datetuple
            return value
        else:
            return value

    def try_format_array( self, info ) :
        cell = info["cell"]
        value = cell.value
        try:
            array_value = eval(value);
            return array_value;
        except:
            print("Error in sheet:%s at column[%s] cell[%d,%d],value:%s"%(self.msg_for_cur_sheet(info),info["nameStr"],info["row"],info["col"],value))
            return list();

        return list();


    def format_value2( self, sheet, row, col, typeStr, nameStr ) :
        info = {"sheet":sheet, "nameStr":nameStr, "row":row, "col":col, "cell":sheet.cell(row,col)}
        if typeStr.lower() == "int":
            return self.try_fromat_int(info)
        elif typeStr.lower() == "string":
            return self.try_format_string(info)
        elif typeStr.lower() == "array":
            return self.try_format_array(info)



class xlsExport2Lua() :
    CONST_EXPORT_TO_DIR = 1
    CONST_EXPORT_TO_FILE = 2
    def __init__( self, xlsfile, dst ) :
        self._xlsfile = xlsfile
        self._xlsdoc = XlsDocument( xlsfile )
        self._dst = dst;
        self._exportTo = self.CONST_EXPORT_TO_DIR
        if os.path.isdir(dst):
            self._exportTo = self.CONST_EXPORT_TO_DIR
        elif os.path.isfile(dst):
            self._exportTo = self.CONST_EXPORT_TO_FILE
        else:
          print "it's a special file (socket, FIFO, device file)"

    def writeValueToLua(self, fileTo, key, value, indent) :
        if type(value) == type(1):
            if key == None :
                fileTo.write(indent + "%d,\n"%value)
            else:
                fileTo.write(indent + "[\"%s\"] = %d,\n"%(key,value))
        elif type(value) == type("s"):
            if key == None :
                fileTo.write(indent)
                fileTo.write(value.encode("utf8"))
                fileTo.write("\",\n")
            else:
                fileTo.write(indent + "[\"%s\"] = \""%key)
                fileTo.write(value.encode("utf8"))
                fileTo.write("\",\n")
        elif type(value) == type(u's'):
            if key == None :
                fileTo.write(indent)
                fileTo.write(value.encode("utf8"))
                fileTo.write("\",\n")
            else:
                fileTo.write(indent + "[\"%s\"] = \""%key)
                fileTo.write(value.encode("utf8"))
                fileTo.write("\",\n")
        elif type(value) == type(list()):
            if key == None :
                fileTo.write(indent + "{\n")
            else:
                fileTo.write(indent + "[\"%s\"] = {\n"%key)
            indentList = indent + "  "
            for v in value:
                self.writeValueToLua(fileTo, None, v, indentList)
            fileTo.write(indent + "},\n")


    def writeDictToLua(self, fileTo, key, dictSrc, indent, isroot) :
        if isroot :
            tableHead = indent + "local %s = {\n"%key
            tableTail = indent + "}\nreturn %s\n"%key
        else: 
            tableHead = indent + "[\"%s\"] = {\n"%key
            tableTail = indent + "},\n"

        fileTo.write(tableHead);
        indent += "  "

        for (k,v) in dictSrc.items() :
            if type(v) == type(dict()):
                self.writeDictToLua(fileTo, k, v, indent, False)
            else:
                self.writeValueToLua(fileTo, k, v, indent)
        fileTo.write(tableTail);

    def export ( self ) :
        fileList = list()
        worksheets = self._xlsdoc.get_sheets();
        for worksheet in worksheets :
            num_rows = worksheet.nrows
            num_cols = worksheet.ncols
            if num_rows <= CONST_INFO_ROWS and num_cols <= 1 :
                continue
            if not worksheet.cell_value(CONST_SHEET_ATTRIBUTE_TYPE_ROW,CONST_VERSION_COLS) == '$':
                continue
            fileName = worksheet.name;
            sheetDict = dict()
            items = dict();
            for i in range(CONST_INFO_ROWS,num_rows):
                a_version = worksheet.cell_value(i, CONST_VERSION_COLS)
                a_id = int(worksheet.cell_value(i, CONST_INFO_COLS))
                a_content = dict()
                for j in range(CONST_INFO_COLS,num_cols):
                    attr_name = worksheet.cell_value(CONST_SHEET_ATTRIBUTE_NAME_ROW,j)
                    attr_type_str = worksheet.cell_value(CONST_SHEET_ATTRIBUTE_TYPE_ROW,j)
                    if self._xlsdoc.is_skip(attr_type_str):
                        continue
                    a_content[attr_name] = self._xlsdoc.format_value2(worksheet,i,j,attr_type_str,attr_name);
                items[a_id] = a_content
            sheetDict["items"] = items;
            lua_path = self._dst + "/" + fileName + ".lua"
            lua_file = file(lua_path, 'w')
            indent = ""
            self.writeDictToLua(lua_file, fileName, sheetDict, indent, True);
            print("write to lua file " + lua_path);
            fileList.append(fileName)
        return fileList


if __name__ == "__main__" :
    op = xlsExport2Lua( sys.argv[1], sys.argv[2] )
    op.export()
