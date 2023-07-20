import subprocess
from fabric import Connection


class Termux:
	handlers = dict()
	#
	@classmethod
	def arg(cls, *args):
		def wrapper(fn):
			def wrapped(fn):
				name = fn.__name__.replace('_', '-')
				if not (this := cls.handlers.get(name)):
					cls.handlers.update({name: {'handler': fn, 'args': [args or None]}})
				elif args and args not in this['args']:
					this['args'].append(args)
				return fn
			return wrapped(fn)
		return wrapper

	def query(self, cmd :list):
		if cmd[0] not in self.handlers:
			raise RuntimeError(f'Handler for {cmd} not registered!')
		if (args := tuple(cmd[1:])) and args not in self.handlers[cmd[0]]['args']:
			raise RuntimeError(f'Invalid arguments for {cmd[0]} : {args}')
		return self.handlers[cmd[0]]['handler'](' '.join(cmd))

	def execute(self, cmd):
		return Connection(self.host, connect_timeout=5).run(cmd, hide=True).stdout

	def __init__(self, host :str):
		self.host = host

