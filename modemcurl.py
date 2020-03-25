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

		body = bytes.getvalue().decode('utf8', 'ignore').replace("'", '"')
		replaced = re.sub("(\s*?{\s*?|\s*?,\s*?)(['\"])?([a-zA-Z0-9_]+)(['\"])?:", '\g<1>"\g<3>":', body)
		self.STATUS = json.loads(replaced)
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
	def get_status(self):
		URL = self.URL + 'cgi-bin/webproc'
		bytes = BytesIO()
		curl = pycurl.Curl() 
		configParser = configparser.RawConfigParser()   

		configFilePath = 'config'
		configParser.read(configFilePath)
		username = configParser.get(self.__class__.__name__, 'username')
		password = configParser.get(self.__class__.__name__, 'password')

		post = "getpage=html%2Findex.html&errorpage=html%2Fmain.html&" \
			"var%3Amenu=setup&var%3Apage=wireless&obj-action=auth&" \
			"%3Ausername=" + username + "&%3Apassword=" + password + \
			"&%3Aaction=login&"

		curl.setopt(curl.URL, URL)
		curl.setopt(curl.REFERER, self.URL + 'cgi-bin/webproc')
		curl.setopt(curl.COOKIEFILE, 'cookie')
		curl.setopt(curl.WRITEDATA, bytes)
		curl.perform()

		curl.setopt(curl.URL, URL)
		curl.setopt(curl.REFERER, self.URL + 'cgi-bin/webproc')
		curl.setopt(curl.POSTFIELDS, post)
		curl.setopt(curl.COOKIEJAR, 'cookie')
		curl.setopt(curl.FOLLOWLOCATION, 1)
		curl.setopt(curl.WRITEDATA, bytes)
		curl.perform()

		bytes.seek(0)
		curl.setopt(curl.URL, URL + "?getpage=html/index.html&var:menu=status&var:page=deviceinfo")
		curl.setopt(curl.REFERER, self.URL + 'cgi-bin/webproc')
		curl.setopt(curl.WRITEDATA, bytes)
		curl.perform()

		print(bytes.getvalue().decode('utf8', 'ignore'))