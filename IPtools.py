#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# IPtools v2.0.0 (15.09.2012) by Bystroushaak (bystrousak@kitakitsune.org)
#
# Imports ======================================================================
import os
import sys
import urllib2
import socket
from threading import Timer


try:
	import socks
except ImportError, e:
	sys.stderr.write("I do require sock module. You can get it from\n")
	sys.stderr.write("http://socksipy.sourceforge.net/\n")
	raise e

try:
	from timeout import timeout
except ImportError, e:
	import base64, zlib

	f = open("timeout.py", "w")
	f.write(zlib.decompress(base64.b64decode("""eJx9UsFOhDAQvfcrxnCBzbKYPRmMBw/G
mOhFvW8qtNCktKSdbuTvLUvZUDDby3Rm3kzfe5DcFc6a4keogqkz9AO2WpEE8l0Ola6FakpwyPOHsUIS
36kMqwU+QovYl0XRN07UzB4Uw2KaztGhNoLKay46ph3mNOdOVSi0Kojoem0Q7GCvV9EoKgmQSlJr4Xsa
evmtWD+OpNdbVgIBf/oR5vE14xCeSEM8jXEPvkOdxKy84Be400wk5aE5A/gx3VHT2EV5PdtSVUtm0pGw
6/bADe3YCj8eQ4VlWx0ZgQiqZT2vhKfgwmEKaci+3l6f3z8/9msKWbwpoKmkpoucyCABNKLxL1yaIBQs
+2BZpVVto21ohhK2ohieqfREefApQrCLyo3mf7xh6IyaP1DU5sKLkMN25rY1Cxtv2XIfEw48JlVkVeVH
ssjWv84fYU34lA==""")))
	f.close()

	try:
		from timeout import timeout
	except ImportError, e:
		sys.stderr.write("Lol, you are fucked. Read only medium? SRSLY?\n")
		raise e



# Vars =========================================================================
ip = ["", ""]
TIMEOUT = 5.0



# Functions & objects ==========================================================
class ProxyException(Exception):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return repr(self.msg)
class ProxyTimeoutException(ProxyException):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return repr(self.msg)


@timeout(int(TIMEOUT), None)
def __getPage(url):
	def handler():
		raise ProxyTimeoutException("This proxy is fucking slow, slower than your " + str(TIMEOUT) + "s timeout (see TIMEOUT property).")

	t = Timer(TIMEOUT, handler)
	t.start()

	f = urllib2.urlopen(url, None, 2.5)
	data = f.read()
	t.cancel()

	f.close()
	return data


def getIP():
	ipstr = filter(lambda x: x.startswith("Vaše IP"), __getPage("http://anoncheck.security-portal.cz/").splitlines())[0]
	return "".join(filter(lambda x: x.isdigit() or x == ".", list(ipstr)))
	

@timeout(int(TIMEOUT * 2), None)
def installProxy(SOCK_ADDR, SOCK_PORT):
	# get normal ip
	try:
		ip[0] = getIP()
	except:
		raise ProxyException("Can't connect to internet!")

	# apply proxy
	socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, SOCK_ADDR, SOCK_PORT)
	socket.socket = socks.socksocket

	# get ip over proxy
	try:
		ip[1] = getIP()
	except ProxyTimeout, e:
		raise e
	except:
		raise ProxyException("Your SOCK5 proxy (" + SOCK_ADDR + ":" + str(SOCK_PORT) + ") isn't responding!")

	if ip[0] == ip[1]:
		raise ProxyException("This proxy doesn't hides your IP, use better one")
