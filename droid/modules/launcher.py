import time
import glob
from droid import Droid
from loguru import logger
from threading import Event
from threading import Lock, Thread

# --
@Droid.module()
class Launcher:
    app :Droid
    # --
    def __init__(self, spec):
        self.context = {
            'active': Event(),
            'foreground': Event(),
            'worker': {
                'lock': Lock(),
                'handle': None
            }
        }
        self.name = spec['name']
        self.app.on('droid.sensor.PICKED', self.foreground)
        self.app.on('droid.sensor.PUTDOWN', self.background)
        self.app.on('droid.SHUTDOWN', self.shutdown)

    def foreground(self, time):
        logger.debug('Foreground')

    def background(self, time):
        logger.debug('Background')

    def shutdown(self):
        if self.context['worker']['lock'].locked():
            return self.context['active'].clear()

