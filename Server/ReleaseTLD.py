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
DataFile = "./DataOrigin.in"

#option configure
BindIp = "127.0.0.1"
BindPort = "53"
ZoneName = "dummy"

#virtual info config [if no special ,pls don't change configure below]
VirtualIp = "1.1.1.1"
VirtualName = "a.virtual"


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
	logging.debug(pprint.pprint(TLDList))

	fp = open(FileName, 'a')
	TLDNoRedundancy = [i for i in set(TLDList)]
	for TLDName in TLDNoRedundancy:
		str1 = "%s.\t\t\t172800\tIN\tNS\t%s.%s.\n" % (TLDName,VirtualName,TLDName)
		str2 = "%s.%s.\t172800\tIN\tA\t%s\n" % (VirtualName,TLDName,VirtualIp)
		fp.write(str1)
		fp.write(str2)	
	#ADD root
	fp.write(".\t\t\t172800\tIN\tNS\ta.virtual.\n")
	fp.write("a.virtual.\t172800\tIN\tA\t1.1.1.1\n")
	fp.close()
	logging.debug(pprint.pprint(ReturnTLD))
	return [i for i in set(ReturnTLD)]


def CreateZoneFile(TLDList,FileName = DataFile):
	logging.debug(pprint.pprint(TLDList))
	DividedItem = {}
	fp = open(DataFile)
	Lines = fp.readlines()
	for j in Lines:			
		if j.strip().split()[3] == "DS":
			DividedItem.setdefault(".",[])
			DividedItem["."].append(j)
			continue
 				
		if "virtual" in j.strip().split()[0]:
			DividedItem.setdefault(".",[])
			DividedItem["."].append(j)
		elif "virtual" in j.strip().split()[-1]:
			DividedItem.setdefault(".",[])
			DividedItem["."].append(j)
		else:
			pass
		
		tld = j.strip().split()[0].split('.')[-2]
		judge = j.strip().split()[0]+j.strip().split()[-1]					 
		if tld in TLDList and tld == ZoneName and "virtual" not in judge:
			DividedItem.setdefault(tld,[])
			DividedItem[tld].append(j)
		elif tld in TLDList and tld != ZoneName:
			DividedItem.setdefault(tld,[])
			DividedItem[tld].append(j)
		else:
			pass

	fp.close()		
	logging.debug(pprint.pprint(DividedItem))
				
	DataFileName = []
	name = "dummy"
	SOA4 = "dummy"
	for i in TLDList:
		if i == ".":
			name = "root"
		else:
			name = i

		for j in DividedItem[i]:
			if j.strip().split()[3] == "NS":
				SOA4 = j.strip().split()[4]
				break

		DataFileName.append("./%s.db" % name)

		fp = open("./%s.db" %name, 'w')
		fp.write("$ORIGIN .\n")
		fp.write("$TTL 86400\n\n")
		if name == "root":
			fp.write("%s. IN SOA %s %s (86400 2m 2m 2m 2m)\n" %("",SOA4,SOA4))
		else:
			fp.write("%s. IN SOA %s %s (86400 2m 2m 2m 2m)\n" %(name,SOA4,SOA4))
		fp.writelines(DividedItem[i])
		fp.close()

	
	return DataFileName



def KeyGenerate(TLDList):		
	KeySplit = {}
#---------------->CreateKeys
	cmd = "dnssec-keygen -f KSK -a RSASHA1 -b 512 -n ZONE base." 
	subKSK = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
	subKSK.wait()
	contentKSK = subKSK.stdout.read()
	resoutKSK = re.findall(r"K\w*\.\+\d*\+\d*",contentKSK,re.MULTILINE)
#	pprint.pprint(resoutKSK)

	cmd = "dnssec-keygen -a RSASHA1 -b 512 -n ZONE base." 
	subZSK = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
	subZSK.wait()
	contentZSK = subZSK.stdout.read()
	resoutZSK = re.findall(r"K\w*\.\+\d*\+\d*",contentZSK,re.MULTILINE)
#	pprint.pprint(resoutZSK)

	for keyitem in TLDList:
		if keyitem == '.':
			keyitem = ''
		Keyitemdot = keyitem+'.'
		KeySplit.setdefault(Keyitemdot,[])
		KeySplit[Keyitemdot].append(re.sub(r"base",keyitem,resoutKSK[0]))
		KeySplit[Keyitemdot].append(re.sub(r"base",keyitem,resoutZSK[0]))
#	pprint.pprint(KeySplit)

