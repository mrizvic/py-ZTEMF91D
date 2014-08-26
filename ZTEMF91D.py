import datetime
from random import randrange
import urllib
import urllib2
import cookielib
import time
import socket
import struct

'''
Device info:
	var manufacturer = 'ZTE';
	var ufi_type = 'MF91D';
	var software_version = 'BD_MF91D_EURO_V1.0.0B04';
	var imei = 'CENSORED';
	var hardware_version = 'xk1B';
	var system_up_time = '5 hours, 20 mins, 17 secs';
	system_up_time_result = str_replace(system_up_time);
	var manufacturer_home = 'www.zte.com.cn';
	var webui_version = 'WEB_EURO_MF91DV1.0.0B03';
'''

class ZTEMF91D(object):

	'''
	Manipulate with ZTE MF91D configuration over web interface
	'''

	def __init__(self,ip='192.168.1.1',port='80',userpass='admin',delay=5):
		self.url='http://{0}:{1}'.format(ip,port)
		self.userpass=userpass
		self.delay=delay

		#create lucky number

		t = int(datetime.datetime.now().strftime('%s')) * 1000
		t = t % (1000*60*60*24)
		rand = randrange(10000)
		self.lucky_num = t * 10000 + rand

		self.cookies = {'Cookie':'MF91_lucky_num={}'.format(self.lucky_num)}

	def __Request(self,url,values,cookies='',info='',timeout=5,verbose=0):
		if cookies == '':
			cookies = self.cookies
		if info == '':
			print 'trying URL {0}'.format(url)
		else:
			print info

		try:
			data = urllib.urlencode(values)
			if verbose > 0:
				print url
				print data
				print cookies
				print ''

			'''Wait between each HTTP request because ZTE is kinda slow'''
			time.sleep(self.delay)
			request = urllib2.Request(url,data,cookies)
			response = urllib2.urlopen(request,timeout=timeout)

			buffer = response.read()
			return buffer
		except Exception as e:
			print e

	def __zte_ipcalc(self,ip):

		'''
		Strange formula when you are adding IP address to DMZ
		'''

		iplong = struct.unpack('!L', socket.inet_aton(ip))[0]
		ipzte = -1 * ((2**32) - iplong)
		return ipzte

	def goform_login_pwd(self):

		'''
		Login to ZTE MF91D web interface
		'''

		userpass = self.userpass
		lucky_num = self.lucky_num
		values={
					'userpass'	:	userpass,
					'lucky_num'	:	lucky_num,
					'login'		:	'Login'
		}

		url=self.url + '/goform/login_pwd'
		return self.__Request(url,values,info='logging in...')

	def goform_verify_PIN(self,pin):

		'''
		PIN code verify procedure after login (if required by SIMLOCK)
		'''

		if pin is None:
			raise Exception('PIN requested but not set')

		values={
					'Pin_Verify'	:	pin,
					'save'			:	'Apply'
		}

		url = self.url + '/goform/Verify_PIN'
		return self.__Request(url,values,info='verifying PIN...')

	def goform_apn_set_add(self,profile_name,apn_name,dialnum,ppp_username,ppp_password,ppp_auth_mode='pap'):

		'''
		Procedure for adding APN to ZTE
		'''

		values={
					'goformId'			:	'APN_PROC',
					'lucknum_APN_PROC'	:	'',
					'apn_select'		:	'manual',
					'wan_dial'			:	dialnum,
					'pdp_type'			:	'PPP',
					'pdp_select'		:	'auto',
					'pdp_addr'			:	'',
					'profile_name'		:	profile_name,
					'wan_apn'			:	apn_name,
					'ppp_auth_mode'		:	ppp_auth_mode,
					'ppp_username'		:	ppp_username,
					'ppp_passwd'		:	ppp_password,
					'dns_mode'			:	'auto',
					'prefer_dns_manual1':	'',
					'prefer_dns_manual2':	'',
					'prefer_dns_manual3':	'',
					'prefer_dns_manual4':	'',
					'standby_dns_manual1':	'',
					'standby_dns_manual2':	'',
					'standby_dns_manual3':	'',
					'standby_dns_manual4':	'',
					'Submit'			:	'Save',
					'index'				:	'',
					'default_index'		:	'',
					'ifdelete'			:	'',
					'profilename'		:	'',
					'profile_for_bug'	:	'',
					'add_flag'			:	''
		}

		url = self.url + '/goform/apn_set_add'
		return self.__Request(url,values,info='adding APN {0} with username {1}'.format(apn_name,ppp_username))

	def goform_apn_set_default(self,profileid=2):
		'''
		Set default APN profile
		'''

		values={
				'goformId'				:	'DHCP_SET',
				'lucknum_DHCP_SET'		:	'',
				'apn_profile'			:	profileid,
				'auto_manual_APN'		:	''
		}

		url = self.url + '/goform/apn_set_defalt'
		return self.__Request(url,values,info='setting default APN id {0}'.format(profileid))


	def goform_set_auto_manual(self):
		'''
		Switch to manualy defined APN.
		TODO: switch back to automatic
		'''

		values={
				'auto_manual_APN'		:	'Manual_APN1'
		}

		url = self.url + '/goform/set_auto_manual_APN'
		return self.__Request(url,values,info='setting APN to user defined...')

	def goform_Restore(self):
		'''
		Factory default ZTE
		'''

		values={
				'restore'		:		'Restore'
		}

		url = self.url + '/goform/Restore'
		return self.__Request(url,values,info='factory reset procedure...')

	def internet_apn(self):
		'''
		Get configured APN profiles from the device
		'''

		values={
						'foo'	:	'bar'
		}

		url = self.url + '/internet/apn.asp'
		response = self.__Request(url,values,info='retrieving configured APN profiles...')
		response = response.split('\n')
		for line in response:
			if line.startswith('apn[') and not '2468531' in line:
				print line
			if 'var_apn_default' in line:
				print line

		return 'TODO'

	def wlan_dmz_add(self,ip):
		'''
		Configure IP address to DMZ
		'''

		ipzte = self.__zte_ipcalc(ip)
		values={
						'goformId'					:	'FW_FILTER_ADD',
						'lucknum_FW_FILTER_ADD'		:	'',
						'ip_addr'					:	ipzte,
						'input3'					:	'Apply'
		}

		url = self.url + '/goform/wlan_dmz_add'
		return self.__Request(url,values,info='adding IP {0} to DMZ...'.format(ip))

	def set_remote_Webserver(self):
		'''
		Allow ZTE web page to be accessed via WAN IP
		'''

		values={
				'remote_webserver_enable'	:	'1',
				'sysfwApply'				:	'Apply'
		}

		url = self.url + '/goform/set_remote_Webserver'
		return self.__Request(url,values,info='enabling ZTE web page to be accessed via WAN IP...')

	def goform_wlan_set_virtual_server_add(self,ip='192.168.1.2',global_port='22',private_port='22',protocol='TCP'):
		'''
		Create port forwarding
		'''

		values={
				'virtual_server_setting'		:	'Enable',
				'ip_addr'						:	ip,
				'private_port'					:	private_port,
				'global_port'					:	global_port,
				'protocol'						:	protocol,
				'setting_Apply'					:	'Apply'
		}

		url = self.url + '/goform/wlan_set_virtual_server_add'
		return self.__Request(url,values,info='adding virtual server WAN:{0} -> {1}:{2}/{3}'.format(global_port,ip,private_port,protocol))

	def GET_wireless_basic(self):
		'''
		Get WiFi basic configuration parameters
		'''

		url = self.url + '/wireless/basic.asp'
		values={'foo':'bar'}
		response = self.__Request(url,values,info='getting WIFI basic settings')
		response = response.split('\n')
		for line in response:
			if line.startswith('var '):
				print line


	def GET_wireless_security(self):
		'''
		Get WiFi security configuration parameters
		'''

		url = self.url + '/wireless/security.asp'
		values={'foo':'bar'}
		response = self.__Request(url,values,info='getting WIFI security settings')
		response = response.split('\n')
		for line in response:
			if line.startswith('var '):
				print line

	def GET_basicstatus(self):
		'''
		Get basic status info
		'''

		url = self.url + '/status/basicstatus.asp'
		values={'foo':'bar'}
		response = self.__Request(url,values,info='getting basic status info')
		response = response.split('\n')
		for line in response:
			if line.startswith('	var '):
				print line

	def GET_netstatus(self):
		'''
		Get network status info
		'''

		url = self.url + '/status/netstatus.asp'
		values={'foo':'bar'}
		return self.__Request(url,values,info='getting network status info')

	def set_remote_ICMP(self,flag=0):
		'''
		Allow ping from WAN filter
		'''

		if flag == 0 or flag == 1:
			url = self.url + '/goform/set_remote_ICMP?remote_icmp_enable={0}&sysfwApply=Apply'.format(flag)
			values={'foo':'bar'}
			return self.__Request(url,values,info='setting remote ICMP to {0}'.format(flag))
		else:
			raise Exception('invalid flag'.format(flag))

	def set_networkSelect_3G(self):
		'''
		Force ZTEMF91D to 3G mode only
		'''

		url = self.url + '/goform/SetNetworkSelectionMode?file=4&node=AutoManual'
		values = {
						'goFormId'					:	'NET_CONNECT',
						'lucknum_NET_CONNECT'		:	'',
						'value'						:	'0',
						'dial_mode'					:	'auto_dial',
						'NetSelect_Mode'			:	'Auto',
						'mode'						:	'wcdma_mode',
						'Submit_linkset'			:	'Apply'
		}

		return self.__Request(url,values,info='force modem to 3G only')



def getpass(user):
	file=open('tesla')
	for line in file:
		x = line.split('\t')
		if x[0] == user:
			pw = x[1]
			pw = pw.rstrip()
			return pw
	raise Exception('username not found')
