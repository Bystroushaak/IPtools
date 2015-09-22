#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to ease usage of SOCK5 proxy and SSH tunnel installation.

There is also functions for checking your IP.

Examples:
--
>>> import IPtools
>>> IPtools.getIP()
'429.292.637.2'  # modified to protect my privacy
--

SSH proxy:
--
>>> port = IPtools.sshTunnel("bystrousak@kitakitsune.org", "###")
>>> IPtools.installProxy("localhost", port)
>>> IPtools.getIP()
'31.31.73.113'
--

Restoring original socket:
--
>>> import IPtools
>>> IPtools.getIP()
'429.292.637.2'
>>> IPtools.installProxy("localhost", IPtools.sshTunnel("bystrousak@kitakitsune.org", "###"))
>>> IPtools.getIP()
'31.31.73.113'
>>> IPtools.restoreSocket()
>>> IPtools.getIP()
'429.292.637.2'
>>>
--

Author: Bystroushaak (bystrousak@kitakitsune.org)
"""
#
# Imports #####################################################################
import sys
import copy
import socket
import random
import urllib2


try:
    import pexpect
except ImportError, e:
    sys.stderr.write(
        "I do require pexpect module. You can get it from\n"
        "http://sourceforge.net/projects/pexpect/ OR from 'python-pexpect'"
        "ubuntu package OR from PIP (pexpect)\n"
    )
    raise


try:
    import socks
except ImportError, e:
    sys.stderr.write(
        "I do require sock module. You can get it from\n"
        "http://socksipy.sourceforge.net/ OR from PIP (SocksiPy)\n"
    )
    raise


try:
    from timeout_wrapper import timeout
except ImportError, e:
    sys.stderr.write(
        "I do require sock module. You can get it from\n"
        "using sudo pip install -U timeout_wrapper.\n"
    )
    raise


# Vars ########################################################################
_IP = ["", ""]
TIMEOUT = 10.0
ORIG_SOCK = None

EXPECT_CLASS = []  # this is necessary due to garbage collector


# Functions & objects #########################################################
class ProxyException(Exception):
    pass


@timeout(
    int(TIMEOUT / 2),
    exception_message="The proxy is slower than your %ss .TIMEOUT!" % TIMEOUT
)
def _get_page(url):
    f = urllib2.urlopen(url)
    data = f.read()
    f.close()

    return data


def getIP():
    """
    Get current IP address.

    Returns:
        str: IP address.
    """
    data = _get_page("http://myip.cz")
    data = data.split("Your IP Address is: <b>")[-1].split("</b>")[0]
    return data.strip()


@timeout(int(TIMEOUT), None)
def installProxy(SOCK_ADDR, SOCK_PORT, check_ip=True):
    """
    Install SOCKS5 proxy.

    Raise ProxyTimeoutException
    """
    # get normal ip
    if check_ip:
        try:
            _IP[0] = getIP()
        except Exception, e:
            raise ProxyException("Can't connect to internet!\n" + str(e))

    # save original socket
    global ORIG_SOCK
    ORIG_SOCK = copy.copy(socket.socket)

    # apply proxy
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, SOCK_ADDR, SOCK_PORT)
    socket.socket = socks.socksocket

    # get ip over proxy
    if not check_ip:
        return

    try:
        _IP[1] = getIP()
    except Exception, e:
        raise ProxyException(
            "Your SOCK5 proxy (" + SOCK_ADDR + ":" + str(SOCK_PORT) + ") "
            "isn't responding!\n" +
            str(e)
        )

    if _IP[0] == _IP[1]:
        raise ProxyException(
            "This proxy doesn't hides your IP, use better one."
        )


def sshTunnel(login_serv, e, port=None, timeout=TIMEOUT):
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

    Return port where the tunnel is listenning.
    """
    if port is None:
        port = random.randint(1025, 65534)

    # create ssh tunnel
    c = pexpect.spawn("ssh -D " + str(port) + " " + login_serv)
    tmp = c.expect([e, "yes/no"], timeout=timeout)

    # ssh key authorization
    if tmp == 1:
        c.sendline("yes")
        c.expect(e, timeout=timeout)

    EXPECT_CLASS.append(c)  # dont let garbage collector delete this
    return port


def restoreSocket():
    """Removes proxy from your system and restores original socket."""
    global ORIG_SOCK
    socket.socket = ORIG_SOCK
