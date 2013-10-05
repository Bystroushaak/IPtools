#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Timeout() to limit execution time of your functions.

Author: Bystroushaak (bystrousak@kitakitsune.org)
Credit; http://pguides.net/python-tutorial/python-timeout-a-function/
"""
# Imports #####################################################################
import signal



# Functions & classes #########################################################
class TimeoutException(Exception):
	def __init__(self, value = ""):
		self.value = value

	def __str__(self):
		return repr(self.value)


def __timeout_handler(signum, frame):
	raise TimeoutException()


def timeout(timeout_time, default, exception_message = None):
	"""
	Use this as decorator to your functions:

	--
	@timeout(5, None)
	def myFunc(..)
	--

	timeout_time -- measured in seconds
	default -- default value returned if function timeouts
	exception_message -- if set, raise TimeoutException instead of returning
	default value.
	"""
	def __timeout_function(f):
		def f2(*args, **kwargs):
			old_handler = signal.signal(signal.SIGALRM, __timeout_handler)
			signal.alarm(timeout_time)  # triger alarm in timeout_time seconds

			try:
				retval = f(*args, **kwargs)
			except TimeoutException:
				if exception_message is not None:
					raise TimeoutException(str(exception_message))
				return default
			finally:
				signal.signal(signal.SIGALRM, old_handler)

			signal.alarm(0)
			return retval
		return f2
	return __timeout_function



# Unittests ###################################################################
if __name__ == '__main__':
	import time

	SLEEP_TIME = 5
	WAIT_TIME  = 1

	print "Testing .."

	@timeout(WAIT_TIME, None)
	def sleep():
		time.sleep(SLEEP_TIME)

	@timeout(WAIT_TIME, "timeouted")
	def sleep2():
		time.sleep(SLEEP_TIME)

	@timeout(WAIT_TIME, "", "Timeouted!")
	def sleep3():
		time.sleep(SLEEP_TIME)


	ts = time.time()
	assert sleep() is None
	te = time.time()

	assert int(te - ts) == WAIT_TIME, "Timeout takes too long!"
	assert sleep2() == "timeouted", "Timeout doesn't return proper defaults!"

	try:
		sleep3()
		raise AssertionError("Timeout doesn't raise proper exception!")
	except TimeoutException, e:
		assert e.value == "Timeouted!"

	print "Everything is working as expected."
