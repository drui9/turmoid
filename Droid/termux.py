import loguru
import threading
import subprocess
from Droid import engine
from fabric import Connection
from Droid.models import Resource
from sqlalchemy.orm import Session
from invoke.exceptions import UnexpectedExit


class Termux:
	handlers = dict()
	logger = loguru.logger
	#
	@classmethod
	def arg(cls, args :str=None):
		def wrapper(fn):
			def wrapped(fn):
				name = fn.__name__.replace('_', '-')
				if not cls.handlers.get(name):
					cls.handlers.update({name: {'handler': fn, 'args': args}})
				return fn
			return wrapped(fn)
		return wrapper

	def query(self, cmd :list, timeout = 0):
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
		return self.handlers[cmd[0]]['handler'](' '.join(cmd))

	def execute(self, cmd):
		if self.connection:
			try: # remote execution
				return self.connection.run(cmd, hide=True).stdout
			except UnexpectedExit:
				return 'Command exited with error!'
		# local execution
		t = subprocess.run(cmd, shell=True, capture_output=True)
		t.check_returncode()
		return t.stdout.decode()

	def __init__(self, host :str):
		self.connected = threading.Event()
		if 'localhost' in host:
			self.connection = None
		else:
			try:
				self.connection = Connection(host, connect_timeout=5)
				self.connected.set()
			except Exception as e:
				self.logger.critical(str(e))
		self.cwd = self.execute('pwd').strip('\n')
