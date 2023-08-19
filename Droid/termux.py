import os
import loguru
import subprocess
from time import perf_counter
from Droid.errors import TermuxAPIError


class Termux:
	handlers = dict()
	logger = loguru.logger
	#
	@classmethod
	def arg(cls, args :str=None):
		"""Register command handler function."""
		def wrapper(fn):
			def wrapped(fn):
				name = fn.__name__.replace('_', '-')
				if not cls.handlers.get(name):
					cls.handlers.update({name: {'handler': fn, 'args': args}})
				return fn
			return wrapped(fn)
		return wrapper

	def query(self, cmd :list, cache=False):
		"""Validate and execute cmd[0] with cmd[1:] arguments"""
		if cmd[0] not in self.handlers:
			raise RuntimeError(f'Handler for {cmd} not registered!')
		for arg in cmd[1:]:
			if arg not in (args := self.handlers[cmd[0]]['args']):
				if '-' in arg:
					prev_index = arg.find('-') - 1
					if arg[prev_index] != '\\':
						options = [i for i in cmd[1:] if i not in args]
						raise RuntimeError(f'Invalid options {options} for {cmd[0]}')
				if '*' not in args:
					invalid = [i for i in cmd[1:] if i not in args]
					raise RuntimeError(f'Invalid parameter(s) {invalid} for {cmd[0]}')
		#
		try:
			if cache:
				ret = self.cache.get(cmd[0]) or self.execute(cmd)
			else:
				st = perf_counter()
				ret = self.execute(cmd)
				final_ = perf_counter()
			# cache
			if cache and cmd[0] not in self.cache:
				if isinstance(ret, str):
					self.cache.update({cmd[0], ret})
					self.logger.debug('todo: save to cache.')
					# todo: save cache
			#
			final_ = f'{cmd[0]} latency: {final_ - st:.2f}sec'
			return final_, self.handlers[cmd[0]]['handler'](ret)
		except Exception as e:
			self.logger.exception(e)
			return False, e

	def execute(self, cmd :list, shell=False):
		"""Execute cmd through termux"""
		self.logger.debug(cmd)
		task = subprocess.run(cmd, shell=shell, capture_output=True)
		if not task.returncode:
			try:
				return task.stdout.decode('utf8')
			except UnicodeDecodeError:
				pass
			return task.stdout
		else:
			msg = f'{task.returncode} : {cmd[0]}'
			raise TermuxAPIError(msg)

	def __init__(self):
		"""Initialize termux communication"""
		self.cwd = os.getcwd()
		self.cache = dict()
		# todo: load cache
		return
