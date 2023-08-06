from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

engine = create_engine('sqlite:///:memory:')
Base = declarative_base()
#
from .models import *  # noqa: F403, E402
Base.metadata.create_all(bind=engine)
#
from .termux import Termux # noqa: F403, E402, F401
#
from .droid import Android # noqa: F403, E402, F401
droid = Android()
#
from .termcalls import * # noqa: F403, E402
from .commands import * # noqa: F403, E402
from .routines import *  # noqa: F403, E402
