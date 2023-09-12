from abc import ABC, abstractmethod
from contextlib import contextmanager


class Service(ABC):
    def __init__(self, core):
        # -- unpack core dict
        for k, v in core.items():
            setattr(self, k, v)
        # -- initialize
        self.logger = self.core.logger
        self.declare()
        with self.ServiceSession():
            try:
                self.start()
            except Exception:
                self.logger.exception('what?')

    #
    @contextmanager
    def ServiceSession(self):
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
