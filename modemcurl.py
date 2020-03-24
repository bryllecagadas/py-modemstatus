import json
import pycurl
import re
from io import BytesIO 

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
		crl = pycurl.Curl() 

		crl.setopt(crl.URL, URL)
		crl.setopt(crl.REFERER, self.URL)
		crl.setopt(crl.WRITEDATA, bytes)
		crl.perform() 
		crl.close()

		body = bytes.getvalue().decode('utf8').replace("'", '"')
		replaced = re.sub("(\s*?{\s*?|\s*?,\s*?)(['\"])?([a-zA-Z0-9_]+)(['\"])?:", '\g<1>"\g<3>":', body)
		self.STATUS = json.loads(replaced)
	def print_status(self):
		print("Globe Aztech")
		print("Status: " + self.STATUS['HOME_Adsl_Status'])
		print("Uptime: " + self.STATUS['HOME_Adsl_Uptime'])
		print("Download: " + self.STATUS['HOME_Adsl_Downstream'])
		print("Upload: " + self.STATUS['HOME_Adsl_Upstream'])