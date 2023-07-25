from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

engine = create_engine('sqlite:///:memory:')
Base = declarative_base()
#
from .models import *
Base.metadata.create_all(bind=engine)
#
from .termux import Termux
termux = Termux('_gateway')
#
from .main import Android
from .utils import *
from .extras import *
