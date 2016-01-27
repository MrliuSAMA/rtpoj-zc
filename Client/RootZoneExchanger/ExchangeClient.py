#coding=utf-8
#!/usr/bin/env python
import getopt
import sys
import subprocess
import pprint
import re
import logging
import os
import getpass
import time
import json
import sched
import os

debug = 0
version = "0.1"


def PrintUsage():
	#usage file To help start program

	print "\n\n\n\n\t\tCheck RRsets Tools"+"[version %s]\t\t\n" % version 
	print "usage: chkrr\t[-v version][-f=file_path filemode][-h help manual]"
	print "\t\t[-D debug info][-d short debug info][-l log record]"
	print "\t\t[-t=dst_ip query target][-p=dst_port query target]"
	print "\t\t[-k=turstkey_path] Name *Class Type"
	print "\n"
	print "The most commonly used git commands are:"
	print "   -v\t Show current version of program"
	print "   -t\t Decide DNS query Target IP"
	print "   -p\t Decide DNS query Port"
	print "   --help\t"
	print "   -h\t Show the help manual of program"
	print "   -d\t Show brief debug info to debuger"
	print "   -D\t Show detailed debug info to debuger"
	print "   -l\t Recording log to file,log will write each query&answer"
	print "   -k\t Trusted-key path to verify fetched record"
	print "   -f\t Batch  mode,lunch multi items in file."
	print "   \t cautions! Batchmode will ignore args except -l"
	print "\n"
	print "Some usage tips, maybe it will helps:"
	print "   1.  ExchangeClient.py cn. NS -t 127.0.0.1"
	print "   2.  ExchangeClient.py cn. IN NS -t 127.0.0.1"
	print "   3.  ExchangeClient.py cn. NS -t 127.0.0.1 -d"
	print "   4.  ExchangeClient.py cn. NS -t 127.0.0.1 -D"
	print "   5.  ExchangeClient.py -f ./queryfile.in"
	print "\n"	




def PrintVersion():
	print version



def ExtractParameter(ConfigurationFile):
#	print ConfigurationFile
	#get parameters from configuration files
	if ConfigurationFile == "dummy":
		ConfigurationFile = "./Configuration.in"

	f = open(ConfigurationFile, 'r')
	fileContent = f.read()
	f.close()
#	print fileContent

	period = re.search("Period\s*=\s*([0-9]*)", fileContent).group(1)
	outputName = re.search("OutputName\s*=\s*([a-zA-Z0-9\./]*)", fileContent).group(1)
	queryFile = re.search("DataOriginFile\s*=\s*([a-zA-Z0-9\./]*)", fileContent).group(1)
	prefix = re.search("Prefix\s*=\s*([a-zA-Z0-9\./]*)", fileContent).group(1)
	backupFilePath = re.search("BackupFilePath\s*=\s*([a-zA-Z0-9\./]*)", fileContent).group(1) 
	trueFilePath = re.search("CurFilePath\s*=\s*([a-zA-Z0-9\./]*)", fileContent).group(1)
	logPath = re.search("LogPath\s*=\s*([a-zA-Z0-9\./]*)", fileContent).group(1)


	return period, outputName, queryFile, prefix, \
		prefix+'/'+backupFilePath, prefix+'/'+trueFilePath, prefix+'/'+logPath



def init(Period, OutputName, QueryFile, Prefix, BackupFolder, FinalFolder, LogFolder):
	#total initial work
	init_directory(Prefix, BackupFolder, FinalFolder, LogFolder)

	init_logging(LogFolder)

	init_environ()

	#print os.system("whoami")

	#pprint.pprint(os.environ)



def init_directory(Prefix, BackupFolder, FinalFolder, LogFolder):
	# init_directory module must not use logging grammar
	# create & change attribute of folder

	currentUser = getpass.getuser()
	if os.path.exists(BackupFolder)==False:
		cmdstring = "sudo mkdir -p %s && sudo chown -R %s %s && sudo chgrp -R %s %s && chmod -R 775 %s" \
				 % (BackupFolder, currentUser, Prefix, currentUser, Prefix, Prefix)  
