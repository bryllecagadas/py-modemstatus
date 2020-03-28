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
username = username_here
password = password_here


[PLDTiGateway]
username = username_here
password = password_here
```
2. Create blank `./pldtcookie` and `./tplinkcookie` files to store cookies.

3. Modify `./modemstatus.py` and replace the URLs of the modems, include the trailing slash.

4. Run the script.

To run: `./modemstatus.py --show=DEVICE`

### Options

DEVICE = Device could either be `all`, `globe`, `pldt`, `dhcp`