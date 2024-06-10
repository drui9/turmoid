from droid.tool.schedule import Scheduler
from droid.tool.watchdog import Watchdog
from droid.tool.sensors import Sensor
from contextlib import contextmanager
from threading import Lock
from loguru import logger
from .core import Core
import signal

# --
class Droid(Core):
    def __init__(self):
        super().__init__()
        self.intents = {
            'lock': Lock(),
            'items': list()
        }
        self.dirmon = Watchdog()
        self.scheduler = Scheduler()
        self.sensor = Sensor(self.terminate)
        signal.signal(signal.SIGINT, self.shutdown)
        return self.on('droid.SHUTDOWN', self.shutdown)
    #--
    @contextmanager
    def session(self):
        logger.debug('Schedulling a new session.')
        yield
        logger.debug('Session ended.')
        self.emit('droid.SHUTDOWN')
    #-- main loop
    def run(self):
        while not self.terminate.is_set():
            with self.session():
                pass

