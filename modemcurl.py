import ast
import configparser
import hashlib
import json
import math
import os
import pycurl
import re
import urllib
from http.cookiejar import Cookie, MozillaCookieJar, FileCookieJar
from io import BytesIO 

class ModemCurl:
	def __init__(self, URL):
		self.URL = URL
		self.basepath = os.path.dirname(os.path.realpath(__file__))

	def get_status(self):
		return 0

	def print_status(self):
		return 0

class GlobeAztech(ModemCurl):
	def get_status(self):
		URL = self.URL + 'cgi-bin/main_json.asp'
		bytes = BytesIO() 
		curl = pycurl.Curl() 

		curl.setopt(curl.URL, URL)
		curl.setopt(curl.REFERER, self.URL)
		curl.setopt(curl.WRITEDATA, bytes)
		curl.perform() 
		curl.close()

		# Wrap values in double quotes in order for json.loads to succeed
		body = bytes.getvalue().decode('utf8', 'ignore').replace("'", '"')

		# Retrieve problematic  HOME_Adsl_Uptime value and replace with a placeholder
		match = re.search("HOME_Adsl_Uptime\:\"(.+?)\"", body)
		matches = match.groups()
		uptime_value = 0
		if (len(matches) > 0):
			body = re.sub("HOME_Adsl_Uptime\:\".+?\"", 'HOME_Adsl_Uptime:"HOME_Adsl_Uptime_value"', body)
			uptime_value = matches[0]

		# Wrap names in double quotes for json.loads
		replaced = re.sub("(\s*?{\s*?|\s*?,\s*?)(['\"])?([a-zA-Z0-9_]+)(['\"])?:", '\g<1>"\g<3>":', body)
		self.STATUS = json.loads(replaced)
		self.STATUS['HOME_Adsl_Uptime'] = uptime_value

		self.print_status()

	def print_status(self):
		print("-")
		print("Globe Aztech")
		print("Status: " + self.STATUS['HOME_Adsl_Status'])
		print("Uptime: " + self.STATUS['HOME_Adsl_Uptime'])
		print("Download: " + self.STATUS['HOME_Adsl_Downstream'])
		print("Upload: " + self.STATUS['HOME_Adsl_Upstream'])