#		print cmdstring
		sub = subprocess.Popen(cmdstring, shell=True)
		sub.wait()

	if os.path.exists(FinalFolder)==False:
		cmdstring = "sudo mkdir -p %s && sudo chown -R %s %s && sudo chgrp -R %s %s && chmod -R 775 %s" \
				 % (FinalFolder, currentUser, Prefix, currentUser, Prefix, Prefix)  
#		print cmdstring
		sub = subprocess.Popen(cmdstring, shell=True)
		sub.wait()

	if os.path.exists(LogFolder)==False:
		cmdstring = "sudo mkdir -p %s && sudo chown -R %s %s && sudo chgrp -R %s %s && chmod -R 775 %s" \
				 % (LogFolder, currentUser, Prefix, currentUser, Prefix, Prefix)  
#		print cmdstring
		sub = subprocess.Popen(cmdstring, shell=True)
		sub.wait()

	#init tempfile directory
	if os.path.exists("/tmp/root-zone-exchanger")==True:
		cmdstring = "rm -f /tmp/root-zone-exchanger/*.*"
		sub = subprocess.Popen(cmdstring, shell=True)
		sub.wait()
	else:
		cmdstring = "sudo mkdir -p %s && sudo chown -R %s %s && sudo chgrp -R %s %s && chmod -R 775 %s" \
			% ("/tmp/root-zone-exchanger", currentUser, "/tmp/root-zone-exchanger", \
				currentUser,"/tmp/root-zone-exchanger", "/tmp/root-zone-exchanger")
#		print cmdstring
		sub = subprocess.Popen(cmdstring, shell=True)	
		sub.wait()


	return  None


def init_environ():
	os.environ["HOME"] = "/home/nagios"
	os.environ["LOGNAME"] = "nagios"
	os.environ["USER"] = "nagios"
	os.environ["USERNAME"] = "nagios"
	#print "******"
	#f = open("/tmp/ttttt.txt")
	#print os.system("pwd")
	#f.wirte(k[0])

	#f.wirte(k[1])
	#f.close()
	#print "******"
	os.chdir("/tmp")



class Whitelist(logging.Filter):
	def __init__(self, *whitelist):
		self.whitelist = [logging.Filter(name) for name in whitelist]
	def filter(self, record):
        		return any(f.filter(record) for f in self.whitelist)

class Blacklist(Whitelist):
	def filter(self, record):
		return not Whitelist.filter(self, record)

def init_logging(LogFolder):
	#init logging module

	# create logger with "run_logger"
	run_logger = logging.getLogger("run_logger")
	run_logger.setLevel(logging.DEBUG)

	# create file handler 
	run_fh = logging.FileHandler("%s/run.log" % LogFolder, "a")
	run_fh.setLevel(logging.DEBUG)

	# create formatter and add it to the handlers
	formatter = logging.Formatter("%(asctime)s %(filename)s[line:%(lineno)4d] %(levelname)-8s %(message)s", \
					"%Y-%m-%d %H:%M:%S")
	run_fh.setFormatter(formatter)

	#add handler to filter
	run_logger.addHandler(run_fh)
	run_logger.info('#'*30 + "A New restart of Run Log:")		



	# create logger with "data_logger"
	data_logger = logging.getLogger("data_logger")
	data_logger.setLevel(logging.DEBUG)

	# create file handler 
	run_fh = logging.FileHandler("%s/data.log" % LogFolder, "a")
	run_fh.setLevel(logging.DEBUG)

	# create formatter and add it to the handlers
	formatter = logging.Formatter("%(asctime)s %(filename)s[line:%(lineno)4d] %(levelname)-8s %(message)s", \
					"%Y-%m-%d %H:%M:%S")
	run_fh.setFormatter(formatter)

	#add handler to filter
	data_logger.addHandler(run_fh)
	data_logger.info('#'*30 + "A New restart of Data Log:")

	#not writing logging to console
#	root_logging = logging.getLogger()
#	for handler in logging.root.handlers:
#		handler.addFilter("ghty")
	return None




