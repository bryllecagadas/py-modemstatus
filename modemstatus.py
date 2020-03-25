#!/usr/bin/env python3
import threading
from  modemcurl import *

def startPLDT():
	pldt = PLDTiGateway('http://192.168.1.1/')
	pldt.get_status()

def startGlobe():
	globe = GlobeAztech('http://192.168.254.254/')
	globe.get_status()

pldt = threading.Thread(target=startPLDT)
globe = threading.Thread(target=startGlobe)

pldt.start()
globe.start()