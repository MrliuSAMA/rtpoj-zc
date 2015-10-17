#!/usr/bin/env python
import getopt
import sys
import subprocess
import DebugInfo
import FindCheck
import pprint
import re
import sched
import time
import CheckRR

OutputPath = r"/root/Tokangning/ZoneExchange"
OutputName = r"root.zone.exchange"
storepathB = r"/home/Tokangning/ZoneExchange.Bak"
storepathT = r"/home/Tokangning/ZoneExchange"
numcounter = 1


def perform_command(schedule,delay_s):
	global numcounter
	schedule.enter(delay_s,0,perform_command,(schedule,delay_s))
	print "run once"
	CheckRR.ProcFile("./queryfile.in")
	cmd1 = "rm %s/*.*" % storepathT
	sub1 = subprocess.Popen(cmd1,shell=True)
	sub1.wait()
	cmd2 = "mv ./queryfile.out %s/%s" % (storepathB,"queryfile.out"+str(numcounter))
	sub2 = subprocess.Popen(cmd2,shell=True)
	sub2.wait()
	cmd3 = "cp %s/%s %s/%s" % (storepathB,"queryfile.out"+str(numcounter),storepathT,OutputName)
	sub3 = subprocess.Popen(cmd3,shell=True)
	sub3.wait()
	numcounter = numcounter+1

def timing_exe(delay = 60*10):
	schedule = sched.scheduler(time.time,time.sleep)
	schedule.enter(delay,0,perform_command,(schedule,delay))
	schedule.run()




if __name__ == "__main__":
	print "start periodic task!"
	timing_exe()

