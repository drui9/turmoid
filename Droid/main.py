import loguru
from Droid.termux import Termux

class Android:
	def __init__(self):
		self.termux=Termux()
		self.logger = loguru.logger

	def whoami(self, data):
		self.logger.debug(data)

	def start(self):
		data = self.termux.query(['termux-audio-info'])
		print(data)
