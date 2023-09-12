from sqlalchemy.orm import declarative_base
#
Base = declarative_base()
from .calls import Call  # noqa: F401, E402
from .contact import Contact # noqa: F401, E402
from .android import Android # noqa: F401, E402
from .message import Message # noqa: F401, E402
