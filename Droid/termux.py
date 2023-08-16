import os
import invoke
import loguru
import threading
from time import perf_counter
from fabric import Connection


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

	def query(self, cmd :list):
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
			st = perf_counter()
			ret = self.handlers[cmd[0]]['handler'](' '.join(cmd))
			return f'Latency: {perf_counter() - st:.2f}s' , ret
		except Exception as e:
			if not self.connected.is_set():
				e.add_note('Remote end disconnected!')
			return False, e

	def execute(self, cmd):
		"""Execute cmd through termux"""
		try:
			self.logger.debug(f'Executing: {cmd}')
			cmd = ['timeout 5', cmd]
			return self.connection.run(' '.join(cmd), hide=True).stdout
		except invoke.exceptions.UnexpectedExit:
			raise RuntimeError('Invoke: UnexpectedExit')

	def ready(self):
		"""Return True if termux communication is ready"""
		return self.connected.is_set()

	def __init__(self):
		"""Initialize termux communication"""
		self.connected = threading.Event()
		self.cwd = os.getcwd()
		try:
			self.connection = Connection('_gateway', connect_timeout=5)
			if output := self.execute('pwd'):
				self.cwd = output.strip('\n')
			self.connected.set()
		except Exception as e:
			self.logger.critical(str(e))
