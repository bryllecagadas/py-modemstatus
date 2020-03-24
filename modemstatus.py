#!/usr/bin/env python3
from  modemcurl import *

globe = GlobeAztech('http://192.168.254.254/')
globe.get_status()