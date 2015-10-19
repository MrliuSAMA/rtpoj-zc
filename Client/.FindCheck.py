#coding=utf-8
"""
findAndcheck 模块
收集用于验证DNS应答包的条目
使用这些条目按照DNSSSEC的逻辑进行验证
"""
import re


def find_rrset_query(list,name_zone):
	res1 = re.search("RRset to chase",list[0])
	res2 = re.search(name_zone,list[1])
	if res1 != None and res2 != None:
		print "---->rrset get success"

	result = []
	for i in list[1:]:
		result.append(i.split()[4])
	return result



def find_rrset_dnskey(list,name_zone):
	res1 = re.search("DNSKEYset that signs the RRset",list[0])
	res2 = re.search(name_zone,list[1])
	res3 = re.search("DNSKEY",list[1])
	if res1 != None and res2 != None and res3 != None:
		print "---->dnskey for rrsig get success"



def find_rrset_ds(list,name_zone):
	res0 = re.search("Launch a query to find a RRset of type DS for zone: ."\
					,list[0])
	if res0 != None:
		print "---->reached top! root haven't DS"
		return -1
	res1 = re.search("DSset of the DNSKEYset",list[0])
	res2 = re.search(name_zone,list[1])
	res3 = re.search("DS",list[1])
	if res1 != None and res2 != None and res3 != None:
		print "---->ds for rrsig(dnskey) get success"
		return 0



def find_rrsig_rrset(list,name_zone):
	res1 = re.search("RRSIG of the RRset to chase",list[0])
	res2 = re.search(name_zone,list[1])
	res3 = re.search("RRSIG",list[1])
	if res1 != None and res2 != None and res3 != None:
		print "---->rrsig for rrset get success"



def find_rrsig_dnskey(list,name_zone):
	res1 = re.search("RRSIG of the DNSKEYset that signs the RRset to chase"\
					 ,list[0])
	res2 = re.search(name_zone,list[1])
	res3 = re.search(r"RRSIG\tDNSKEY",list[1])
	if res1 != None and res2 != None and res3 != None:
		print "---->rrsig for dnskey get success"



def find_rrsig_ds(list,name_zone):
	res1 = re.search("RRSIG of the DSset of the DNSKEYset",list[0])
	res2 = re.search(name_zone,list[1])
	res3 = re.search(r"RRSIG\tDS",list[1])
	if res1 != None and res2 != None and res3 != None:
		print "---->rrsig for DS get success"



def check(list,name,namezone,types,recursive_flag):
	res0 = re.search("WE HAVE MATERIAL, WE NOW DO VALIDATION",list[0])
	if res0 != None:
		print "check start normal"
	else:
		print "check failed (0) program will exit..."
		return

	str1 = "VERIFYING %s RRset for %s" % (types,name)
	res11 = re.search(str1, list[1])
	res12 = re.search("success",list[1])
	res13 = re.search("expired",list[1])
	if res11 != None and res12 != None:
		print "---->check %s-rrset by rrsig......yes" % types
	if res11 != None and res13 != None:
		print "---->check rrset by rrsig......NO(expired)"
		add_result(list)
		return

	str2 = "OK We found DNSKEY \(or more\) to validate the RRset"
	res2 = re.search(str2, list[2])
	if res2 != None:
		print "---->ksk find"
	
	str31 = "Now, we are going to validate this DNSKEY by the DS"
	res311 = re.search(str31, list[3])
	if res311 != None:
		print "there isn't trustkey we want find ds"
		str41 = "the DNSKEY isn't trusted-key and there isn't DS"+\
				" to validate the DNSKEY"
		res411 = re.search(str41, list[4])
		res412 = re.search("FAILED", list[4])
		if res411 != None and res412 != None:
			print "No ds!!! DNSSEC validation is......failed"
			return
		str42 = "OK a DS valids a DNSKEY in the RRset"
		res421 = re.search(str42,list[4])
		if res421 != None:
			print "---->check ksk(by DS)......yes"
		
		str51 = "Now verify that this DNSKEY validates the DNSKEY RRset"
		res51 = re.search(str51,list[5])
		if res51 != None:
			print "check zsk start"
		else:
			print "checking zsk[quit]"
			return
		
		str61 = "VERIFYING DNSKEY RRset for %s with DNSKEY" % namezone
		res61 = re.search(str61,list[6])
		res62 = re.search("success",list[6])
		if res61 != None and res62 != None:
			print "---->check zsk(by ksk)......yes"
		else:
			print "---->check zsk,failed"
			return
		
		str81 = "Now, we want to validate the DS"
		str82 = "recursive call"
		res81 = re.search(str81,list[8])
		res82 = re.search(str82,list[8])
		if res81 != None and res82 != None:
			print "check current data......yse;start recursive check"
			return

	str32 = "Ok, find a Trusted Key in the DNSKEY RRset"
	res321 = re.search(str32, list[3])
	if res321 != None:
		str43 = "VERIFYING DNSKEY RRset for "+namezone
		res431 = re.search(str43, list[4])
		res432 = re.search("success", list[4])
		if res431 != None and res432 != None:
			print "DNSSEC validation is yes"
			return

