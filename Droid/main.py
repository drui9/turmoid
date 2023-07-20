import loguru
from Droid import termux

class Android:
	def __init__(self):
		self.termux = termux
		self.logger = loguru.logger

	def whoami(self, data):
		self.logger.debug(data)

	def start(self):
		data = termux.query(['termux-audio-info'])
		print(data)
