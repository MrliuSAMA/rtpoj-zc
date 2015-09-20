import MySQLdb

def CreateConfigureFromDB():
	try:
		conn=MySQLdb.connect(   host='localhost',	\
								user='root',		\
								passwd='liu',		\
								db='configuration',		\
								port=3306)
		cur=conn.cursor()
		resnum = cur.execute('select * from zc_client')
		resinfo = cur.fetchmany(resnum)
		for everyitem in resinfo:
			print everyitem
		cur.close()
		conn.close()
	except MySQLdb.Error,e:
		print "Mysql Error %d: %s" % (e.args[0], e.args[1])
	return resinfo

def CreateConfigureFile(DBData,FileName = "ZCClient.in"):
	f = open("./%s" % FileName, 'w')
	for i in DBData:
		str = "%s\t%s\t%s\t%s\t%s\n" % (i[1],i[2],i[3],i[4],i[5])
		f.write(str)
	f.close()



if __name__ == "__main__":
	data = CreateConfigureFromDB()
	CreateConfigureFile(data)




