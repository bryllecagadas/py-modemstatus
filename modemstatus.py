#!/usr/bin/env python3
import getopt, sys
import threading
from  modemcurl import *

def start_pldt():
	pldt = PLDTiGateway('http://192.168.1.1/')
	pldt.get_status()

def start_globe():
	globe = GlobeAztech('http://192.168.254.254/')
	globe.get_status()

def start_tplink():
	tplink = TPLinkR470("http://192.168.0.1/")
	tplink.get_status()

def start_dhcp():
	tplink = TPLinkR470("http://192.168.0.1/")
	tplink.get_dhcp()


full_cmd_arguments = sys.argv
argument_list = full_cmd_arguments[1:]

short_options = "s:"
long_options = ["show="]

try:
	arguments, values = getopt.getopt(argument_list, short_options, long_options)
except getopt.error as err:
	# Output error, and return with an error code
	print (str(err))
	sys.exit(2)

for current_argument, current_value in arguments:
	if current_argument in ("-s", "--show"):
		items = []
		map = {
			'start_pldt' : start_pldt,
			'start_globe' : start_globe,
			'start_tplink' : start_tplink,
			'start_dhcp' : start_dhcp,
		}
		if (current_value == 'all'):
			items.append('pldt')
			items.append('globe')
			items.append('tplink')
			items.append('dhcp')
		elif (current_value == 'pldt'):
			items.append('pldt')
		elif (current_value == 'globe'):
			items.append('globe')
		elif (current_value == 'tplink'):
			items.append('tplink')
		elif (current_value == 'dhcp'):
			items.append('dhcp')

		for i in items:
			func = 'start_' + i
			thread = threading.Thread(target=map[func])
			thread.start()