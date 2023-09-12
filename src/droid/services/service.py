import queue
from abc import ABC, abstractmethod
from contextlib import contextmanager


class Service(ABC):
    def __init__(self, core):
        # -- unpack core dict
        for k, v in core.items():
            setattr(self, k, v)
        # -- initialize
        self.logger = self.core.logger
        self.io = self.core.register
        self.declare()
        if self.autostart == 'on':
            self.launch()
        else:
            while not self.terminate.is_set():
                with self.core.Subscribe(f'{self.alias}-start') as start:
                    while not self.terminate.is_set():
                        try:
                            start.get(timeout=2)
                            break
                        except queue.Empty:
                            continue
                # -- launch service
                self.launch()

    #
    def launch(self):
        with self.ServiceSession():
            try:
                self.start()
            except Exception:
                self.logger.exception('what?')

    #
    def stop(self):
        self.terminate.set()

    #
    def to_stop(self):
        return self.terminate.is_set()

    #
    def expects(self, events: str|list):
        """Register triggers"""
        if isinstance(events, str):
            events = [events]
        with self.io['lock']:
            if self.alias not in self.io['expects']:
                self.io['expects'][self.alias] = list()
            for event in events:
                self.io['expects'][self.alias].append(event)

    #
    def produces(self, events: str|list):
        """Register events raised"""
        if isinstance(events, str):
            events = [events]
        with self.io['lock']:
            if self.alias not in self.io['products']:
                self.io['products'][self.alias] = list()
            for event in events:
                self.io['products'][self.alias].append(event)

    #
    @contextmanager
    def ServiceSession(self):
        if self.autostart == 'off':
            pass
        self.core.services['servlist'][self.alias]['runtime']['online'].set()
        yield
        self.core.services['servlist'][self.alias]['runtime']['online'].clear()

    # for variable declarations
    @abstractmethod
    def declare():
        pass

    # main app entry
    @abstractmethod
    def start():
        pass