def verify_result(list):
	run_logger = logging.getLogger("run_logger")
	run_logger.debug("enter function verify_result()")
	res1 = re.search("SUCCESS", list[-1][-1])
	if res1 != None:
		return "Verifyed"
	res2 = re.search("FAILED", list[-1][-1])
	if res2 != None:
		return "Unpassed"



def extract_answer(list):
	run_logger = logging.getLogger("run_logger")
	run_logger.debug("enter function extract_answer()")
	result = []
	for i in list[0]:
		result.append(i.strip().split())
	return result[1:]
		



def split2block(total):
	run_logger = logging.getLogger("run_logger")
	run_logger.debug("enter function split2block()")
	total.append('\n')
	split_list = []
	lastsplit = -1
	for num in range(len(total)):
		if total[num] != '\n':
			pass
		if total[num] == '\n':
			if num-lastsplit == 1:
				lastsplit = num
				continue
			split_list.append(total[lastsplit+1:num])
			lastsplit = num

	return split_list

	

#	发送一次dig查询，并且返回该次查询的答案以及对答案校验的结果
def Proc(Name, Type, Dst, DstPort, KeyPath, DebugMode):
	run_logger = logging.getLogger("run_logger")
	data_logger = logging.getLogger("data_logger")
	run_logger.debug("enter function Proc()")


	if DebugMode == "dig" or DebugMode == "drill":
		pass
	else:
		run_logger.warning("Debug mode not defined, data-log info can not write")

	cmd = "dig @%s %s %s -p %s +sigchase +trusted-key=%s" % (Dst,Name,Type,DstPort,KeyPath)
	run_logger.info(cmd)
	sub=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
	sub.wait()
	lLineList = sub.stdout.readlines()
	pprint.pprint(lLineList)
	lBlocks = split2block(lLineList)
	sStatus = verify_result(lBlocks)
	lAnswer = extract_answer(lBlocks)
	if DebugMode == "dig":
		#write dig data log info
		data_logger.info(cmd)
		content = "\n"
		lino = 1
		for line in lLineList:
			line = ("[%3d]" % lino) + line
			content = content + line
			lino = lino + 1
		data_logger.debug(content)
	if DebugMode == "drill":
		#write drill data log info
		cmd = "drill @%s %s %s -S -k %s -p %s" % (Dst,Name,Type,KeyPath,DstPort)
		data_logger.info(cmd)
		sub = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
		sub.wait()
		LineList = sub.stdout.readlines()
		content = "\n"
		lino = 1
		for line in LineList:
			line = ("[%3d]" % lino) + line
			content = content + line
			lino = lino + 1
		data_logger.debug(content)	


	
	return sStatus,lAnswer



