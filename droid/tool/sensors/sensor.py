import queue
import subprocess as sp
from loguru import logger
from contextlib import contextmanager
from droid.tool.emitter import Emitter
from threading import Thread, Event, Lock

# --
class Sensor:
    evt = Emitter()
    terminate :Event
    register = {
        'parser': None,
        'lock': Lock(),
        'changed': Event(),
        'interval': -1,
        'sensors': dict(),
        'filters': dict()
    }
    # --
    @classmethod
    def parser(cls):
        def wrapper(func):
            cls.register['parser'] = func
            return func
        return wrapper
    # --
    @classmethod
    def filter(cls, name :str):
        def wrapper(func):
            if name not in cls.register['filters']:
                cls.register['filters'][name] = dict()
            #--
            cls.register['filters'][name] |= {func.__name__: func}
            return func
        return wrapper
    # --
    @classmethod
    @contextmanager
    def on(cls, filt :str):
        out = list()
        filters = [i.strip() for i in filt.split(',')]
        for filt in filters:
            for name, val in cls.register['filters'].items():
                if filt in val:
                    logger.debug('Adding filter: {} to {}', filt, name)
                    out.append(val[filt])
        if len(out) != len(filters):
            known = [list(i.keys())[-1] for i in cls.register['filters'].values()]
            raise RuntimeError(f'Missing filter in {filters}.\nKnown filters: {", ".join(known)}')
        yield tuple(out)
    # --
    def __init__(self, terminate):
        self.terminate = terminate
        self.runtime = {
            'lock': Lock(),
            'worker': None
        }

    @contextmanager
    def sense(self, name, interval):
        sink = queue.Queue()
        # -- register sink
        with self.register['lock']:
            if self.terminate.is_set():
                return
            self.register['interval'] = interval
            if name not in self.register['sensors']:
                logger.debug('Adding new sensor: {}', name)
                self.register['sensors'][name] = [sink]
                self.register['changed'].set()
            else:
                logger.debug('Adding sensor to read: {}', name)
                self.register['sensors'][name].append(sink)
        # --
        with self.runtime['lock']:
            if self.terminate.is_set():
                return
            if (not self.runtime['worker']) or (not self.runtime['worker'].is_alive()):
                self.runtime['worker'] = Thread(target=self.processor)
                self.runtime['worker'].name = self.processor.__name__
                self.runtime['worker'].start()
        yield self.reader(sink)
        # -- pop sink
        with self.register['lock']:
            self.register['sensors'][name].remove(sink)
            if not self.register['sensors'][name]:
                logger.debug('Removing sensor: {}', name)
                self.register['sensors'].pop(name)
            self.register['changed'].set()
    # --
    def reader(self, source):
        while not self.terminate.is_set():
            try:
                yield source.get(timeout=5)
            except queue.Empty:
                continue
    # --
    def processor(self):
        while not self.terminate.is_set():
            with self.register['lock']:
                self.register['changed'].clear()
                interval = self.register['interval']
                sensors = ','.join(list(self.register['sensors'].keys()))
            # --
            init = f'termux-sensor -c'
            sp.Popen(init.split(' '), stdout=sp.PIPE, stderr=sp.PIPE).wait()
            # --
            cmd = f'termux-sensor -s {sensors} -d {interval}'
            logger.debug(cmd)
            proc = sp.Popen(cmd.split(' '), stdout=sp.PIPE, stderr=sp.PIPE)
            generator = self.register['parser'](proc) or list()
            for value in generator:
                with self.register['lock']:
                    for name, sinks in self.register['sensors'].items():
                        sname = name.upper()
                        if sname not in value: continue
                        for sink in sinks:
                            sink.put(value[sname]['values'])
                if self.register['changed'].is_set() or self.terminate.is_set():
                    proc.kill()
                    proc.wait()
                    break
            # --
            proc.kill()
            proc.wait()

