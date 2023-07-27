import loguru
import threading
from fabric import Connection


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
		try:
			return True, self.handlers[cmd[0]]['handler'](' '.join(cmd))
		except Exception:
			if not self.connected.is_set():
				return False, 'Remote end disconnected!'
			return False, None

	def execute(self, cmd):
		try:
			return self.connection.run(cmd, hide=True).stdout
		except Exception:
			if not self.connection.is_connected:
				self.connected.clear()
		return

	def __init__(self, host :str):
		self.connected = threading.Event()
		try:
			self.connection = Connection(host, connect_timeout=5)
			if output := self.execute('pwd'):
				self.cwd = output.strip('\n')
			self.connected.set()
		except Exception as e:
			self.logger.critical(str(e))
