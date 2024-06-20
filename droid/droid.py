from droid.tool.schedule import Scheduler
from droid.tool.watchdog import Watchdog
from droid.tool.sensors import Sensor
from contextlib import contextmanager
from loguru import logger
from .core import Core
import signal

# --
class Droid(Core):
    def __init__(self):
        super().__init__()
        self.config = None
        self.dirmon = Watchdog()
        self.scheduler = Scheduler()
        self.sensor = Sensor(self.terminate)
        # -- setup termination methods
        signal.signal(signal.SIGINT, self.shutdown)
        return self.on('droid.SHUTDOWN', self.shutdown)
    #--
    @contextmanager
    def session(self):
        logger.debug('Schedulling a new session.')
        yield
        logger.debug('Session ended.')

    #-- main loop
    def run(self):
        with self.session():
            self.emit('droid.MUSIC')
            self.terminate.wait(60)
            self.emit('droid.MUSIC')
        # --end--
        self.emit('droid.SHUTDOWN')

