#coding=utf-8
#!/usr/bin/env python
import getopt
import sys
import subprocess
import pprint
import re
import sched
import time
import ExchangeClient
import os

DownloadPeriod = 12*3600
OutputName = "root.zone.exchangedata"
storepathB = "/var/ZoneExchange/Data/ZoneExchangeBak/"
storepathT = "/var/ZoneExchange/Data/ZoneExchange/"
QueryFile = "./Query.in"		
numcounter = 1

#	
def perform_command(schedule,delay_s):
	schedule.enter(delay_s,0,perform_command,(schedule,delay_s))
	print "run once"
	OutputFilename = ExchangeClient.ProcFile(QueryFile)
	TimedOutputFilename = time.strftime("%F-%H:%M-")+OutputFilename

	cmd1 = "rm -f %s*.*" % storepathT
	sub1 = subprocess.Popen(cmd1,shell=True)
	sub1.wait()

	cmd2 = "mv ./%s %s%s" % (OutputFilename, storepathB,TimedOutputFilename)
	sub2 = subprocess.Popen(cmd2,shell=True)
	sub2.wait()

	cmd3 = "cp %s%s %s%s" % (storepathB, TimedOutputFilename, storepathT, OutputName)
	sub3 = subprocess.Popen(cmd3,shell=True)
	sub3.wait()

def timing_exe(delay = 60):
	delay = int(DownloadPeriod)
	schedule = sched.scheduler(time.time,time.sleep)
	schedule.enter(delay,0,perform_command,(schedule,delay))
	schedule.run()

def init():
	
	global OutputName
	global storepathB
	global storepathT
	global QueryFile
	global DownloadPeriod

	#init parameter
	f = open("./Configuration.in")
	lines = f.readlines()
	DownloadPeriod = lines[0].strip().split()[-1]
	OutputName = lines[1].strip().split()[-1]
	storepathB = lines[2].strip().split()[-1]+lines[3].strip().split()[-1]
	storepathT = lines[2].strip().split()[-1]+lines[4].strip().split()[-1]
	QueryFile = lines[5].strip().split()[-1]

	#init folder
	if os.path.exists(storepathB) == False:
		os.makedirs(storepathB)
	if os.path.exists(storepathT) == False:
		os.makedirs(storepathT)






if __name__ == "__main__":
	init()
	print "start periodic task!"
	timing_exe()