class TPLinkR470(ModemCurl):
	def __init__(self, URL):
		self.logged_in = False
		super(TPLinkR470, self).__init__(URL)

	def get_data(self, content):
		result = TPLinkResult(content)
		self.STATUS = result.parse()

	def get_dhcp_data(self, content):
		result = TPLinkDHCP(content)
		self.DHCPSTATUS = result.parse()

	def get_dhcp(self):
		self.login()
		bytes = BytesIO()

		# Retrieve the information
		curl = pycurl.Curl()
		curl.setopt(curl.URL, self.URL + "userRpm/DhcpServer_ClientList.htm?slt_interface=0")
		curl.setopt(curl.REFERER, self.URL + "userRpm/Interface_LanSetting.htm")
		curl.setopt(curl.COOKIEFILE, self.basepath + '/tplinkcookie')
		curl.setopt(curl.WRITEDATA, bytes)
		curl.perform()
		curl.close()

		content = bytes.getvalue().decode('utf8', 'ignore')
		print('here')
		if (content):
			self.get_dhcp_data(content)
			self.print_dhcp()

	def get_status(self):
		self.login()
		bytes = BytesIO()

		# Retrieve the information
		curl = pycurl.Curl()
		curl.setopt(curl.URL, self.URL + "userRpm/Monitor_sysinfo_wanstatus.htm")
		curl.setopt(curl.REFERER, self.URL + "userRpm/Monitor_sysinfo_wanstatus.htm")
		curl.setopt(curl.COOKIEFILE, self.basepath + '/tplinkcookie')
		curl.setopt(curl.WRITEDATA, bytes)
		curl.perform()
		curl.close()

		content = bytes.getvalue().decode('utf8', 'ignore')
		if (content):
			self.get_data(content)
			self.print_status()


	def login(self):
		if (self.logged_in == True):
			return

		URL = self.URL + 'logon/loginJump.htm'
		bytes = BytesIO()
		configParser = configparser.RawConfigParser()   
		configFilePath = self.basepath + '/config'
		configParser.read(configFilePath)
		username = configParser.get(self.__class__.__name__, 'username')
		password = configParser.get(self.__class__.__name__, 'password')

		f = open('/dev/null', 'wb')

		# We try to retrieve the cookie COOKIE
		curl = pycurl.Curl() 
		curl.setopt(curl.URL, self.URL)
		curl.setopt(curl.COOKIEJAR, self.basepath + '/tplinkcookie')
		curl.setopt(curl.WRITEDATA, f)
		curl.perform()
		curl.close()

		cookiejar = MozillaCookieJar()
		cookiejar.load(filename=self.basepath + '/tplinkcookie', ignore_expires=True)

		nonce = ''
		for cookie in cookiejar:
			if (cookie.name == 'COOKIE'):
				nonce = cookie.value

		
		# Generate the hash
		hash = hashlib.md5(password.encode('utf8')).hexdigest()
		hash = hash.upper() + ":" + nonce
		hash = hashlib.md5(hash.encode("utf8")).hexdigest().upper()

		# Try to login with the username and the hashed string
		post = "encoded=" + username + "%3A" + hash +  "&nonce=" + nonce + "&URL=..%2Flogon%2FloginJump.htm"

		curl = pycurl.Curl()
		curl.setopt(curl.URL, URL)
		curl.setopt(curl.REFERER, URL)
		curl.setopt(curl.POSTFIELDS, post)
		curl.setopt(curl.COOKIEFILE, self.basepath + '/tplinkcookie')
		curl.setopt(curl.FOLLOWLOCATION, 1)
		curl.setopt(curl.WRITEDATA, bytes)
		curl.perform()

		# Check if user is already logged-in somewhere
		match = re.search("doContinue\(\)", bytes.getvalue().decode('utf8', 'ignore'), re.MULTILINE)
		curl.reset()
		if (match):
			curl.setopt(curl.URL, self.URL + "logon/loginConfirm.htm")
			curl.setopt(curl.REFERER, URL)
			curl.setopt(curl.COOKIEFILE, self.basepath + '/tplinkcookie')
			curl.setopt(curl.FOLLOWLOCATION, 1)
			curl.setopt(curl.WRITEDATA, f)
			curl.perform()

		f.close()
		curl.close()
		self.logged_in = True

	def print_dhcp(self):
		for i in range(len(self.DHCPSTATUS)):
			print("-")
			print("Client " + str(i + 1))
			print("Name: " + self.DHCPSTATUS[i]['name'])
			print("MAC: " + self.DHCPSTATUS[i]['mac'])
			print("IP: " + self.DHCPSTATUS[i]['ip'])
			print("Time: " + self.DHCPSTATUS[i]['time'])

	def print_status(self):
		for i in self.STATUS:
			print("-")
			print("TPLink: " + i['name'])
			print("Status: " + i['status'])
			print("IP: " + i['ip'])
			print("Gateway: " + i['gateway'])

class PLDTiGateway(ModemCurl):
	def get_data(self, content):
		result = PLDTiGatewayResult(content)
		self.STATUS = result.parse()

	def get_status(self):
		URL = self.URL + 'cgi-bin/webproc'
		bytes = BytesIO()
		configParser = configparser.RawConfigParser()   

		configFilePath = self.basepath + '/config'
		configParser.read(configFilePath)
		username = configParser.get(self.__class__.__name__, 'username')
		password = configParser.get(self.__class__.__name__, 'password')

		f = open('/dev/null', 'wb')

		post = "getpage=html%2Findex.html&errorpage=html%2Fmain.html&" \
			"var%3Amenu=setup&var%3Apage=wireless&obj-action=auth&" \
			"%3Ausername=" + username + "&%3Apassword=" + password + \
			"&%3Aaction=login"

		# First step is to retrieve the sessionid
		# The sessionid is required in order for login to go through
		curl = pycurl.Curl() 
		curl.setopt(curl.URL, URL)
		curl.setopt(curl.COOKIEJAR, self.basepath + '/pldtcookie')
		curl.setopt(curl.WRITEDATA, f)
		curl.perform()
		curl.close()

		cookiejar = MozillaCookieJar()
		cookiejar.load(self.basepath + '/pldtcookie')

		sessionid = ''
		for cookie in cookiejar:
			if (cookie.name == 'sessionid'):
				sessionid = cookie.value

		if (sessionid == ''):
			return

		post += "&%3Asessionid=" + sessionid

		# Try to login with the sessionid
		curl = pycurl.Curl()
		curl.setopt(curl.URL, URL)
		curl.setopt(curl.REFERER, self.URL + 'cgi-bin/webproc')
		curl.setopt(curl.POSTFIELDS, post)
		curl.setopt(curl.COOKIEFILE, self.basepath + '/pldtcookie')
		curl.setopt(curl.FOLLOWLOCATION, 1)
		curl.setopt(curl.WRITEDATA, f)
		curl.perform()

		f.close()

		# Retrieve the status page
		curl.setopt(curl.URL, URL + "?getpage=html/index.html&var:menu=status&var:page=deviceinfo")
		curl.setopt(curl.REFERER, self.URL + 'cgi-bin/webproc')
		curl.setopt(curl.WRITEDATA, bytes)
		curl.perform()
		curl.close()

		content = bytes.getvalue().decode('utf8', 'ignore')

		if (content):
			self.get_data(content)
			self.print_status()

	def print_status(self):
		print("-")
		print("PLDT iGateway")
		print("Status: " + self.STATUS['status'])
		print("Uptime: " + self.STATUS['uptime'])
		print("Download: " + self.STATUS['download'])
		print("Upload: " + self.STATUS['upload'])
		return

