from abc import ABC, abstractmethod
from threading import Event
from loguru import logger

class App(ABC):
    # <> initialize
    def __init__(self, coreapp, *args, **kwargs):
        self.args = args
        self.log = logger
        self.app = coreapp
        self.kwargs = kwargs
        self.state = {
            'close': Event(),
            'foreground': Event()
        }
        self.name = self.__class__.__name__
        self.data = coreapp.context['data']['apps'][self.name]['handle']['data']
    # </>

    # <> quit app
    def quit(self):
        """Trigger app close"""
        self.state['foreground'].clear()
        return self.state['close'].set()
    # </>

    # <> check close
    @property
    def stop(self):
        """Check if terminate is triggered"""
        if self.app.stop:
            self.quit()
        return self.state['close'].is_set()
    # </>

    # <> force implementation on children
    @abstractmethod
    def start(self, *args, **kwargs):
        """Start app"""
        if self.stop: self.state['close'].clear()
    # </>

