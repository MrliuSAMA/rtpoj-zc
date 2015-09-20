#!/usr/bin/env python
import getopt
import sys
import subprocess
import DebugInfo
import FindCheck
import pprint
import re

debug = 0
version = "0.1"

def PrintUsage():
	print "\n\n\t\tCheck RRsets Tools"+"[version %s]\t\t\n" % version 
	print "usage: chkrr\t[-v version][-f=file_path filemode][-h help manual]"
	print "\t\t[-D debug info][-d short debug info][-l log record]"
	print "\t\t[-t=dst_ip query target][-p=dst_port query target]"
	print "Name *Class Type"
	print "\n"
	print "The most commonly used git commands are:"
	print "   -v\t Show current version of program"
	print "   -t\t Decide where the DNS query will be send to"
	print "   --help\t"
	print "   -h\t Show the help manual of program"
	print "   -d\t Show brief debug info to debuger"
	print "   -D\t Show detailed debug info to debuger"
	print "   -l\t Recording log to file,log will write each query&answer"
	print "   -f\t Batch mode,lunch multi items in file."
	print "   \t cautions! Batchmode will ignore args except -l"
	print "\n"
	print "Some usage tips, maybe it will helps:"
	print "   1.  chkrr cn. NS -t 127.0.0.1"
	print "   2.  chkrr cn. IN NS -t 127.0.0.1"
	print "   3.  chkrr cn. NS -t 127.0.0.1 -d"
	print "   4.  chkrr cn. NS -t 127.0.0.1 -D"
	print "   5.  chkrr -f ./queryfile.in"
	print "   6.  chkrr -f ./queryfile.in -l"
	print "\n"	


def PrintVersion():
	print version


def VerifyResult(list):
	res1 = re.search("SUCCESS", list[-1][-1])
	if res1 != None:
		return "Verifyed"
	res2 = re.search("FAILED", list[-1][-1])
	if res2 != None:
		return "Unpassed"


def ExtractAnswer(list):
	result = []
	for i in list[0]:
		result.append(i.strip().split())
	
	return result[1:]
		
def SplitToBlock(total):
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


def Proc(Name, Type, Dst, DstPort, KeyPath, DetailDebug=0, ShortDebug=0):
	cmd = "dig @%s %s %s -p %s +sigchase +trusted-key=%s" % (Dst,Name,Type,DstPort,KeyPath)
	if DetailDebug:
		print "|%s debug info start %s|" % ('-'*15,'-'*15)
		cmdseq = "%s | cat -n" % cmd
		getdetail = subprocess.Popen(cmdseq, shell=True, stdout=subprocess.PIPE)
		getdetail.wait()
		print getdetail.stdout.read()
		print "|%s debug info end   %s|" % ('-'*15,'-'*15)
	elif ShortDebug:
		print "|%s debug info start %s|" % ('-'*15,'-'*15)
		cmdseq = "drill @%s %s %s -S -k %s -p %s" % (Dst,Name,Type,KeyPath,DstPort)
		getdetail = subprocess.Popen(cmdseq, shell=True, stdout=subprocess.PIPE)
		getdetail.wait()
		print getdetail.stdout.read()
		print "|%s debug info end   %s|" % ('-'*15,'-'*15)
	else:
		pass
	sub=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
	sub.wait()
	lLineList = sub.stdout.readlines()
	lBlocks = SplitToBlock(lLineList)
	sStatus = VerifyResult(lBlocks)
	lAnswer = ExtractAnswer(lBlocks)
	pprint.pprint(lAnswer)
	
	return sStatus,lAnswer


def ProcFile(BatchPath):
	outputFileName = BatchPath.strip().split('/')[-1].split('.')[-2]+".out"
	fileIn = open(BatchPath, 'r')
	fileOut = open(outputFileName, 'w')
	lQuery = fileIn.readlines()
	for eachline in lQuery:
		item = eachline.strip().split()
		sStatusNS,lAnswerNS = Proc(item[0],item[1],item[2],item[3],item[4])
#		print lAnswerNS
		for k in lAnswerNS:
			fileOut.write("%s\t%s\t%s\t%s\t%s\n" % (k[0],k[1],k[2],k[3],k[4]))
		for i in lAnswerNS:
			sStatusA,lAnswerA = Proc(i[4],'A',item[2],item[3],item[4])
			for j in lAnswerA:
				fileOut.write("%s\t%s\t%s\t%s\t%s\n" % (j[0],j[1],j[2],j[3],j[4]))
	fileIn.close()
	fileOut.close()


def main(argv):
	print argv
	Dst			= "127.0.0.1"
	DstPort		= "53"
	Name		= "."
	Type		= "NS"
	FilePath	= "null"
	ShortDebug	= 0
	DetailDebug = 0
	LogPath		= "null"
	BatchPath	= "null"
	KeyPath		= "/var/namedFaker/trusted-key.key"
	try:
		opts,args = getopt.getopt(argv[1:], "hvdDt:p:l:f:k:", ["help"])
	except getopt.GetoptError,info:
		print info.msg
		PrintUsage()
		sys.exit()
	for option,value in opts:
		if option in ('-h',"--help"):
			PrintUsage()
			return 0
		elif option in ('-v'):
			PrintVersion()
			return 0
		elif option in ('-d'):
			ShortDebug = 1
		elif option in ('-D'):
			DetailDebug = 1
		elif option in ('-t'):
			Dst = value
		elif option in ('-p'):
			DstPort = value
		elif option in ('-l'):
			LogPath = value
		elif option in ('-f'):
			BatchPath = value
		elif option in ('-k'):
			Keypath = value
		else:
			p_usage()
			sys.exit()
	if len(args) == 3:
		Name = args[0]
		Type = args[2]
	elif len(args) == 2:
		Name = args[0]
		Type = args[1]
	elif len(args) <2:
		if BatchPath == "null":
			PrintUsage()
			return 0

	if BatchPath == "null":
		Proc(Name, Type, Dst, DstPort, KeyPath, DetailDebug,ShortDebug)
	else:
		ProcFile(BatchPath)


if __name__ == "__main__":
	main(sys.argv)

