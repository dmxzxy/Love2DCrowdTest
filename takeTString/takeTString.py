
import os
import re
import xlrd
import xlwt

CONST_HEAD_ROWS = 3

def getTString(file_path):
	fp = open(file_path, 'r')
	file_text = fp.read()
	digi_str = re.findall(r'_T\("(.*?)"\)',file_text,re.MULTILINE)
	fp.close()
	return digi_str

def writeTStringByFolder(folder_path):
	file = xlwt.Workbook()

	table = file.add_sheet('script_multlang',cell_overwrite_ok=True)
	index = 0

	# write head
	table.write(0,0,'$')
	table.write(1,0,'!')
	table.write(2,0,'#')

	table.write(0,1,'lang')
	table.write(1,1,'id')
	table.write(2,1,'ID')

	table.write(0,2,'lang')
	table.write(1,2,'zhcn')
	table.write(2,2,'zhcn')

	# write body
	list_dirs = os.walk(folder_path) 
	for root, dirs, files in list_dirs:    
		for f in files: 
			lst = getTString(os.path.join(root, f))
			for s in lst:
				table.write(CONST_HEAD_ROWS+index,0,'1.1')
				table.write(CONST_HEAD_ROWS+index,1,s.decode('utf-8'))
				table.write(CONST_HEAD_ROWS+index,2,s.decode('utf-8'))
				index += 1

	file.save('../xlstolua/xls/multlang.xls')


writeTStringByFolder('./');