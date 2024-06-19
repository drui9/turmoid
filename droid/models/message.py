from . import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Boolean, String, DateTime, ForeignKey


class Message(Base):
    __tablename__ = 'message'
    #
    id = Column(Integer, primary_key=True)
    body = Column(String(2048))
    done = Column(Boolean, default=False)
    time = Column(DateTime, nullable=False)
    label = Column(String(12), default='inbox') # inbox, sent
    sender = Column(String(21), nullable=False)
    contact_id = Column(ForeignKey('contact.id'))
    contact = relationship('Contact', uselist=False, back_populates='messages')

    def __repr__(self):
        return f'Message(label:{self.label}, is_read={self.done})'

