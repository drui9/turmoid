import asyncio
from abc import ABC, abstractmethod
from contextlib import contextmanager


class Service(ABC):
    def __init__(self, enter):
        # -- unpack core dict
        for k,v in enter.items():
            if k == 'alias': # alias alias
                self.name = v
                continue
            elif k == 'core': # shortcuts
                self.get = v.get
            #
            setattr(self, k, v)
        with self.ServiceSession():
            if not self.online.is_set():
                self.logger.debug(f'start {self.name} failed.')
                return
            try:
                asyncio.run(self.start())
            except Exception:
                self.logger.exception('what?')

    #
    def activate(self):
        pass

    #
    @contextmanager
    def ServiceSession(self):
        self.initialize()
        self.online.set()
        yield
        return self.online.clear()

    #
    def fetch(self, id):
        """Wait for returnval to Event(id=id)"""
        pass

    #
    def post(self, event, target = str()):
        """Post/Broadcast event to core"""
        return self.core.internal.put(event)

    #
    def expects(self, events: str|list):
        """Register triggers"""
        if isinstance(events, str):
            events = [events]
        with self.get(self.core.runtime, 'register') as reg:
            if self.name not in reg['expects']:
                self.core.set(reg['expects'], self.name, list())
            for event in events:
                reg['expects'][self.name].append(event)

    #
    def produces(self, events: str|list):
        """Register events raised"""
        if isinstance(events, str):
            events = [events]
        with self.get(self.core.runtime, 'register') as reg:
            if self.name not in reg['products']:
                self.core.set(reg['products'], self.name, list())
            for event in events:
                reg['products'][self.name].append(event)

    #
    @property
    def stopping(self):
        return not self.online.is_set()

    #
    @property
    def stop(self):
        self.online.set()

    # required:: pre-entry initialization
    @abstractmethod
    def initialize():
        pass

    # required:: main app entry
    @abstractmethod
    def start():
        pass
