from droid.tool.sensors import Sensor
from contextlib import contextmanager
from threading import Lock, Thread
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
        self.sensor = Sensor(self.terminate)
        signal.signal(signal.SIGINT, self.shutdown)
        return self.on('droid.SHUTDOWN', self.shutdown)
    # --
    @contextmanager
    def session(self):
        logger.debug('Schedulling a new session.')
        logger.debug(self.sensor.register['filters'])
        with self.sensor.on('held,shake') as filt:
            with self.sensor.sense('accelerometer', 300) as s1:
                with self.sensor.sense('accelerometer', 300) as s2:
                    held, shake = filt
                    def reader(who):
                        for what in who:
                            if isinstance(what, str):
                                logger.debug(what)
                    t1 = Thread(target=reader, args=(held(s1),))
                    t2 = Thread(target=reader, args=(shake(s2),))
                    t1.start(), t2.start(), t1.join(), t2.join()
        yield
        logger.debug('Session ended.')
        self.emit('droid.SHUTDOWN')
    # -- main loop
    def run(self):
        while not self.terminate.is_set():
            with self.session():
                pass

