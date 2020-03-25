import ast
import configparser
import json
import pycurl
import re
import urllib
from io import BytesIO 
from http.cookiejar import Cookie, MozillaCookieJar

class ModemCurl:
	def __init__(self, URL):
		self.URL = URL
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
		# Wrap names in double quotes for json.loads
		replaced = re.sub("(\s*?{\s*?|\s*?,\s*?)(['\"])?([a-zA-Z0-9_]+)(['\"])?:", '\g<1>"\g<3>":', body)

		self.STATUS = json.loads(replaced)
		self.print_status()
	def print_status(self):
		print("Globe Aztech")
		print("Status: " + self.STATUS['HOME_Adsl_Status'])
		print("Uptime: " + self.STATUS['HOME_Adsl_Uptime'])
		print("Download: " + self.STATUS['HOME_Adsl_Downstream'])
		print("Upload: " + self.STATUS['HOME_Adsl_Upstream'])

class TPLinkR470(ModemCurl):
	def get_status(self):
		configParser = configparser.RawConfigParser()   
		configFilePath = 'config'
		configParser.read(configFilePath)

class PLDTiGateway(ModemCurl):
	def get_data(self, content):
		result = PLDTiGatewayResult(content)
		self.STATUS = result.parse()

	def get_status(self):
		URL = self.URL + 'cgi-bin/webproc'
		bytes = BytesIO()
		curl = pycurl.Curl() 
		configParser = configparser.RawConfigParser()   

		configFilePath = 'config'
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
		curl.setopt(curl.URL, URL)
		curl.setopt(curl.REFERER, self.URL + 'cgi-bin/webproc')
		curl.setopt(curl.COOKIEFILE, 'cookie')
		curl.setopt(curl.WRITEDATA, f)
		curl.perform()

		cookiejar = MozillaCookieJar()
		cookiejar.load('cookie')

		sessionid = ''
		for cookie in cookiejar:
			if (cookie.name == 'sessionid'):
				sessionid = cookie.value

		if (sessionid == ''):
			return

		post += "&%3Asessionid=" + sessionid

		# Try to login with the sessionid
		curl.setopt(curl.URL, URL)
		curl.setopt(curl.REFERER, self.URL + 'cgi-bin/webproc')
		curl.setopt(curl.POSTFIELDS, post)
		curl.setopt(curl.COOKIEJAR, 'cookie')
		curl.setopt(curl.FOLLOWLOCATION, 1)
		curl.setopt(curl.WRITEDATA, f)
		curl.perform()

		f.close()

		# Retrieve the status page
		curl.setopt(curl.URL, URL + "?getpage=html/index.html&var:menu=status&var:page=deviceinfo")
		curl.setopt(curl.REFERER, self.URL + 'cgi-bin/webproc')
		curl.setopt(curl.WRITEDATA, bytes)
		curl.perform()

		content = bytes.getvalue().decode('utf8', 'ignore')

		if (content):
			self.get_data(content)
			self.print_status()

	def print_status(self):
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
			evaled = ast.literal_eval(cleansed)
			result['name'] = evaled[0]
			result['status'] = evaled[1]
			result['ip'] = evaled[8]
			result['uptime'] = evaled[14]

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