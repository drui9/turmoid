import sys
import time
import math
import loguru
import threading
from datetime import datetime
from Droid.models import Device
from Droid import engine, termux
from sqlalchemy.orm import Session
from contextlib import contextmanager


class Android:
	routines = dict()
	logger = loguru.logger
	active = threading.Event()
	# add new routines
	@classmethod
	def routine(cls, interval):
		def wrapper(fn):
			if interval not in cls.routines:
				cls.routines.update({interval: list()})
			# append routine
			routine = {
					'handler': fn,
					'last_run': datetime.now(),
					'fails': 0,
					'reason': None
				}
			cls.routines[interval].append(routine)
			return fn
		return wrapper
	#
	@classmethod
	def get(cls, command :list):
		ok, data = termux.query(command)
		if not ok:
			msg = data or 'Prev command exited with error. Shutting down'
			cls.logger.critical(msg)
			if not cls.active.is_set():
				sys.exit(0)
			cls.active.clear()
		return data
	#
	def __init__(self):
		self.user = None
		return

	@contextmanager
	def authorize(self):
		session = Session(bind=engine)
		user = self.get(['whoami'])
		self.logger.info(f'Initializing user: {user}')
		device = session.query(Device).filter_by(user=user).first()
		if not device:
			# -- run authorization
			# cmd = 'termux-fingerprint -t "Droid"'
			# msg = 'Touch fingerprint sensor to continue.'
			# auth = self.get([*cmd.split(' '), '-d', f'"{msg}"'])
			# if auth['auth_result'] != 'AUTH_RESULT_SUCCESS':
			# 	yield
			# 	return
			# -- load device info
			device = Device()
			device.user = user
			data = self.get(['termux-info'])
			device.version = data['Android version']
			device.termux_version = data['TERMUX_VERSION']
			device.manufacturer = data['Manufacturer']
			device.model = data['Model']
			session.add(device)
			session.commit()
			self.logger.info(f'Device [{device.model}:v{device.version}] registered.')
		#
		self.user = user
		yield self.active.set()
		return

	def get_lcm(self, nums):
		gcd = math.gcd(*nums)
		return abs(math.prod(nums)) // gcd

	def get_next(self, start, end, intervals):
		if len(intervals) == 1:
			return intervals[0]
		for i in range(start, end):
			for intv in intervals:
				if i % intv == 0:
					return i

	def execute(self, interval):
		for task in self.routines[interval]:
			if task['fails']:
				continue
			try:
				task['handler']()
				task['last_run'] = datetime.now()
			except Exception as e:
				task['fails'] += 1
				task['reason'] = str(e)
		return

	def schedule_routines(self):
		intervals = sorted(self.routines)
		lcm = self.get_lcm(intervals)
		maxim = lcm
		sleeptime = 0
		while True:
			if sleeptime % lcm == 0:
				sleeptime = 0
			# do work
			for interval in self.routines:
				if sleeptime % interval == 0:
					self.execute(interval)
			# find timeout
			nextv = self.get_next(sleeptime + 1, lcm + 1, intervals)
			timeout = nextv - sleeptime
			sleeptime += timeout
			time.sleep(timeout)
			#
			if not maxim:
				break
			maxim -= 1
		return

	def start(self):
		self.schedule_routines()
		return
		# ---business logic---
		if not termux.connected.is_set():
			return
		# start session
		with self.authorize():
			if not self.active.is_set():
				self.logger.critical('Authorization failed!')
				return
			self.schedule_routines()
		return
