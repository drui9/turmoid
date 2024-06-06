from loguru import logger
from droid.tool import Emitter
from threading import Thread, Event
from contextlib import contextmanager

# --
class Sensors:
    evt = Emitter()
    register = dict()
    # --
    @classmethod
    def sense(cls, sensor):
        def wrapper(func):
            if sensor not in cls.register:
                cls.register[sensor] = {
                    'readers': list(),
                    'active': Event()
                }
            @contextmanager
            def context(**kwargs):
                # -- add to readers
                activate = False
                cls.register[sensor]['readers'].append(kwargs)
                if len(cls.register[sensor]['readers']) == 1:
                    activate = True
                # --
                if activate:
                    logger.debug('Activating sensor: {}', sensor)
                    cls.register[sensor]['active'].set()
                    args = (sensor, *kwargs, cls.register[sensor])
                    # --
                    t = Thread(target=func, args=args)
                    # t.daemon = True
                    t.start()
                yield
                # -- pop from readers
                cls.register[sensor]['readers'].remove(kwargs)
                if not cls.register[sensor]['readers']:
                    cls.register[sensor]['active'].clear()
                logger.debug('Deactivating sensor: {}', sensor)
            return context
        return wrapper

