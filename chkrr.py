#!/usr/bin/env python
import getopt
import sys
import subprocess
import re

glo_dst = "127.0.0.1"

version = "0.1"

def p_usage():
	print "\n\t\tcheck rrsets tools:"+"(version)"+version+"\t\t\n"
	print "usage example:","chkrr -d xxx.xxx.xxx.xxx com. NS\n"
	print "usage: check [-hv] [-d query dst]\n"
	print "  -h/--help : print help usage"
	print "  -v : show version"
	print "  -d : query destination"

def p_version():
	print version

def find_rrset_query(list,query):
	res1 = re.search("RRset to chase",list[0])
	res2 = re.search(query,list[1])
	res3 = re.search("NS",list[1])
	if res1 != None and res2 != None and res3 != None:
		print "---->rrset get success"
def find_rrset_dnskey(list,query):
	res1 = re.search("DNSKEYset that signs the RRset",list[0])
	res2 = re.search(query,list[1])
	res3 = re.search("DNSKEY",list[1])
	if res1 != None and res2 != None and res3 != None:
		print "---->dnskey for rrsig get success"
def find_rrset_ds(list,query):
	res0 = re.search("Launch a query to find a RRset of type DS for zone: ."\
					,list[0])
	if res0 != None:
		print "---->reached top! root haven't DS"
		return 
	res1 = re.search("DSset of the DNSKEYset",list[0])
	res2 = re.search(query,list[1])
	res3 = re.search("DS",list[1])
	if res1 != None and res2 != None and res3 != None:
		print "---->ds for rrsig(dnskey) get success"
	
def find_rrsig_rrset(list,query):
	res1 = re.search("RRSIG of the RRset to chase",list[0])
	res2 = re.search(query,list[1])
	res3 = re.search("RRSIG",list[1])
	if res1 != None and res2 != None and res3 != None:
		print "---->rrsig for rrset get success"
def find_rrsig_dnskey(list,query):
	res1 = re.search("RRSIG of the DNSKEYset that signs the RRset to chase"\
					 ,list[0])
	res2 = re.search(query,list[1])
	res3 = re.search(r"RRSIG\tDNSKEY",list[1])
	if res1 != None and res2 != None and res3 != None:
		print "---->rrsig for dnskey get success"
def find_rrsig_ds():
	pass
def check(list,query):
	res0 = re.search("WE HAVE MATERIAL, WE NOW DO VALIDATION",list[0])
	if res0 != None:
		print "---->check start normal"
	else:
		print "---->check failed ! program will exit..."
		return
	str1 = "VERIFYING NS RRset for "+query
	res11 = re.search(str1, list[1])
	res12 = re.search("success",list[1])
	if res11 != None and res12 != None:
		print "---->check rrset by rrsig......yes"

	str2 = "OK We found DNSKEY \(or more\) to validate the RRset"
	res2 = re.search(str2, list[2])
	if res2 != None:
		print "---->KSK find"

	str31 = "Now, we are going to validate this DNSKEY by the DS"
	res311 = re.search(str31, list[3])
	if res311 != None:
		str41 = "the DNSKEY isn't trusted-key and there isn't DS"+\
				" to validate the DNSKEY"
		print str41
		res411 = re.search(str41, list[4])
		res412 = re.search("FAILED", list[4])
		if res411 != None and res412 != None:
			print "DNSSEC validation is NO"
			return
		str42 = "OK a DS valids a DNSKEY in the RRset"
		res421 = re.search(str42,list[4])
		if res421 != None:
			print "---->check ksk(by DS) yes"

	str32 = "Ok, find a Trusted Key in the DNSKEY RRset"
	res321 = re.search(str32, list[3])
	if res321 != None:
		str43 = "VERIFYING DNSKEY RRset for "+query
		res431 = re.search(str43, list[4])
		res432 = re.search("success", list[4])
		if res431 != None and res432 != None and query == ".":
			print "DNSSEC validation is yes"
			return

def proc(args):
	if len(args) == 3:
		name = args[0]
		types = args[2]
	if len(args) == 2:
		name = args[0]
		types = args[1]
	cmd = "dig @127.0.0.1 . NS +sigchase +trusted-key=/root/trusted-key.key"
	sub=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
	sub.wait()
	print type(sub)
	linelist = sub.stdout.readlines()
	print linelist	
	print "---------------->"
	split_list = modify_split(linelist)
	semantic_list = modify_semantic_split(split_list)
	find_rrset_query(semantic_list[0], '.')
	find_rrsig_rrset(semantic_list[1], '.')
	find_rrset_dnskey(semantic_list[2], '.')
	find_rrsig_dnskey(semantic_list[3], '.')
	find_rrset_ds(semantic_list[4],'.')
	check(semantic_list[5],'.')	



def modify_split(total):
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
#	for i in split_list:
#		print i


def modify_semantic_split(total):
	split_list = []
	for num in range(len(total)):
		res = len(total[num])
		if res == 1:
			continue
		if res > 1:
			split_list.append(total[num])
	for i in split_list:
		print i
	return split_list









def main(argv):
	try:
		opts,args = getopt.getopt(argv[1:], "hvd:", ["help"])
	except getopt.error,errinfo:
		if getopt.error.msg != "" or getopt.error.opt != "":
			print getopt.error.msg
			print getopt.error.opt
		print errinfo
		p_usage()
		sys.exit()
	for o,a in opts:
		if o in ('-h',"--help"):
			p_usage()
			return 0
		elif o in ('-d'):
			print a
			glo_dst = a
		elif o in ('-v'):
			p_version()
			return 0
		else:
			p_usage()
			sys.exit()
	proc(args)

	


















if __name__ == "__main__":
	main(sys.argv)

