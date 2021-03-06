#coding=utf-8
import pprint
import subprocess
import re
import os
import logging
import socket
import fcntl
import struct
import getopt
import sys


#file path configure
DBPath = "/var/named/exchange-data"
ConfigurePath = "/etc"

#input&output
DataFile = "./ZoneExchangeData.in"

#option configure
BindIp = "127.0.0.1"
BindPort = "53"
ZoneName = "dummy"

#virtual info config [if no special ,pls don't change configure below]
VirtualIp = "1.1.1.1"
VirtualName = "a.virtual"

#####
PREFIX = "/opt/RootZoneExchangeServer/"


#	使输入的数据符合BIND的发布逻辑，虚拟一些顶级域节点，虚拟的顶级域节点IP地址可以任意填写，
#	因为发布该数据的服务器同时负责根节点和顶级域节点。对内十负责多个区的权威服务器，
#	对外可看做一台递归服务器。
def AddVirtualTld2File(FileName = DataFile):
	TLDList = []
	ReturnTLD = [".",]
	# initial TLD
	fp = open(FileName, 'r')
	RRLists = fp.readlines()
	for item in RRLists:
		TLD = item.strip().split()[0].split('.')[-2]
		if ReturnTLD == "":
			ReturnTLD.append(".")
		else:
			ReturnTLD.append(TLD.lower())
		if TLD=="":
			pass
		else:
			TLDList.append(TLD.lower())
	fp.close()
#	logging.debug(pprint.pprint(TLDList))

	#复制一个新的临时文件，新的文件添加上用于辅助BIND逻辑的虚拟节点信息
	templist = FileName.split('.')
	templist.append("temp")
	NewFileName = '.'.join(templist)
	global DataFile
	DataFile = NewFileName
	cmd = "cp %s %s" % (FileName, NewFileName)
	sub = subprocess.Popen(cmd, shell=True)
	sub.wait()	

	#添加额外的虚拟顶级域节点信息
	fp = open(NewFileName, 'a')
	TLDNoRedundancy = [i for i in set(TLDList)]
	for TLDName in TLDNoRedundancy:
		str1 = "%s.\t\t\t172800\tIN\tNS\t%s.%s.\n" % (TLDName,VirtualName,TLDName)
		str2 = "%s.%s.\t172800\tIN\tA\t%s\n" % (VirtualName,TLDName,VirtualIp)
		fp.write(str1)
		fp.write(str2)
	
	#添加额外的虚拟跟区节点信息
	fp.write(".\t\t\t172800\tIN\tNS\ta.virtual.\n")
	fp.write("a.virtual.\t172800\tIN\tA\t1.1.1.1\n")
	fp.close()
#	logging.debug(pprint.pprint(ReturnTLD))
	return [i for i in set(ReturnTLD)]



#	生成BIND配置文件中的option选项
def CreateOptions(ConfigureFileName	= "./named.conf",	\
				  DataFileDir	= "dummy",	\
				  BindIp	= "dummy",		\
				  BindPort	= "dummy"):
	fp = open(ConfigureFileName,'w+')
	fp.write("options {\n")
	fp.write("\tlisten-on port %s { 127.0.0.1;%s; };\n" % (BindPort,BindIp))
	fp.write("\tdirectory\t\t\t\"%s\";\n" % DataFileDir)
	fp.write("\tdump-file\t\t\t\"data/cache_dump.db\";\n")
	fp.write("\tstatistics-file\t\t\t\"data/named_stats.txt\";\n")
	fp.write("\tmemstatistics-file\t\t\"data/named_mem_stats.txt\";\n")
	fp.write("\tallow-query	{ any; };\n")
	fp.write("\trecursion no;\n")
	fp.write("\tdnssec-enable yes;\n")
	fp.write("};\n\n")
	fp.close()


