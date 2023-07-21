from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

engine = create_engine('sqlite:///:memory:')
Base = declarative_base()
#
from Droid.models import *
Base.metadata.create_all(bind=engine)
#
from Droid.termux import Termux
termux = Termux('_gateway')
#
from Droid.main import Android
from Droid.utils import *
from Droid.extras import *
