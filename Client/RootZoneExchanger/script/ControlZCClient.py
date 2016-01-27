from __future__ import print_function
import getopt
import sys
import re
import getopt
import subprocess

PREFIX = "/opt/RootZoneExchange/RootZoneExchanger/"

def startService(ControlPREFIX = PREFIX):
	cmd = 'ps -ef | grep "python %sExchangeClient.py"' % ControlPREFIX
	sub = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	sub.wait()
	reslines = sub.stdout.readlines()
	for lines in reslines:
		if lines.split()[2] == '1':
			print("program already start")
			return	

	cmd1 = "python %sExchangeClient.py -q %sQuery.in -c %sConfiguration.in -z &" % (PREFIX,PREFIX,PREFIX)
	#sub1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE, shell=True)
	sub1 = subprocess.Popen(cmd1, shell=True)
#	readlines = sub1.stdout.readlines()
	sub1.wait()

	#print (os.system("pwd"))
	'''
	cmdtemp = "pwd"
	#sub1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE, shell=True)
	subtemp = subprocess.Popen(cmdtemp, stdout=subprocess.PIPE, shell=True)
	readlines_t = subtemp.stdout.readlines()
	print (readlines_t)
	subtemp.wait()
	'''

	sub2 = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	reslines = sub2.stdout.readlines()
	pid = "dummy"
	for lines in reslines:
		if lines.split()[2] == '1':
			pid = lines.split()[1]
			print (pid)
	
def stopService(ControlPREFIX = PREFIX):
	cmd = 'ps -ef | grep "python %sExchangeClient"' % ControlPREFIX
	sub = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	sub.wait()
	reslines = sub.stdout.readlines()
	pid = "dummy"
	for lines in reslines:
		if lines.split()[2] == '1':
			pid = lines.split()[1]
			print (pid)
 
	sub1 = subprocess.Popen("sudo kill -9 %s" % pid, stdout=subprocess.PIPE, shell=True)
	sub1.wait()

def runServiceOnce(ControlPREFIX = PREFIX):
	cmd = "python %sPeroidicExchangeClientBasic.py &" % ControlPREFIX
	sub = subprocess.Popen(cmd, shell=True)
	sub.wait()

def updateConfiguration(ControlPREFIX,value):
	items = value.strip().split(',')
	f = open(ControlPREFIX+"Configuration.in",'r')
	filelines = f.readlines()
	for i in range(len((filelines))):
		if filelines[i].strip().split()[0] == "period":
				filelines[i] = "%s\t%s\t%s\n" % ("period","=",items[0])
#		if filelines[i].strip().split()[0] == "ZoneDir":
#				filelines[i] = "%s\t%s\t%s\n" % ("ZoneDir","=",items[0][7:])
#		if filelines[i].strip().split()[0] == "SigDir":
#				filelines[i] = "%s\t%s\t%s\n" % ("SigDir","=",items[1][7:])		
	f.close()
#	print (filelines)
	f = open(ControlPREFIX+"Configuration.in",'w')
	f.writelines(filelines)
	f.close()

	stopService(ControlPREFIX)
	startService(ControlPREFIX)



def main(argv):
	try:
		opts,args = getopt.getopt(argv[1:], "h", ["stop","start","restart","runonce","update="])
	except getopt.GetoptError,info:
		print (info.msg)
		PrintUsage()
		sys.exit()
	for option,value in opts:
		if option in ("--start"):
			startService(PREFIX)
		elif option in ('--stop'):
			stopService(PREFIX)
		elif option in ('--restart'):
			stopService(PREFIX)
			startService(PREFIX)
		elif option in ('--runonce'):
			runServiceOnce(PREFIX)
		elif option in ('--update'):
			updateConfiguration(PREFIX,value)
		elif option in ('-h'):
			PrintUsage()
		else:
			PrintUsage()
			sys.exit()

if __name__ == "__main__":
	main(sys.argv)	
