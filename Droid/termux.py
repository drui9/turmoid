import threading
import subprocess
from Droid import engine
from fabric import Connection
from Droid.models import Resource
from sqlalchemy.orm import Session
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

	def query(self, cmd :list, timeout = 0):
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
		#
		task = threading.Thread(target=self.handlers[cmd[0]]['handler'], args=(' '.join(cmd),))
		task.name = cmd[0]
		task.daemon = True
		task.start()
		if timeout:
			pass
		return

	def execute(self, cmd):
		resources = self.session.query(Resource).all()
		if 'localhost' in self.host:
			t = subprocess.run(cmd, shell=True, capture_output=True)
			t.check_returncode()
			return t.stdout.decode()
		# remote execution
		try:
			return self.connection.run(cmd, hide=True).stdout
		except UnexpectedExit:
			return 'Command exited with error!'

	def __init__(self, host :str):
		self.host = host
		self.session = Session(bind=engine)
		if 'localhost' in self.host:
			self.connection = None
		else:
			self.connection = Connection(self.host, connect_timeout=5)
		self.cwd = self.execute('pwd').strip('\n')

