from contextlib import contextmanager
from .sensors import Sensors
from threading import Event
from .tool import Emitter
from loguru import logger
# --
from .sensors.listeners import (
    putdown,
    picked,
    shake
)

# --
class Droid:
    def __init__(self):
        self.evt = Emitter()
        self.sence = Sensors()
        self.terminate = Event()
        return self.sence.evt.child(self)

    @contextmanager
    def session(self):
        logger.debug('Schedulling a new session.')
        event = shake()
        print(event)
        yield
        logger.debug('Session closed.')
        self.evt.emit('shutdown')

    def run(self):
        self.evt.on('shutdown', self.shutdown)
        while not self.terminate.is_set():
            with self.session():
                logger.debug('Session running...')

    def shutdown(self):
        self.terminate.set()