#	生成BIND配置文件中的loging选项
def CreateLogging(FileName  = "./named.conf"):
	fp = open(FileName,'a+')
	fp.write("logging {\n")
	fp.write("\tchannel default_debug {\n")
	fp.write("\t\tfile \"data/named.run\";\n")
	fp.write("\t\tseverity dynamic;\n")
	fp.write("\t\t};\n};\n\n")
	fp.close()


#	生成BIND配置文件中的Zone选项
def CreateZone(ZoneName,ZonePath,FileName = "./named.conf"):
	fp = open(FileName,'a+')
	fp.write("zone \"%s\" IN {\n\ttype master;\n\tfile \"%s\";\n};\n\n" %\
			(ZoneName,ZonePath))
	fp.close()


def CreateMultiZone(TLDList):
	for name in TLDList:
		zone = name
		if zone == ".":
			zone = ""
			name = "root"
		CreateZone("%s." % zone, "%s.db.signed" % name)


#	将文件移动到目录所指定的位置
def MoveFile(DBPath = "/var/named/exchange-data", ConfigurePath = "/etc"):
	cmd = "sudo mv -b *.conf %s" % ConfigurePath
	sub = subprocess.Popen(cmd, shell=True)
	sub.wait()




def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])



def init(tempDataFile,tempBindIp,tempBindPort):
	global DBPath
	global ConfigurePath
	global DataFile
	global BindIp
	global BindPort
	global ZoneName
	global VirtualIp
	global VirtualName
	
	#init local ip
	BindIp = get_ip_address("eth0")

	#read parameter
	if tempDataFile != "dummy":
		if tempBindIp != "dummy":
			BindIp = tempBindIp
		if tempBindPort != "dummy":
			BindPort = tempBindPort
		DataFile = tempDataFile
	else:
		f = open("%sConfiguration.in" % PREFIX,'r')
		filelines = f.readlines()
		BindIp = filelines[0].strip().split()[-1]
		BindPort = filelines[1].strip().split()[-1]
		DBPath	= filelines[2].strip().split()[-1]
		ConfigurePath = filelines[3].strip().split()[-1]
		DataFile = filelines[4].strip().split()[-1]
		VirtualIp = filelines[5].strip().split()[-1]
		VirtualName = filelines[6].strip().split()[-1]
		f.close()
		
	#init zonename
	f = open(DataFile,'r')
	lines = f.readlines()
	for i in lines:
		if i.strip().split()[3] == 'NS':
			ZoneName = i.strip().split()[0].split('.')[-2]
			break

	#init Folder
	if os.path.exists(DBPath) == False:
		os.makedirs(DBPath)

	#init logging mode
	logging.basicConfig(level = logging.DEBUG,\
					format = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',\
					datefmt = '%a, %d %m %Y %H:%M:%S',\
					filename = "./run.log",	\
					filemode = 'a')
	logging.info("############################ A New restart ############################")
	
	

if __name__ == "__main__":
	tempBindIp = "dummy"
	tempBindPort = "dummy"
	tempDataFile = "dummy"
	
	try:
		opts,args = getopt.getopt(sys.argv[1:], "s:p:f:")
#		print opts
#		print args
	except getopt.GetoptError,info:
#		print info.msg 
		sys.exit()
	for option,value in opts:
		if option in ('-s'):
			tempBindIp = value
		elif option in ('-p'):
			tempBindPort = value
		elif option in ('-f'):
			tempDataFile = value
		else:
			pass

  	
	init(tempDataFile,tempBindIp,tempBindPort)
	TLDList = AddVirtualTld2File(DataFile)
#	DataFileName = CreateZoneFile(TLDList,DataFile)
#	KeyDict = KeyGenerate(TLDList)
#	SignDBfile(KeyDict)

	CreateOptions(DataFileDir = DBPath, BindIp = BindIp, BindPort = BindPort)
	CreateLogging()
	CreateMultiZone(TLDList)
	MoveFile(DBPath = DBPath,ConfigurePath = ConfigurePath)
#	ExportTrustedKey(KeyDict,DBfilepath = DBPath)
	



