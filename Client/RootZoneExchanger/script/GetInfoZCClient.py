#!/usr/bin/python
from __future__ import print_function
import re
import subprocess
import os

ControlPREFIX = "/opt/RootZoneExchange/RootZoneExchanger/"
DataPREFIX = "/opt/RootZoneExchange/RootZoneExchanged/Data/ZoneExchangeBak"
FinalData = "/opt/RootZoneExchange/RootZoneExchanged/Data/ZoneExchange/root.zone.exchangedata"
def ReturnConfig(ControlPREFIX,DataPREFIX,FileName = "Configuration.in"):

	#print configures
	f = open(ControlPREFIX+FileName, 'r')
	fileContent = f.read()	
	match = re.search(r"Period\s*=\s*[0-9]*",fileContent)
	print ("period="+match.group().split()[-1]+',',end="\n")
	matchPrefix = re.search(r"Prefix\s*=\s*[a-zA-Z/\.]*",fileContent)
	matchCurFilePath = re.search(r"CurFilePath\s*=\s*[a-zA-Z/\.]*",fileContent)
	matchBackupFilePath = re.search(r"BackupFilePath\s*=\s*[a-zA-Z/\.]*",fileContent)
	matchFinalFile = re.search(r"OutputName\s*=\s*[a-zA-Z/\.]*",fileContent)
	datapath = matchPrefix.group().split()[-1]+'/'+matchBackupFilePath.group().split()[-1]
	print ("DataPath="+datapath+'/'+',', end="\n")
	finalfile = datapath+matchFinalFile.group().split()[-1]
	print ("outputfile="+finalfile+',', end="\n")
	f.close()

	#print files
	cur_path = os.getcwd()
	compare_path = DataPREFIX
	os.chdir(compare_path)

	files= os.listdir(compare_path)
	zone_files = [x for x in files if x.endswith("out")]
	zone_files.sort(cmp = compare_time, reverse = True)

	num_counter = 0
	while(num_counter < min(3,len(zone_files))):
		print (zone_files[num_counter]+',', end="\n")
		num_counter = num_counter + 1
	os.chdir(cur_path)
	##sub1 = subprocess.Popen("ls -lt -d %s*.out | wc -l" % DataPREFIX, stdout=subprocess.PIPE, shell=True)
	##print ("filesnumber="+sub1.stdout.readlines()[0].strip()+',',end="\n")
	##sub1.wait()
	##
	##temp3filename = []
	##sub0 = subprocess.Popen("ls -lt -d %s*.out | head -n 10" % DataPREFIX, stdout=subprocess.PIPE, shell=True)
	##sub0.wait()
	##reslines = sub0.stdout.readlines()
	##
	##itemnum = len(reslines)
###	print (itemnum)
##
	##if itemnum > 0 and itemnum < 2:
		##temp3filename.append(reslines[0].split()[-1].split('/')[-1])
	##elif itemnum > 0 and itemnum < 3:
		##temp3filename.append(reslines[0].split()[-1].split('/')[-1])	 
		##temp3filename.append(reslines[1].split()[-1].split('/')[-1])
	##elif itemnum > 3:
		##temp3filename.append(reslines[0].split()[-1].split('/')[-1])	 
		##temp3filename.append(reslines[1].split()[-1].split('/')[-1])	
		##temp3filename.append(reslines[2].split()[-1].split('/')[-1])
	##else:
		##print ("no files")
##
	##for i in temp3filename:
		##print (i+',')

	#print countrys
	itemnum = len(zone_files)
	temp3filename = zone_files[-min(3,len(zone_files)):]
	if itemnum > 3:
		itemnum = 3 
	for i in range(itemnum):
		f = open(ControlPREFIX+"Query.in",'r')
		filelines = f.readlines()
		total_country = 0
		for line in filelines:
			if line.strip().split()[-1] == "1":
				total_country = total_country + 1
		total_country = "TotalCountrys=%s" % total_country
		print (total_country+',', end="")
		templist = []
		for line in filelines:
			if line.strip().split()[-1] == "1":			
				templist.append(line.split()[0])
		print ('|'.join(templist),end=",")
#			print (line.split()[0]+'|', end="")
		f.close()

		cur_country = 0
		cur_country_list = []
		templist_ = []
		f = open(DataPREFIX+'/'+temp3filename[i],'r')
		filelines = f.readlines()
		for line in filelines:
			if line.split()[3] == "DS" and line.split()[0] not in templist_:
				templist_.append(line.split()[0])
				cur_country = cur_country+1
				cur_country_list.append(line.split()[0])
		cur_country = "CurCountrys=%s" % str(cur_country)
#

		print (cur_country+',', end="")
#		templist = []
		if len(templist) == 0:
			print ("", end="\n")
		else:
			print (cur_country_list)
			for i in cur_country_list:
				templist.append(i)
				print ('|'.join(templist)+',', end="\n")
		f.close()

	#print pid
	cmd = 'ps -ef | grep "python %sExchangeClient"'%ControlPREFIX
	sub = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	sub.wait()
	reslines = sub.stdout.readlines()
	judgeifrun = 0
	for lines in reslines:
		if lines.split()[2] == '1':
			print ("pid=%s," % lines.split()[1])
			judgeifrun = 1
			break
	if judgeifrun == 0:
		print ("pid=0,")	


def compare_time(file_x, file_y):
	#internal called function
	stat_x = os.stat(file_x)
	stat_y = os.stat(file_y)
	if stat_x.st_mtime < stat_y.st_mtime:
		return -1
	elif stat_x.st_mtime > stat_y.st_mtime:
		return 1
	else:
		return 0



if __name__ == "__main__":
	ReturnConfig(ControlPREFIX,DataPREFIX)
