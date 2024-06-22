from droid.tool.schedule import Scheduler
from droid.tool.watchdog import Watchdog
from droid.tool.sensors import Sensor
from contextlib import contextmanager
from threading import Thread, Event
from loguru import logger
from .core import Core
import signal
import queue
import time

# --
class Droid(Core):
    def __init__(self):
        super().__init__()
        self.config = dict()
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
        def putdown(stop):
            with self.sensor.on('held') as filters:
                held = filters[0]
                with self.sensor.sense('accelerometer', 1000) as accel:
                    for state in held(accel):
                        if self.terminate.is_set() or stop.is_set():
                            break
                        if isinstance(state, str):
                            self.emit(state)
        stop = Event()
        t = Thread(target=putdown, args=(stop,))
        t.name = 'Session-close-monitor'
        t.start()
        yield
        stop.set()
        t.join()
        self.emit('droid.SHUTDOWN')
        logger.debug('Session ended.')
    #--
    def emit(self, *args, **kwargs):
        return self.context['source'].put((args, kwargs))
    #-- main loop
    def run(self):
        with self.session():
            while not self.terminate.is_set():
                try:
                    evt = self.context['source'].get(timeout=5)
                    event, kwargs = evt[0][0], evt[1] or { 'time': time.time() }
                    logger.debug(event)
                    with self.context['lock']:
                        super().emit(event, **kwargs)
                except queue.Empty:
                    continue
        # --end--
