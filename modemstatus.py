#!/usr/bin/env python3
from  modemcurl import *

globe = GlobeAztech('http://192.168.254.254/')
globe.get_status()
print("Globe")
print("Status: " + globe.STATUS['HOME_Adsl_Status'])
print("Uptime: " + globe.STATUS['HOME_Adsl_Uptime'])
print("Download: " + globe.STATUS['HOME_Adsl_Downstream'])
print("Upload: " + globe.STATUS['HOME_Adsl_Upstream'])