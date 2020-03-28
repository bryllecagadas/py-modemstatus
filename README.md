# py-modemstatus

## Problem

I have 2 ISPs, and instead of opening 2 pages and the load balancers status page, why not run a script that retrieves the info. 

## Requirements

- python3
- pycurl

## Installation

1. Create a `./config` file and supply the `username` and `password` for the load balancer and the modem
```
[TPLinkR470]
username = username
password = password


[PLDTiGateway]
username = username
password = password
```
2. Modify `./modemstatus.py` and replace the URLs of the modem, include the trailing slash.

3. Done

To run: `./modemstatus.py`