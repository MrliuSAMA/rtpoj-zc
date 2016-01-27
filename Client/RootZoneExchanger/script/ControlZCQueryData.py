from __future__ import print_function
import getopt
import sys
import re
import getopt
import subprocess
import ControlZCClient

PREFIX = "/opt/RootZoneExchange/RootZoneExchanger/"

def show():
	f = open(PREFIX+"Query.in",'r')
	filelines = f.readlines()
	for i in filelines:
		t = i.strip().split()
		print ("%s %s %s %s %s," % (t[0],t[1],t[2],t[3],t[4]), end = "\n")
	f.close()

def on_off(name,ifvalid):
	f = open(PREFIX+"Query.in",'r')
	filelines = f.readlines()
#	print (ifvalid)
	for i in range(len((filelines))):
		if filelines[i].strip().split()[0] == name:
			t = filelines[i].strip().split()
			filelines[i] = "%s\t%s\t%s\t%s\t%s\n" % (t[0],t[1],t[2],t[3],ifvalid)
	f.close()
#	print (filelines)
	f = open(PREFIX+"Query.in",'w')
	f.writelines(filelines)
	f.close()

def change(name,ip,port,keypath):
	f = open(PREFIX+"Query.in",'r')
	filelines = f.readlines()
	for i in range(len((filelines))):
		if filelines[i].strip().split()[0] == name:
			t = filelines[i].strip().split()
			if ip == "dummy":
				ip = t[1]
			if port == "dummy":
				port = t[2]
			if keypath == "dummy":
				keypath = t[3]
			filelines[i] = "%s\t%s\t%s\t%s\t%s\n" % (t[0],ip,port,keypath,t[4])
	f.close()
	print (filelines)
	f = open(PREFIX+"Query.in",'w')
	f.writelines(filelines)
	f.close()

def add(name,ip,port,keypath):
	f = open(PREFIX+"Query.in",'r')
	filelines = f.readlines()
	for i in range(len((filelines))):
		if filelines[i].strip().split()[0] == name:
			print ("key repeated! exit")
			return
		else:
			pass
	f.close()
	line = "%s\t%s\t%s\t%s\t%s\n" % (name,ip,port,keypath,'1')
	f = open(PREFIX+"Query.in",'a')
	f.writelines(line)
	f.close()

def update(str):
	lines = str.strip().split('#')
	f = open(PREFIX+"Query.in",'w')
	for line in lines:
		items = line.strip().split(',')
		f.write("%s\t%s\t%s\t%s\t%s\n" % (items[0],items[1],items[2],items[3],items[4]))
	f.close() 
	ControlZCClient.stopService()
	ControlZCClient.startService()

def main(argv):
	name = "dummy"
	sourceip = "dummy"
	sourceport = "dummy"
	keypath = "dummy"
	ifvalid = "dummy"

	try:
		opts,args = getopt.getopt(argv[1:], "n:s:p:k:v:", ["show","add","switch","change","update="])
	except getopt.GetoptError,info:
#		print (info.msg)
#		PrintUsage()
		sys.exit()

	for option,value in opts:
		if option in ('-n'):
			name = value
		elif option in ('-s'):
			sourceip = value
		elif option in ('-p'):
			sourceport = value
		elif option in ('-k'):
			keypath = value
		elif option in ('-v'):
			ifvalid = value
		else:
			pass

	for option,value in opts:
		if option in ("--show"):
			show()
		elif option in ('--add'):
			add(name,sourceip,sourceport,keypath)
		elif option in ('--switch'):
			on_off(name,ifvalid)
		elif option in ('--change'):
			change(name,sourceip,sourceport,keypath)
		elif option in ('--update'):
			inputstr = value
			update(inputstr)
		else:
			sys.exit()

if __name__ == "__main__":
	main(sys.argv)	
