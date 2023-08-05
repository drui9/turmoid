import time
import math
import threading
from datetime import datetime
from Droid.models import Device
from Droid import engine, Termux
from sqlalchemy.orm import Session
from contextlib import contextmanager


class Base:
	routines = dict()
	termux = Termux()
	logger = Termux.logger
	need_fore = threading.Event()
	active = threading.Event()
	foreground = threading.Event()

	# add new routines
	@classmethod
	def routine(cls, interval):
		"""Add a routine to execute at each interval time"""
		"""Execute routine in daemon thread if interval == 0"""
		def wrapper(fn):
			if not interval:
				work = threading.Thread(target=fn)
				work.name = fn.__name__
				work.daemon = True
				work.start()
				return # Block external calls by not returning function
			elif interval == -1:
				return # Execution disabled for this routine
			#
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

	# -- instance methods ---
	def __init__(self):
		self.speed = 20
		self.user = None
		return

	def get(self, command :str):
		"""A convenience call to self.termux.query for calls without arguments"""
		ok, data = self.termux.query([command])
		if not ok:
			raise data
		return data

	def get_fore(self, block=True):
		self.need_fore.set()
		self.logger.info('Foreground requested.')
		while block:
			if self.foreground.wait(timeout=12):
				return True
		return self.foreground.wait(timeout=2)

	def fingerprint(self):
		return True # dev feature
		#
		self.logger.info('Requesting fingerprint.')
		if self.get_fore():
			cmd = 'termux-fingerprint -t "Authenticate Droid"'
			msg = 'Touch fingerprint sensor to continue.'
			ok, resp = self.termux.query([*cmd.split(' '), '-d', f'"{msg}"'])
			if not ok or (res := resp['auth_result']) != 'AUTH_RESULT_SUCCESS':
				self.logger.critical(f'Fingerprint auth failed: {res}')
				return
			self.logger.info('Fingerprint auth success.')
			return True

	@contextmanager
	def authorize(self):
		session = Session(bind=engine)
		user = self.get('whoami')
		self.logger.info(f'Initializing user: {user}')
		device = session.query(Device).filter_by(user=user).first()
		if not device:
			# -- run authorization
			if not self.fingerprint():
				yield
				return
			# -- load device info
			device = Device()
			device.user = user
			#
			self.logger.info('Getting device info...')
			data = self.get('termux-info')
			#
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
			if task['fails']: # todo: clear fail count or alert user
				continue
			try:
				task['handler']()
				task['last_run'] = datetime.now()
			except Exception as e:
				task['fails'] += 1
				task['reason'] = str(e)
				if task['fails'] == 1:
					self.logger.critical(f'Task({task["handler"].__name__} failed: {str(e)}')  # noqa: E501
		return

	def schedule_routines(self):
		if not self.routines:
			return
		self.active.wait()
		intervals = sorted(self.routines)
		lcm = self.get_lcm(intervals)
		self.logger.debug(f'Schedule looping at LCM: {lcm}.')
		maxim = lcm
		sleeptime = 0
		while self.active.is_set():
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
			time.sleep(timeout / self.speed) # dev speedup
			# todo: remove maxim limit
			if not maxim:
				break
			maxim -= 1
		return
