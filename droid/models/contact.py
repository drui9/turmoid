from . import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String


class Contact(Base):
    __tablename__ = 'contact'
    #
    id = Column(Integer, primary_key=True)
    name = Column(String(64), default='Unknown')
    phone_number = Column(String(21), unique=True)
    calls = relationship('Call', back_populates='contact')
    messages = relationship('Message', back_populates='contact')

    def __repr__(self):
        return f'Contact(id={self.id}, {self.name})'

