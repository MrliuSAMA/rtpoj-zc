#coding=utf-8
"""
debuginfo 模块
用于打印各种格式的debug的信息，将打印过程封装成函数
"""
def print_list(list):
	for i in list:
		print i

def print_string(string):
	print string

def print_result(name, types, answer):
	print "query: \n%s IN %s" % (name,types)
	print "answer:"
	for i in answer:
		print i

def print_dict_valueIslist(dict):
	keylist = dict.iterkeys()
	for key in keylist:
		print key
		for valueitem in dict[key]:
			print valueitem

