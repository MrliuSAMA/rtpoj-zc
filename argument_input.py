import json

def Input():
	pass	
	
def input_iterms(items_key):
	total_items = {}
	input_values = []
	print "please input %s,An item with enterkey,End with char '$.$'" % items_key
	lastitem = 'null'
	while(lastitem != '$.$'):
		lastitem = raw_input("enter a %s :" % items_key)
		input_values.append(lastitem)
	else:
		print "checked end flag,input end"
	total_items[items_key] = input_values[:-1]
	return total_items
	
if __name__ == "__main__":
	cname = raw_input("please input country name:")

	serverip = input_iterms("ServerIP")
	domain  = input_iterms("Donains")
	pubpath  = input_iterms("Pubpath")
	merged_dict = dict(serverip,**dict(domain,**pubpath))
	
	jsonfile = open("./argument",'r+')
	jsonString = json.load(jsonfile)	#jsonString is a dict
	jsonString[cname] = merged_dict		#add an item to jsonString
	
	jsonfile.seek(0)
	json.dump(jsonString,jsonfile,indent = 4,sort_keys = True)
	#write and cover origin items
	jsonfile.close()
	print total_items