#	批处理文件中的查询，文件中的每一行都对应3个问题(A,NS,DS),多次调用Proc()函数，
#	来返回查询结果和校验结果。
def ProcFile(BatchPath, DebugMode):
	run_logger = logging.getLogger("run_logger")
	run_logger.debug("enter function ProcFile()")
	#handle each query in query file
	tempdir = "/tmp/root-zone-exchanger"
	nowtime = time.strftime("%F_%T_")
	outputFileName = nowtime+"Query.out"
	fullOutputFileName = "%s/%s" % (tempdir, outputFileName)

	#status variable
	datasource = []
	totalnumber = 0
	total = []
	successnumber = 0
	success = []

	fileIn = open(BatchPath, 'r')
	fileOut = open(fullOutputFileName, 'w')
	lQuery = fileIn.readlines()
	for eachline in lQuery:
		#write record
		totalnumber = totalnumber + 1
		total.append(eachline.strip().split()[0])
		datasource.append(eachline.strip().split()[1])
		#write end
		if eachline.strip().split()[-1] == "0":
			continue
		item = eachline.strip().split()
		sStatusNS,lAnswerNS = Proc(item[0],"NS",item[1],item[2],item[3], DebugMode)
		#wite recoed
		print sStatusNS,lAnswerNS
		if sStatusNS == "Verifyed":
			successnumber = successnumber + 1
			success.append(lAnswerNS[0][0])
		#write end
		for k in lAnswerNS:
		#	fileOut.write("%s\t%s\t%s\t%s\t%s\n" % (k[0],k[1],k[2],k[3],k[4]))
			fileOut.write('\t'.join(k)+'\n')
		for i in lAnswerNS:
			sStatusA,lAnswerA = Proc(i[4],'A',item[1],item[2],item[3], DebugMode)
			for j in lAnswerA:
		#		fileOut.write("%s\t%s\t%s\t%s\t%s\n" % (j[0],j[1],j[2],j[3],j[4]))
				fileOut.write('\t'.join(j)+'\n')

	for eachline in lQuery:
		if eachline.strip().split()[-1] == "0":
			continue
		item = eachline.strip().split()
		sStatusNS,lAnswerNS = Proc(item[0],"DS",item[1],item[2],item[3], DebugMode)
		for k in lAnswerNS:
		#	fileOut.write("%s\t%s\t%s\t%s\t%s\n" % (k[0],k[1],k[2],k[3],k[4]))
			fileOut.write('\t'.join(k)+'\n')

	fileIn.close()
	fileOut.close()

	#write record file
	recordDict = {}
	recordDict["DataSource"] = datasource
	recordDict["FetchTime"] = nowtime
	recordDict["TotalNumber"] = totalnumber
	recordDict["TotalItems"] = total
	recordDict["SuccessNumber"] = successnumber
	recordDict["SuccessItems"] = success
	RecordFileName = nowtime + "Query.log"
	fp= open("%s/%s" % (tempdir,RecordFileName) ,"w")
	json.dump(recordDict, fp, indent=4, sort_keys=True)
	fp.close()


	return outputFileName, RecordFileName


def Move(outputFileName, RecordFileName, BackupFolder, FinalFolder):
	run_logger = logging.getLogger("run_logger")
	run_logger.debug("enter function Move()")
	tempdir = "/tmp/root-zone-exchanger"
	#move downloaded file to backup folder
	runcmd = "mv -t %s %s/%s %s/%s"  \
			% (BackupFolder, tempdir, outputFileName, tempdir, RecordFileName)
	run_logger.debug(runcmd)
	sub = subprocess.Popen(runcmd, shell=True)
	sub.wait()
	if sub.returncode != 0:
		run_logger.warning("move downloaded file to backup folder failed")

	#clear final folder
	runcmd = "rm -f %s/root.zone.exchangedata" % FinalFolder
	run_logger.info(runcmd)
	sub = subprocess.Popen(runcmd, shell=True)
	sub.wait()
	if sub.returncode != 0:
		run_logger.warning("clear final folder failed")

	#move files from backupfolder to finalfolder
	runcmd = "cp %s/%s %s/%s" % (BackupFolder, outputFileName, FinalFolder, "root.zone.exchangedata")
	run_logger.info(runcmd)
	sub = subprocess.Popen(runcmd, shell=True)
	sub.wait()
	if sub.returncode != 0:
		run_logger.warning("move data_files from backupfolder to finalfolder failed")

	runcmd = "cp %s/%s %s/%s" % (BackupFolder, RecordFileName, FinalFolder, "root.zone.log")
	run_logger.info(runcmd)
	sub = subprocess.Popen(runcmd, shell=True)
	sub.wait()
	if sub.returncode != 0:
		run_logger.warning("move log_files from backupfolder to finalfolder failed")



def perform_command(schedule, delay, BatchPath, BackupFolder, FinalFolder):
	run_logger = logging.getLogger("run_logger")
	run_logger.debug("enter function perform_command()")
	schedule.enter(delay, 0, perform_command, (schedule,delay, BatchPath, BackupFolder, FinalFolder))

	outputFile,recordFile = ProcFile(BatchPath, "dig")

	Move(outputFile, recordFile, BackupFolder, FinalFolder)
#	proc(ZoneFileDir,SigFileDir,BackupFolder,FinalFolder)

