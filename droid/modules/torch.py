from droid import Droid
from loguru import logger
from threading import Event
from datetime import datetime

config = {
    'start-time': 19,
    'stop-time': 6
}
# --
@Droid.module()
class Torch:
    app :Droid
    # --
    def __init__(self, spec):
        self.on = Event()
        self.name = spec['name']
        self.app.on('droid.TORCH', self.activate)

    def activate(self):
        if self.on.is_set():
            logger.debug('torch off')
            self.on.clear()
        # tm = datetime.now()
        tm = datetime(year=2024, month=6, day=9, hour=5)
        if tm.hour < 12:
            if tm.hour > config['stop-time']:
                return
        elif tm.hour < config['start-time']:
            return
        logger.debug('torch on')
        self.on.set()

