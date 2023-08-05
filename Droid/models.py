from Droid import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float, DateTime


class Contact(Base):
	__tablename__ = 'contact'
	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(32))
	number = Column(String(15))

class Message(Base):
	__tablename__ = 'message'
	id = Column(Integer, primary_key=True, nullable=False)
	group = Column(String(24), nullable=False)
	read = Column(Boolean, default=False)
	time = Column(DateTime, nullable=False)
	body = Column(String(4096), nullable=False)

class Resource(Base):
	__tablename__ = 'resource'

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String, unique=True)
	balance = Column(Integer, default=0)
	last_checked = Column(DateTime, nullable=True)
	owner_id = Column(ForeignKey('Android.id'))
	owner = relationship('Device', back_populates='resources')

class Battery(Base):
	__tablename__ = 'battery'

	id = Column(Integer, primary_key=True, autoincrement=True)
	health = Column(String, nullable=False)
	percentage = Column(Integer, nullable=False)
	plugged = Column(String, nullable=False)
	status = Column(String, nullable=False)
	temperature = Column(Float, nullable=False)
	current = Column(Integer, nullable=False)
	device_id = Column(ForeignKey('Android.id'))
	device = relationship('Device', back_populates='battery')

	def __repr__(self):
		return f'Battery(device={self.device.id}, percent={self.percentage})'

class Device(Base):
	__tablename__ = 'Android'

	id = Column(Integer, primary_key=True, autoincrement=True)
	version = Column(String, nullable=False)
	termux_version = Column(String, nullable=False)
	manufacturer = Column(String, nullable=False)
	model = Column(String, nullable=False)
	user = Column(String, nullable=False)
	admin = Column(String, default="Admin")
	set_admin = Column(Boolean, default=False)
	enable_upgrades = Column(Boolean, default=False)
	battery = relationship('Battery', uselist=False, back_populates='device')
	resources = relationship('Resource', back_populates='owner')

	def __repr__(self):
		return f'Android({self.version}, {self.model}, {self.user})'
