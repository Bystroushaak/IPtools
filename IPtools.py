#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# IPtools v2.2.0 (07.07.2012) by Bystroushaak (bystrousak@kitakitsune.org)
#
# Imports ======================================================================
import os
import sys
import socket
import random
import urllib2
from threading import Timer


try:
	import pexpect
except ImportError, e:
	sys.stderr.write("I do require pexpect module. You can get it from\n")
	sys.stderr.write("http://sourceforge.net/projects/pexpect/\n")
	raise e


try:
	import socks
except ImportError, e:
	sys.stderr.write("I do require sock module. You can get it from\n")
	sys.stderr.write("http://socksipy.sourceforge.net/\n")
	raise e


from timeout import timeout



# Vars =========================================================================
IP = ["", ""]
TIMEOUT = 5.0
ORIG_SOCK = None



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
	"Return IP address (from http://anoncheck.security-portal.cz/)."

	ipstr = filter(lambda x: x.startswith("Vaše IP"), __getPage("http://anoncheck.security-portal.cz/").splitlines())[0]
	return "".join(filter(lambda x: x.isdigit() or x == ".", list(ipstr)))
	

@timeout(int(TIMEOUT * 2), None)
def installProxy(SOCK_ADDR, SOCK_PORT, check_ip = True):
	"Install SOCKS5 proxy."

	# get normal ip
	if check_ip:
		try:
			IP[0] = getIP()
		except:
			raise ProxyException("Can't connect to internet!")

	# save original socket
	global ORIG_SOCK
	ORIG_SOCK = socket.socket

	# apply proxy
	socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, SOCK_ADDR, SOCK_PORT)
	socket.socket = socks.socksocket

	# get ip over proxy
	if check_ip:
		try:
			IP[1] = getIP()
		except ProxyTimeoutException, e:
			raise e
		except:
			raise ProxyException("Your SOCK5 proxy (" + SOCK_ADDR + ":" + str(SOCK_PORT) + ") isn't responding!")

		if IP[0] == IP[1]:
			raise ProxyException("This proxy doesn't hides your IP, use better one")


def sshTunnel(login_serv, e, port = None, check_ip = True, timeout = 10):
	"Create ssh SOCKS5 tunnel."

	if port == None:
		port = random.randint(1025, 65534)

	# create ssh tunnel
	c = pexpect.spawn("ssh -D " + str(port) + " " + login_serv)
	tmp = c.expect([e, "yes/no"], timeout = timeout)

	# ssh key authorization
	if tmp == 1:
		c.sendline("yes")
		c.expect(e, timeout = timeout)

	installProxy("127.0.0.1", port, check_ip)

	return c


# Main =========================================================================
if __name__ == '__main__':
	print "IPTools; https://github.com/Bystroushaak/IPtools"