class PLDTiGatewayResult:
	def __init__(self, content):
		self.content = content

	def parse(self):
		result = {
			'name': '',
			'status': '',
			'ip' : '',
			'uptime' : '',
			'download' : '',
			'upload' : ''
		}

		# Retrieve block of javascript object that contains the information
		match = re.search("G_wanConnction\[m\] = (\[.+?\])\;", self.content, re.MULTILINE | re.DOTALL)
		matches = match.groups()

		if(len(matches) == 1):
			isolated = matches[0]
			# Remove comments from the block
			cleansed = re.sub(" ?//[a-zA-Z ]*\r", "", isolated)
			# Remove the javascript code
			cleansed = re.sub("==\"[a-zA-Z]*\" \? [a-zA-Z_ \.\:]* ,", ",", cleansed)
			
			# Try to eval the cleaned value
			eval = ast.literal_eval(cleansed)
			result['name'] = eval[0]
			result['status'] = eval[1]
			result['ip'] = eval[8]
			result['uptime'] = eval[14]

		# Retrieve download rate
		match = re.search("G_dsl_downrate = \"(\d+)\"", self.content)
		matches = match.groups()
		if(len(matches) == 1):
			result['download'] = matches[0]

		# Retrieve upload rate
		match = re.search("G_dsl_uprate = \"(\d+)\"", self.content)
		matches = match.groups()
		if(len(matches) == 1):
			result['upload'] = matches[0]		

		return result

class TPLinkResult:
	def __init__(self, content):
		self.content = content

	def parse(self):
		result = []
		statuses = [
			'Disconnected',
			'Connecting',
			'Connected',
			'Disabled',
			'Online Detection failed',
			'Online Detection success',
			'Online Detection is disabled',
		]

		# Retrieve block of javascript object that contains the information
		match = re.search("var wanInfoArr \= new Array\((.+?)\)\;", self.content, re.MULTILINE | re.DOTALL)
		matches = match.groups()

		raw = ''
		if(len(matches) == 1):
			raw = matches[0].replace("\n", '')

		eval = ast.literal_eval('[' + raw + ']')
		wan = 0
		length = len(eval)
		for i in range(0, length, 11):
			if (i + 5 > length):
				break
			if (eval[i] != 0):
				wan += 1
				if (eval[i] == 5):
					status = statuses[2]
				else:
					status = statuses[int(eval[i])]

				base = {
					'name': 'Wan ' + str(wan),
					'gateway': eval[i + 5],
					'ip': eval[i + 3],
					'status': status,
				}

				result.append(base)

		return result

class TPLinkDHCP:
	def __init__(self, content):
		self.content = content

	def parse(self):
		result = []

		# Retrieve block of javascript object that contains the information
		match = re.search("var dhcpList \= new Array\((.+?)\)\;", self.content, re.MULTILINE | re.DOTALL)
		matches = match.groups()

		raw = ''
		if(len(matches) == 1):
			raw = matches[0].replace("\n", '')

		eval = ast.literal_eval('[' + raw + ']')
		wan = 0
		length = len(eval)
		for i in range(0, length, 4):
			if (i + 3 > length):
				break

			base = {
				'name': eval[i],
				'mac': eval[i + 1],
				'ip': eval[i + 2],
				'time': self.format_time(eval[i + 3]),
			}

			result.append(base)

		return result

	def format_time(self, seconds):
		seconds = int(seconds)
		h = seconds / 3600
		m = (seconds % 3600) / 60
		s = seconds % 60

		h = str(math.floor(h))

		if (m < 10):
			m = '0' + str(math.floor(m))
		else:
			m = str(math.floor(m))

		s = str(s)

		return h + ":" + m + ":" + s