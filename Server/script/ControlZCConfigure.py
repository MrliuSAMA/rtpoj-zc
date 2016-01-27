from __future__ import print_function
import getopt
import sys
import re
import getopt
import subprocess

PREFIX = "/opt/RootZoneExchangeServer/"

def show():
	f = open(PREFIX+"Configuration.in",'r')
	filelines = f.readlines()
	for i in filelines:
		t = i.strip().split()
		print ("%s=%s," % (t[0],t[2]))
	f.close()

def change(bindip,bindport,datafilepath):
	f = open(PREFIX+"Configuration.in",'r')
	filelines = f.readlines()
	for i in range(len((filelines))):
		if filelines[i].strip().split()[0] == "ServerIP":
			if bindip == "dummy":
				pass
			else:
				filelines[i] = "%s\t%s\t%s\n" % ("ServerIP","=",bindip)

		if filelines[i].strip().split()[0] == "ServerPort":
			if bindport == "dummy":
				pass
			else:
				filelines[i] = "%s\t%s\t%s\n" % ("ServerPort","=",bindport)
		
		if filelines[i].strip().split()[0] == "InputZoneFile":
			if datafilepath == "dummy":
				pass
			else:
				filelines[i] = "%s\t%s\t%s\n" % ("InputZoneFile","=",datafilepath)		

	f.close()
	print (filelines)
	f = open(PREFIX+"Configuration.in",'w')
	f.writelines(filelines)
	f.close()

def update(inputstr):
	line = inputstr.strip().split(',')
	change(line[0],line[1],"dummy")

	cmd0 = "sudo python %sRestartExchangeServer.py &"  % PREFIX
	sub0 = subprocess.Popen(cmd0, shell=True)
	sub0.wait()


	cmd = "sudo service named restart"
	sub = subprocess.Popen(cmd, shell=True)
	sub.wait()
	









def main(argv):
	bindip = "dummy"
	bindport = "dummy"
	datafilepath = "dummy"

	try:
		opts,args = getopt.getopt(argv[1:], "i:p:d:", ["show","change","update="])
	except getopt.GetoptError,info:
		print (info.msg)
		PrintUsage()
		sys.exit()

	for option,value in opts:
		if option in ('-i'):
			bindip = value
		elif option in ('-p'):
			bindport = value
		elif option in ('-d'):
			datafilepath = value
		else:
			pass

	for option,value in opts:
		if option in ("--show"):
			show()
		elif option in ('--change'):
			change(bindip,bindport,datafilepath)
		elif option in ('--update'):
			update(value) 
		else:
			sys.exit()

if __name__ == "__main__":
	main(sys.argv)	
