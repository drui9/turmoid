from . import Base
from sqlalchemy import Column, Integer, String

#
class Android(Base):
	__tablename__ = 'android'
	#
	id = Column(Integer, primary_key=True, autoincrement=True)
	version = Column(String(64), nullable=False)
	tmux_version = Column(String(12), nullable=False)
	manufacturer = Column(String(32), nullable=False)
	model = Column(String(64), nullable=False)
	tmux_user = Column(String(12), nullable=False)

	def __repr__(self):
		return f'Android({self.user}, {self.model}, {self.version})'
