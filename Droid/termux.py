import subprocess
from fabric import Connection
from invoke.exceptions import UnexpectedExit


class Termux:
	handlers = dict()
	#
	@classmethod
	def arg(cls, args :str=None):
		def wrapper(fn):
			def wrapped(fn):
				name = fn.__name__.replace('_', '-')
				if not (this := cls.handlers.get(name)):
					cls.handlers.update({name: {'handler': fn, 'args': args}})
				return fn
			return wrapped(fn)
		return wrapper

	def query(self, cmd :list):
		if cmd[0] not in self.handlers:
			raise RuntimeError(f'Handler for {cmd} not registered!')
		for arg in cmd[1:]:
			if arg not in (args := self.handlers[cmd[0]]['args']):
				if '-' in arg:
					prev_index = arg.find('-') - 1
					if arg[prev_index] != '\\':
						raise RuntimeError(f'Invalid options {[i for i in cmd[1:] if i not in args]} for {cmd[0]}')
				if '*' not in args:
					raise RuntimeError(f'Invalid parameter(s) {[i for i in cmd[1:] if i not in args]} for {cmd[0]}')
		return self.handlers[cmd[0]]['handler'](' '.join(cmd))

	def execute(self, cmd):
		try:
			return self.connection.run(cmd, hide=True).stdout
		except UnexpectedExit:
			return 'Command exited with error!'

	def __init__(self, host :str):
		self.host = host
		self.connection = Connection(self.host, connect_timeout=5)
		self.cwd = self.execute('pwd').strip('\n')

