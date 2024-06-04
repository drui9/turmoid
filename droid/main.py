from contextlib import contextmanager
from threading import Event
from .tool import Emitter
from loguru import logger
# --
from .sensors.pick import picked
from .sensors.shake import shake

# --
class Droid:
    def __init__(self):
        self.evt = Emitter()
        self.terminate = Event()

    @contextmanager
    def session(self):
        logger.debug('Schedulling a new session.')
        event = shake()
        print(event)
        yield
        logger.debug('Session closed.')

    def run(self):
        while not self.terminate.is_set():
            with self.session():
                logger.debug('Session running...')

