#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# IPtools v3.0.1 (24.07.2013) by Bystroushaak (bystrousak@kitakitsune.org)
#
# Imports #####################################################################
import sys
import socket
import random
import urllib2


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



# Vars ########################################################################
__IP         = ["", ""]
TIMEOUT      = 10.0
ORIG_SOCK    = None
EXPECT_CLASS = []  # this is necessary due to garbage collector



# Functions & objects #########################################################
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


@timeout(
	int(TIMEOUT / 2),
	"This proxy is slower than your " + str(TIMEOUT) + "s .TIMEOUT property!"
)
def __getPage(url):
	f = urllib2.urlopen(url)
	data = f.read()
	f.close()

	return data


def getIP():
	"Return current IP address."

	data = __getPage("http://www.whatsmyip.us/showipsimple.php")
	return data.replace('document.write("', "").replace('");', "").strip()


@timeout(int(TIMEOUT), None)
def installProxy(SOCK_ADDR, SOCK_PORT, check_ip = True):
	"Install SOCKS5 proxy."

	# get normal ip
	if check_ip:
		try:
			__IP[0] = getIP()
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
			__IP[1] = getIP()
		except ProxyTimeoutException, e:
			raise e
		except:
			raise ProxyException(
				"Your SOCK5 proxy (" +
				SOCK_ADDR +
				":" +
				str(SOCK_PORT) +
				") isn't responding!"
			)

		if __IP[0] == __IP[1]:
			raise ProxyException("This proxy doesn't hides your IP, use better one")


def sshTunnel(login_serv, e, port = None, check_ip = True, timeout = TIMEOUT):
	"""
	Create (but don't use -> see installProxy()) SOCKS5 tunnel over SSH.

	Example:
	---
	import IPtools

	print IPtools.getIP() # -> your IP

	IPtools.installProxy(
		"localhost",
		IPtools.sshTunnel("ssh@somewhere.com", timeout = 30)
	)

	print IPtools.getIP() # -> tunnel's IP
	---

	Return port where tunnel is listenning.
	"""

	if port is None:
		port = random.randint(1025, 65534)

	# create ssh tunnel
	c = pexpect.spawn("ssh -D " + str(port) + " " + login_serv)
	tmp = c.expect([e, "yes/no"], timeout = timeout)

	# ssh key authorization
	if tmp == 1:
		c.sendline("yes")
		c.expect(e, timeout = timeout)

	EXPECT_CLASS.append(c)  # dont let garbage collector delete this

	return port



# Main ########################################################################
if __name__ == '__main__':
	print "IPTools; https://github.com/Bystroushaak/IPtools"
