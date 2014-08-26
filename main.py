#!/usr/bin/env python

import ZTEMF91D
import argparse

def getpass(user):
	file=open('tesla')
	for line in file:
		x = line.split('\t')
		if x[0] == user:
			pw = x[1]
			pw = pw.rstrip()
			return pw
	raise Exception('username not found')

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('-a', '--hostname', action='store', dest='hostname', default='192.168.1.1', help='hostname or IP of ZTE MF91D')
	parser.add_argument('-b', '--port', action='store', dest='port', default='80', help='port where webUI of ZTE MF91D resides')
	parser.add_argument('-u', '--username', action='store', dest='username', default='NULL', help='PPP username to configure APN')
	parser.add_argument('-d', '--delay', action='store', dest='delay', type=float, default=5, help='delay between HTTP requests because ZTE is slow')



	args=parser.parse_args()
	hostname=args.hostname
	port=args.port
	username=args.username
	delay=args.delay

	print args
	sys.stdout.flush()

	zte = ZTEMF91D.ZTEMF91D(ip=hostname,port=port,delay=delay)
	print zte.goform_login_pwd()
	sys.stdout.flush()

	print zte.goform_set_auto_manual()
	sys.stdout.flush()

	#print zte.goform_verify_PIN()

	try:
		username = args.username
		teslo=getpass(username)
	except Exception as e:
		print e
		sys.exit(1)
	print zte.goform_apn_set_add('CONNECTION_NAME','APN_NAME','*99#',username,teslo)
	sys.stdout.flush()

	print zte.goform_apn_set_default()
	sys.stdout.flush()

	print zte.set_remote_Webserver()
	sys.stdout.flush()

	print zte.set_remote_ICMP(1)
	sys.stdout.flush()

	print zte.goform_wlan_set_virtual_server_add()
	sys.stdout.flush()

	#print zte.wlan_dmz_add(ip='192.168.1.2')
	#sys.stdout.flush()

	print zte.GET_wireless_basic()
	sys.stdout.flush()

	print zte.GET_wireless_security()
	sys.stdout.flush()

	print zte.set_networkSelect_3G()
	sys.stdout.flush()



if __name__=='__main__':
	import sys
	sys.stdout.flush()
	main()
