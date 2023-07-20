import subprocess


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

	def __init__(self):
		pass

	def query(self, cmd :list):
		print(self.handlers)
		if cmd[0] not in self.handlers:
			raise RuntimeError(f'Handler for {cmd} not registered!')
		if (args := tuple(cmd[1:])) and args not in self.handlers[cmd[0]]['args']:
			raise RuntimeError(f'Invalid arguments for {cmd[0]} : {args}')
		return self.handlers[cmd[0]]['handler'](' '.join(cmd))

# -- start --
@Termux.arg()
@Termux.arg('-h')
def termux_audio_info(cmd :str):
	"""Get information about audio capabilities."""
	return cmd
	# task = subprocess.run('termux-audio-info', capture_output=True)
	# return task.stdout.strip(b'\n')
