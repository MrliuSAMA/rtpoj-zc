import json

def Convert(inputFileName, outputFileName):
	srcfp = open(inputFileName,'r')
	dstfp = open(outputFileName,'w')
	json_string = json.load(srcfp)
	for keyvalue in json_string.keys():
		domain = json_string[keyvalue]["Domains"]
		pubpath = json_string[keyvalue]["Pubpath"]
		serverip = json_string[keyvalue]["ServerIP"]
		for domain_item in domain:
			for ip_item in serverip:
				dstfp.write("%s\t%s\t%s\t%s\n" % (domain_item,"NS",ip_item,pubpath[0]))
	srcfp.close()
	dstfp.close()

if __name__ == "__main__":
	Convert("./argument","./queryfile")


