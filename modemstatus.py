#!/usr/bin/env python3
import threading
from  modemcurl import *

def startPLDT():
	pldt = PLDTiGateway('http://192.168.1.1/')
	pldt.get_status()

def startGlobe():
	globe = GlobeAztech('http://192.168.254.254/')
	globe.get_status()

def startTPLink():
	tplink = TPLinkR470("http://192.168.0.1/")
	tplink.get_status()

pldt = threading.Thread(target=startPLDT)
globe = threading.Thread(target=startGlobe)
tplink = threading.Thread(target=startTPLink)

pldt.start()
globe.start()
tplink.start()