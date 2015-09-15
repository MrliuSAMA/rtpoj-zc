import subprocess
import DebugInfo
import re
import os
import pprint

DBPath = "/var/namedFaker"
ConfigPath = "/etc"
BindIp = "173.26.101.233"
BindPort = "53"

def CreateOptions(FileName	= "./named.conf",\
				  MainDir	= "/var/namedFakier",\
				  ListenIp	= "",\
				 ListenPort	= ""):
	fp = open(FileName,'w+')
	fp.write("options {\n")
	fp.write("\tlisten-on port %s { 127.0.0.1;%s; };\n" % (ListenPort,ListenIp))
	fp.write("\tdirectory\t\t\t\"%s\";\n" % MainDir)
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

def File2GroupLists(FileName = "./config.in"):
	TLDList = []
	ListSplit = {}
	fp = open(FileName, 'r')
	RRLists = fp.readlines()
	for item in RRLists:
		TLD = item.strip().split()[0].split('.')[-2]
		if TLD == "":
			ListSplit.setdefault("root",[])
			ListSplit["root"].append(item)
		else:
			ListSplit.setdefault(TLD,[])
			ListSplit[TLD].append(item)
#	print DebugInfo.print_dict_valueIslist(ListSplit)
#	pprint.pprint(ListSplit)
	return ListSplit

def CreateCopyKeys(ListSplitDict):
	KeySplit = {}
	
	#---------->CreateKeys
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

	for keyitem in ListSplitDict.iterkeys():
		KeySplit.setdefault(keyitem,[])
		KeySplit[keyitem].append(re.sub(r"base",keyitem,resoutKSK[0]))
		KeySplit[keyitem].append(re.sub(r"base",keyitem,resoutZSK[0]))
#	pprint.pprint(KeySplit)

	#---------->Copykeys
	for keyitem in ListSplitDict.iterkeys():
		for postfix in (".key",".private"):
			for resout in (resoutKSK,resoutZSK):
				fileBase = resout[0]+postfix
				fileKeyitem = re.sub(r"base",keyitem,resout[0])+postfix
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
				
	return KeySplit

def CreateDBFile(GroupDict,KeyDict):
	#------->ADD DNSRR RECORD & KSK ZSK
	for keyname in GroupDict.iterkeys():
		zone = keyname
		if keyname == "root":
			zone = ""
		fp = open("./%s.db" % keyname,"w+")
		fp.write("$ORIGIN .\n")
		fp.write("$TTL 86400\n\n")
		fp.write("%s. IN SOA %s. %s. (86400 2m 2m 2m 2m)\n" %(zone,zone,zone))
		if keyname == "root":
			for key in GroupDict.iterkeys():
				for i in GroupDict[key]:
					fp.write(i)
			fp.write("\n\n")
		else:
			for i in GroupDict[keyname]:
				fp.write(i)
			fp.write("\n\n")
		for j in KeyDict[keyname]:
			fp.write("$INCLUDE \"%s.key\"\n" % j)
		fp.close()
#	#------->Add DS RECORD
#	fp = open("./root.db",'a+')
#	for keyname in GroupDict.iterkeys():
#		if keyname == "root":
#			continue
#		else:
#			fp.write("$INCLUDE \"dsset-%s.\"\n" % keyname)
#	fp.close()

	#------->SIGN ZONE(root zone must be the last to sign!)
	for keyname in GroupDict.iterkeys():
		cmd = "dnssec-signzone -o %s. %s.db" % (keyname,keyname)
		sub = subprocess.Popen(cmd, shell=True)
		sub.wait()

def MoveFile(DBpath):
	cmd = "mv *.key *.private *.db *.signed *. %s" % DBpath
	sub = subprocess.Popen(cmd, shell=True)
	sub.wait()
	cmd = "mv -b *.conf %s" % ConfigPath
	sub = subprocess.Popen(cmd, shell=True)
	sub.wait()

def CreateMultiZone(GroupDict):
	for name in GroupDict.iterkeys():
		zone = name
		if zone == "root":
			zone = ""
		CreateZone("%s." % zone, "%s.db.signed" % name)

def ExportTrustedKey(DBpath,Keydict):
	keyName = KeyDict.keys()[0]
	keyFileName = Keydict[keyName][0]
	fpr = open("%s/%s.key" % (DBpath, keyFileName),'r')
	linelist = fpr.readlines()
	fpw = open("%s/trusted-key.key" % DBpath, 'w')
	fpw.write(linelist[-1])
	fpr.close()
	fpw.close()

def init(Path):
	res = os.path.exists(Path)
	if res == True:
		pass
	else:
		cmd = "mkdir %s" % Path
		sub = subprocess.Popen(cmd, shell=True)
		sub.wait()





if __name__ == "__main__":
	init(DBPath)

	GroupDict = File2GroupLists()
	CreateOptions(MainDir = DBPath, ListenIp = BindIp,ListenPort = BindPort)
	CreateLogging()
	CreateMultiZone(GroupDict)

	KeyDict = CreateCopyKeys(GroupDict)
	CreateDBFile(GroupDict,KeyDict)

	MoveFile(DBPath)
	ExportTrustedKey(DBPath,KeyDict)














