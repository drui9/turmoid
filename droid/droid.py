from droid.tool.schedule import Scheduler
from droid.tool.sensors import Sensor
from contextlib import contextmanager
from threading import Lock, Thread
from loguru import logger
from .core import Core
import signal
import time

# --
class Droid(Core):
    def __init__(self):
        super().__init__()
        self.intents = {
            'lock': Lock(),
            'items': list()
        }
        self.scheduler = Scheduler()
        self.sensor = Sensor(self.terminate)
        signal.signal(signal.SIGINT, self.shutdown)
        return self.on('droid.SHUTDOWN', self.shutdown)
    #--
    @Scheduler.add(3)
    def cron(self):
        logger.debug('Crontab')
    #--
    @Scheduler.add(7)
    def cron2(self):
        logger.debug('Crontab2')
    # --
    @contextmanager
    def session(self):
        logger.debug('Schedulling a new session.')
        for sleep in self.scheduler.schedule(self.terminate):
            print(sleep)
            time.sleep(1)
        yield
        logger.debug('Session ended.')
        self.emit('droid.SHUTDOWN')
    # -- main loop
    def run(self):
        while not self.terminate.is_set():
            with self.session():
                pass

