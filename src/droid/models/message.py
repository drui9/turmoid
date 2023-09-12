from . import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Boolean, String, DateTime, ForeignKey


class Message(Base):
    __tablename__ = 'message'
    #
    id = Column(Integer, primary_key=True, nullable=False)
    type = Column(String(12), nullable=False) # inbox, sent
    read = Column(Boolean, default=False) # True, False
    sender = Column(String(21), nullable=False)
    time = Column(DateTime, nullable=False)
    body = Column(String(2048), nullable=False) # todo: check if empty message =possible
    contact_id = Column(ForeignKey('contact.id'))
    contact = relationship('Contact', uselist=False, back_populates='messages')

    def __repr__(self):
        if self.contact:
            return f'Message({self.contact}, is_read={self.read})'
        return f'Message({self.sender}, is_read={self.read})'
