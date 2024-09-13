from droid.tool.schedule import Scheduler
from droid.tool.watcher import Watchdog
from droid.tool.sensors import Sensor
from contextlib import contextmanager
from threading import Thread
from loguru import logger
from .core import Core
from . import toast

# --
class Dru(Core):
    def __init__(self):
        self.toast = toast
        self.dirmon = Watchdog()
        self.sensor = Sensor(self)
        self.scheduler = Scheduler()
        self.on('droid.SHUTDOWN', self.shutdown)
        return super().__init__()

    # <> Run a droid session
    @contextmanager
    def session(self):
        try:
            yield
        finally:
            self.emit('droid.SHUTDOWN')
            logger.debug('Session ended.')
    # </>

    # <> main loop
    async def run(self):
        with self.session():
            enter = None
            for appname, info in self.context['data']['apps'].items():
                args = self, *info['args']
                kwargs = info['kwargs']
                # --
                info['handle']['instance'] = info['handle']['enter'](*args, **kwargs)
                app = info['handle']['instance']
                logger.debug('Initializing {}...', appname)
                if appname == 'Home':
                    enter = app.start
                    continue
            if enter: enter()
    # </> --end--

