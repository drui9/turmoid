from droid.tool.schedule import Scheduler
from droid.tool.watcher import Watchdog
from droid.tool.sensors import Sensor
from contextlib import contextmanager
from filelock import FileLock
from loguru import logger
from .core import Core
import asyncio

# --
class Dru(Core):
    lock = '.turmoid'
    def __init__(self):
        self.dirmon = Watchdog()
        self.sensor = Sensor(self)
        self.scheduler = Scheduler()
        self.on('droid.SHUTDOWN', self.shutdown)
        return super().__init__()

    # <> Run a droid session
    @contextmanager
    def session(self):
        try:
            lock = FileLock(self.lock)
            with lock: yield
        finally:
            self.emit('droid.SHUTDOWN')
            logger.debug('Session ended.')
    # </>

    # <> main loop
    async def run(self):
        with self.session():
            loop = list()
            for appname, info in self.context['runtime']['data']['apps'].items():
                args = self, *info['args']
                kwargs = info['kwargs']
                # --
                info['handle']['instance'] = info['handle']['enter'](*args, **kwargs)
                app = info['handle']['instance']
                loop.append(app.start())
                logger.debug('Initialized {}', appname)
            # -- runtime loop
            await asyncio.gather(*loop)
    # </> --end--
