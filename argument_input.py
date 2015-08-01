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
	total_items = {}
	country_content = []

	serverip = input_iterms("ServerIP")
	domain  = input_iterms("Donains")
	pubpath  = input_iterms("Pubpath")
	country_content.extend([serverip,domain,pubpath])
	total_items[cname] = country_content
	
	encodedjson = json.dumps(total_items)
	print country_content
	print total_items
	print "-------->"
	print encodedjson