#BackupFolder, FinalFolder
#timing_exe(int(period_time), configure_filepath_m, res[4], res[5])
def timing_exe(delay, BatchPath, BackupFolder, FinalFolder):
	run_logger = logging.getLogger("run_logger")
	run_logger.debug("enter function timing_exe()")
	schedule = sched.scheduler(time.time,time.sleep)
	schedule.enter(0, 0, perform_command, (schedule, delay, BatchPath, BackupFolder, FinalFolder))
	schedule.run()


def createDaemon():	
	try:
		if os.fork() > 0: os._exit(0)
	except OSError, error:
		print 'fork #1 failed: %d (%s)' % (error.errno, error.strerror)
		os._exit(1)
	os.chdir('/')
	os.setsid()
	os.umask(0)
	try:
		pid = os.fork()
		if pid > 0:
			print 'Daemon PID %d' % pid
			os._exit(0)
	except OSError, error:
		print 'fork #2 failed: %d (%s)' % (error.errno, error.strerror)
		os._exit(1)
	sys.stdout.flush()
	sys.stderr.flush()
	si = file("/dev/null", 'r')
	so = file("/dev/null", 'a+')
	se = file("/dev/null", 'a+', 0)
	os.dup2(si.fileno(), sys.stdin.fileno())
	os.dup2(so.fileno(), sys.stdout.fileno())
	os.dup2(se.fileno(), sys.stderr.fileno())
	main() # function demo

def main():
	# XXX_s means this para for single mode, XXX_m for batch mode
	dst_ip_s = "null"
	dst_port_s = "53"
	query_name_s = "null"
	query_type_s = "null"
	key_path_s = "null"

	query_filepath_m = "null"
	configure_filepath_m = "null"

	debugmode_ms = "null" #dig or drill

	period_time = "null"

#	print sys.argv
	try:
		opts,args = getopt.getopt(sys.argv[1:], "hvdDzq:c:t:p:k:")
	except getopt.GetoptError,info:
		print info.msg
		usage()
		sys.exit()
	for option,value in opts:
		if option in ("-h"):
			usage()
		elif option in ("-v"):
			print version
		#choose tool
		elif option in ("-d"):
			if debugmode_ms == "null":
				debugmode_ms = "drill"
		elif option in ("-D"):
			debugmode_ms = "dig"
		#bacth mode
		elif option in ("-q"):
			query_filepath_m = value
		elif option in ("-c"):
			configure_filepath_m = value
		elif option in ("-z"):
			period_time = "true"
		#single mode
		elif option in ("-t"):
			dst_ip_s = value
		elif option in ("-p"):
			dst_port_s = value
		elif option in ("-k"):
			key_path_s = value
		else:
			print "option not legal! check again"
			usage()	
			sys.exit()
	if len(args) == 3:
		query_name_s = args[0]
		query_type_s = args[2]
	elif len(args) == 2:
		query_name_s = args[0]
		query_type_s = args[1]

	else:
		if query_filepath_m != "null" or configure_filepath_m != "null":
			pass
		else:
			print "args not legal! check again"
			usage()
			sys.exit()

	#batch mode
	if query_filepath_m != "null":
		if configure_filepath_m == "null":
			configure_filepath_m = "./Configuration"
		else:
			pass

		if period_time != "null":
			res = ExtractParameter(configure_filepath_m)

			init(res[0], res[1], res[2], res[3], res[4],res[5], res[6])

			timing_exe(int(res[0]), query_filepath_m, res[4], res[5])
		else:
			res = ExtractParameter(configure_filepath_m)

			init(res[0], res[1], res[2], res[3], res[4],res[5], res[6])

			outputFile,recordFile = ProcFile(query_filepath_m, "dig")

			Move(outputFile, recordFile, res[4], res[5])


	#judge if args is legal ?
	else:
		#single query mode
#		Proc(query_name_s, query_type_s, dst_ip_s, dst_port_s, key_path_s, debugmode_ms)
		pass



if __name__ == "__main__":
	createDaemon()
	#main()
