import loguru
from Droid import engine, termux
from sqlalchemy.orm import Session

class Android:
	def __init__(self):
		self.termux = termux
		self.session = Session(bind=engine)
		self.logger = loguru.logger

	def start(self):
		return
