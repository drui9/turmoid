from . import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String


class Contact(Base):
    __tablename__ = 'contact'
    #
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(64), nullable=True)
    number = Column(String(21), unique=True)
    messages = relationship('Message', back_populates='contact')
    calls = relationship('Call', back_populates='contact')

    def __repr__(self):
        return f'Contact(id={self.id}, {self.name or self.number})'
