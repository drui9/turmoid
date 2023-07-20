from Droid.termux import Termux
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

engine = create_engine('sqlite:///:memory:')
Base = declarative_base()
termux=Termux('_gateway')

#
from Droid.main import Android
from Droid.models import *
from Droid.utils import *

Base.metadata.create_all(bind=engine)
