from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

engine = create_engine('sqlite:///:memory:')
Base = declarative_base()

#
from Droid.main import Android
from Droid.models import *

Base.metadata.create_all(bind=engine)
