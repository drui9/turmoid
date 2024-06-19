from . import Base
from sqlalchemy import Column, Integer, String

#
class Device(Base):
	__tablename__ = 'device'
	#
	id = Column(Integer, primary_key=True)
	ip = Column(String(32), default='127.0.0.1')

	def __repr__(self):
		return f'Device(ip:{self.ip})'

