from . import Base
from datetime import timedelta
from sqlalchemy.orm import relationship
from sqlalchemy import Interval, Column, String, DateTime, ForeignKey


class Call(Base):
    __tablename__ = 'call'
    #
    id = Column(DateTime, primary_key=True, nullable=False)
    type = Column(String(12), nullable=False) # INCOMING, MISSED, OUTGOING
    duration = Column(Interval, default=timedelta(0))
    number = Column(String(21),  nullable=False)
    contact_id = Column(ForeignKey('contact.id'))
    contact = relationship('Contact', uselist=False, back_populates='call_logs')

    def __repr__(self):
        if self.contact:
            return f'Call({self.contact}, duration: {self.duration})'
        return f'Call({self.number}, duration: {self.duration})'
