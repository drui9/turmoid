import time
import math
import loguru
import threading
from datetime import datetime
from Droid.models import Device
from Droid import engine, Termux
from sqlalchemy.orm import Session
from contextlib import contextmanager
from Droid.change_monitor import Watchdog


class Base:
	routines = dict()
	termux = Termux()
	watcher = Watchdog()
	logger = loguru.logger
	need_fore = threading.Event()
	active = threading.Event()
	foreground = threading.Event()
	terminate = threading.Event()

	# add new routines
	@classmethod
	def routine(cls, interval, **kwargs):
		"""Add a routine to execute at each interval time"""
		"""Execute routine as daemon thread if interval == 0"""
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
		self.speed = 1
		self.user = None
		return

	def get(self, command :str):
		"""A convenience call to self.termux.query for calls without arguments"""
		ok, data = self.termux.query([command])
		if not ok:
			raise data
		self.logger.debug(ok)
		return data

	def get_fore(self, block=True):
		"""Send foreground request."""
		self.need_fore.set()
		if block:
			while not self.terminate.is_set():
				if self.foreground.wait(timeout=6):
					return True
		return self.foreground.wait(0)

	def fingerprint(self):
		"""Authenticate fingerprint in foreground"""
		return True # todo: remove this dev return
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
		"""Register termux device with fingerprint auth for 1st run"""
		session = Session(bind=engine)
		user = self.get('whoami')
		self.logger.info(f'Initializing user: {user}')
		device = session.query(Device).filter_by(user=user).first()
		if not device:
			# -- run authorization
			if not self.fingerprint():
				yield
				return
			# # -- load device info
			device = Device()
			device.user = user
			#
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
		"""Get the least common multiple of List[nums]"""
		gcd = math.gcd(*nums)
		return abs(math.prod(nums)) // gcd

	def get_next(self, start, end, intervals):
		"""Get the index of the upcoming routine handler"""
		if len(intervals) == 1:
			return intervals[0]
		for i in range(start, end):
			for intv in intervals:
				if i % intv == 0:
					return i

	def execute(self, interval):
		"""Execute a function routine and handle errors"""
		for task in self.routines[interval]:
			if self.terminate.is_set():
				return
			if task['fails']: # todo: clear fail count or alert user
				continue
			try:
				self.logger.debug(f'Running({task["handler"].__name__})')
				task['handler']()
				task['last_run'] = datetime.now()
			except Exception as e:
				task['fails'] += 1
				task['reason'] = str(e)
				if task['fails'] == 1:
					e.add_note(f'Task({task["handler"].__name__}')
					if str(e).strip() != '404':
						self.logger.exception(e)
		return

	def schedule_routines(self):
		"""Schedule functions to run at registered intervals"""
		if not self.routines:
			return
		intervals = sorted(self.routines)
		lcm = self.get_lcm(intervals)
		self.logger.info(f'Looping at {lcm}')
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
			time.sleep(timeout / self.speed) # refresh speedup
		self.logger.debug('Scheduler closed.')
		return
