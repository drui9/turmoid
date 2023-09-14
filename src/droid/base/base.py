import loguru
import threading
from sqlalchemy import create_engine
from contextlib import contextmanager
from droid.builtin import EventGroup, Watchdog


class Base:
    terminate = threading.Event()
    events = EventGroup(terminate)
    watchdog = Watchdog()
    logger = loguru.logger
    #
    runtime = {
        'core': {
            'database': create_engine('sqlite:///:memory:', echo=False),
            'services': dict(),
            'apps': dict(),
            'locks': dict()
        }
    }

    #
    @classmethod
    @contextmanager
    def get(cls, path :str):
        """Control access to key"""
        with cls.lockey(path) as obj:
            yield obj

    #
    @classmethod
    @contextmanager
    def lockey(cls, path :str, add=False):
        """arrow points locked: unlocked>locked<unlocked>"""
        if path[-1] not in ('>', '<'):
            raise ValueError(f'Missing  trailing lockstate specifier (> or <): {path}')
        if not isinstance(path, str):
            raise ValueError(f'{path}: expected format: unlocked>locked<unlocked>')
        if path[:4] != 'core':
            raise ValueError(f'Path({path}) does not source from [core]. Are you sure?')
        #
        keys = [i for i in path.replace('<', '.').replace('>', '.').split('.') if i]
        locked = list()
        obj = cls.runtime
        for idx, key in enumerate(keys):
            flag = path.split(key)[1][0]
            if key not in obj:
                if not add:
                    raise RuntimeError(f'{key} is undefined in {list(obj.keys())}')
                elif idx + 1 == len(keys): # last index
                    raise RuntimeError('Missing key: {key} source: {path}')
                obj[key] = dict()
                raise NotImplementedError()
            else:
                node = obj[key]
                obj = node
                if flag == '>':
                    continue
                # grab-lock required
                lname ='.'.join(keys[:idx + 1])
                if not (lock := cls.runtime['core']['locks'].get(lname)):
                    lock = cls.runtime['core']['locks'][lname] = threading.Lock()
                lock.acquire()
                locked.append(lock)
        yield obj
        locked.reverse() # fifo
        return [i.release() for i in locked]

    #
    @classmethod
    def app(cls, config):
        def wrapper(theapp):
            with cls.get('core>apps<') as apps:
                if not (enter := apps.get('enter')):
                    enter = apps['enter'] = list()
                enter.append((theapp, config))
        return wrapper

    #
    @classmethod
    def service(cls, config):
        def wrapper(theserv):
            with cls.get('core>services<') as obj:
                if not (enter := obj.get('enter')):
                    enter = obj['enter'] = list()
                enter.append((theserv, config))
        return wrapper

    #
    @classmethod
    @property
    def stopping(cls):
        return cls.terminate.is_set()


    #
    @classmethod
    @property
    def wait(cls):
        return cls.terminate.wait()

    #
    @classmethod
    def stop(cls, *args):
        cls.terminate.set()
        cls.logger.info(cls.runtime['locks'])
        return
