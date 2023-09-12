import signal
from loguru import logger
from datetime import datetime
from droid.apps import *  # noqa: F403
from droid.services import *  # noqa: F403
from droid.base.core import Core  # noqa: F401


def start():
    logger.info(f'Started. {datetime.now().ctime()}')
    signal.signal(signal.SIGINT, Core.stop)
    try:
        Core()
    except Exception:
        logger.exception('what?')
    logger.info(f'Terminated. {datetime.now().ctime()}')
