from sqlalchemy import create_engine
engine = create_engine('sqlite:///:memory:')
#
from .models import *  # noqa: F403, E402
from .termux import Termux # noqa: F403, E402, F401
#
from .droid import Android # noqa: F403, E402, F401
droid = Android()
#
from .termcalls import * # noqa: F403, E402
from .commands import * # noqa: F403, E402
from .routines import *  # noqa: F403, E402
