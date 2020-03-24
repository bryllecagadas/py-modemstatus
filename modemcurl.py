import pycurl
import re
from io import BytesIO 

class ModemCurl:
	def __init__(self, URL):
		self.URL = URL
	def get_status(self):
		return 0;

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

		body = bytes.getvalue().decode('utf8')

		print(body)
		#self.STATUS = re.findall("id=\"adslstatus\">.+</td>", body)
		#print(self.STATUS)