#--------------->Copykeys
	for keyitem in TLDList:
		if keyitem == '.':
			keyitem = ''
		for postfix in (".key",".private"):
			for resout in (resoutKSK,resoutZSK):
				fileBase = resout[0]+postfix
				fileKeyitem = re.sub(r"base",keyitem,resout[0])+postfix
				print fileKeyitem
				cmdstr = "cp ./%s ./%s" % (fileBase,fileKeyitem)
				sub = subprocess.Popen(cmdstr, shell=True)
				sub.wait()

				if postfix == ".key":
					f = open(fileKeyitem,'r')
					seqlist = f.readlines()
					f.close()
					seqlist[0] = re.sub(r"base",keyitem,seqlist[0])
					seqlist[-1] = re.sub(r"base",keyitem,seqlist[-1])
					f = open(fileKeyitem,'w')
					f.writelines(seqlist)
					f.close()
#				print fileBase
#				print fileKeyitem
	cmdDelete = "rm ./Kbase.*"
	sub = subprocess.Popen(cmdDelete, shell = True)
	sub.wait()
				
	pprint.pprint(KeySplit)
	return KeySplit		
			
def SignDBfile(KeyDict):
	filename = "dummy"
	for i in KeyDict.iterkeys():
		if i == ".":
			filename = "root.db"
		else:
			filename = i+"db"
		fp = open("./%s" % filename, 'a')
		fp.write("\n\n")
		fp.write("$INCLUDE "+KeyDict[i][0]+'.key'+'\n')
		fp.write("$INCLUDE "+KeyDict[i][1]+'.key'+'\n')
		fp.write('\n')
		fp.close()

	for i in KeyDict.iterkeys():
		if i == ".":
			filename = "root.db"
		else:
			filename = i+"db"
		cmd = "dnssec-signzone -o %s %s" % (i,filename)
		sub = subprocess.Popen(cmd, shell=True)
		sub.wait()	

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

def CreateLogging(FileName  = "./named.conf"):
	fp = open(FileName,'a+')
	fp.write("logging {\n")
	fp.write("\tchannel default_debug {\n")
	fp.write("\t\tfile \"data/named.run\";\n")
	fp.write("\t\tseverity dynamic;\n")
	fp.write("\t\t};\n};\n\n")
	fp.close()

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


def MoveFile(DBPath = "/var/namedFaker", ConfigurePath = "/etc"):
	cmd = "mv *.key *.private *.db *.signed *. %s" % DBPath
	sub = subprocess.Popen(cmd, shell=True)
	sub.wait()
	cmd = "mv -b *.conf %s" % ConfigurePath
	sub = subprocess.Popen(cmd, shell=True)
	sub.wait()

def ExportTrustedKey(Keydict, DBfilepath = DBPath):
#	keyName = KeyDict.keys()[0]
	keyName = ZoneName+'.'
	keyFileName = Keydict[keyName][0]
	fpr = open("%s/%s.key" % (DBfilepath, keyFileName),'r')
	linelist = fpr.readlines()
	fpw = open("./trusted-key.key", 'w')
	fpw.write(linelist[-1])
	fpr.close()
	fpw.close()

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def init(tempDataFile,tempBindIp,tempBindPort):
	#read parameter
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

	if tempDataFile != "dummy":
#		f = open("./Configuration.in",'r')
#		filelines = f.readlines()
#		BindIp = filelines[0].strip().split()[-1]
		if tempBindIp != "dummy":
			BindIp = tempBindIp
#		BindPort = filelines[1].strip().split()[-1]
		if tempBindPort != "dummy":
			BindPort = tempBindPort
#	#	ZoneName = filelines[2].strip().split()[-1]
#		DBPath	= filelines[2].strip().split()[-1]
#		ConfigurePath = filelines[3].strip().split()[-1]
#		DataFile = filelines[4].strip().split()[-1]
		DataFile = tempDataFile
#		VirtualIp = filelines[5].strip().split()[-1]
#		VirtualName = filelines[6].strip().split()[-1]
#		f.close()
	else:
		f = open("./Configuration.in",'r')
		filelines = f.readlines()
		BindIp = filelines[0].strip().split()[-1]
		BindPort = filelines[1].strip().split()[-1]
	#	ZoneName = filelines[2].strip().split()[-1]
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

#	print DBPath
#	print ConfigurePath
#	print DataFile
#	print BindIp
#	print BindPort
#	print ZoneName
#	print VirtualIp
#	print VirtualName


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
		print opts
		print args
	except getopt.GetoptError,info:
		print info.msg 
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
	DataFileName = CreateZoneFile(TLDList,DataFile)
	KeyDict = KeyGenerate(TLDList)
	SignDBfile(KeyDict)

	CreateOptions(DataFileDir = DBPath, BindIp = BindIp, BindPort = BindPort)
	CreateLogging()
	CreateMultiZone(TLDList)
	MoveFile(DBPath = DBPath,ConfigurePath = ConfigurePath)
	ExportTrustedKey(KeyDict,DBfilepath = DBPath)
	



