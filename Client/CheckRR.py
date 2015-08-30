#!/usr/bin/env python
import getopt
import sys
import subprocess
import DebugInfo
import FindCheck

debug = 0
version = "0.1"

def p_usage():
	print "\n\n\t\tCheck RRsets Tools"+"[version %s]\t\t\n" % version 
	print "usage: chkrr\t[-v version][-t=dst_ip query target][-h help manual]"
	print "\t\t[-D debug info][-d short debug info][-l log record]"
	print "\t\t[-f=file_path filemode]"
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
	


def p_version():
	print version


def add_result(list):
	res1 = re.search("SUCCESS", list[-1])
	if res1 != None:
		print "DNSSEC validation SUCCESS"
		return 0
	res2 = re.search("FAILED", list[-1])
	if res2 != None:
		print "DNSSEC validation FAILED"
		return -1


def split2block(total):
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


def cut_oneline(total):
	split_list = []
	for num in range(len(total)):
		res = len(total[num])
		if res == 1:
			continue
		if res > 1:
			split_list.append(total[num])
	return split_list


#run a proc means a fetch and a total verify for one DNS query 
def proc(name, types, dst, keypath):
	cmd = "dig @%s %s %s +sigchase +trusted-key=%s" % (dst,name,types,keypath)
	if debug:	
		print cmd
	sub=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
	sub.wait()
	linelist = sub.stdout.readlines()
	blocks = split2block(linelist)
	semantic_list = cut_oneline(blocks)
	
	if debug:
		DebugInfo.print_list(semantic_list)
	
	recursive = 0
	cur_number = 0
	response,cur_number,verify_result = find_And_check(name, types, semantic_list, cur_number, recursive)
	recursive = recursive+1
	if name != ".":				#dot means we don't need a recursive verify
		if recursive != 0:		#recursive verify start with DS record
			find_And_check(".","DS",semantic_list,cur_number,recursive)
	return response,verify_result


#run a find_And_check means a partical verify for a DNS query
def find_And_check(name, types, semantic_list, start_seqno, recursive_flag):
	seq = start_seqno
	end_seqno = 0
	name_zone = name.split('.')[-2]+'.'
	result = []
	if recursive_flag == 0:
		result = FindCheck.find_rrset_query(semantic_list[seq], name_zone)
		seq = seq+1
		FindCheck.find_rrsig_rrset(semantic_list[seq], name_zone)
		seq = seq+1
	FindCheck.find_rrset_dnskey(semantic_list[seq], name_zone)
	seq = seq+1
	FindCheck.find_rrsig_dnskey(semantic_list[seq], name_zone)
	seq = seq+1
	rcode = FindCheck.find_rrset_ds(semantic_list[seq],name_zone)
	seq = seq+1
	if rcode == 0:
		FindCheck.find_rrsig_ds(semantic_list[seq],name_zone)
		seq = seq+1
		FindCheck.check(semantic_list[seq],name,name_zone,types,recursive_flag)
		seq = seq+1
	if rcode == -1:
		FindCheck.check(semantic_list[seq],name,name_zone,types,recursive_flag)
		seq = seq+1
	end_seqno = seq

	if recursive_flag == 0:
		DebugInfo.print_result(name, types, result)

	return result,end_seqno,0


def proc_file(filepath):
	file = open(filepath, 'r')
	outputfile = filepath.strip().split('/')[-1].split('.')[-2]+".out"
	file_res = open(outputfile, 'w')
	querys = file.readlines()
	res = []
	for oneline in querys:
		cmd = oneline.strip().split()
		res,status = proc(cmd[0],cmd[1],cmd[2],cmd[3])
		if status == 0:
			status = "verify_OK"
		else:
			status = "verify_NO"			
		for every_answer in res:
			file_res.write("%s\t%s\t%s\t%s\t%s\n" % (cmd[0],cmd[1],cmd[2],every_answer,status))
#		file_res.close()
#		file_res = open(outputfile, 'a')
	for every_answer in res:
		res_A,status_A = proc(every_answer,'A',cmd[2],cmd[3])
		if status_A == 0:
			status_A = "verify_OK"
		else:
			status_A = "verify_NO"
		for items in res_A:
			file_res.write("%s\t%s\t%s\t%s\t%s\n" % (every_answer,'A',cmd[2],items,status_A))

	file.close()
	file_res.close()



def main(argv):
	noglo_dst	= "127.0.0.1"
	name		= "null"
	types		= "null"
	filepath	= "./queryfile.in"
	try:
		opts,args = getopt.getopt(argv[1:], "hvd:f:", ["help"])
	except getopt.GetoptError,info:
		print info.msg
		p_usage()
		sys.exit()
	for o,a in opts:
		if o in ('-h',"--help"):
			p_usage()
			return 0
		elif o in ('-d'):
			noglo_dst = a
		elif o in ('-v'):
			p_version()
			return 0
		elif f in ('-f'):
			filepath = a
		else:
			p_usage()
			sys.exit()
	if len(args) == 3:
		name = args[0]
		types = args[2]
	if len(args) == 2:
		name = args[0]
		types = args[1]

	if filepath == "null":
		proc(name, types, noglo_dst, keypath)
	else:
		proc_file(filepath)



if __name__ == "__main__":
	main(sys.argv)

