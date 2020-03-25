#!/usr/bin/env python3
from  modemcurl import *

pldt = PLDTiGateway('http://192.168.1.1/')
pldt.get_status()
print("")
globe = GlobeAztech('http://192.168.254.254/')
globe.get_status()