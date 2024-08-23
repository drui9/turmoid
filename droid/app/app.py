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
        self.close = Event()
        self.foreground = Event()
        self.name = self.__class__.__name__
        self.data = coreapp.context['data']['apps'][self.name]['handle']['data']
    # </>

    # <> close trigger
    def quit(self):
        self.foreground.clear()
        return self.close.set()
    # </>

    # <> check close
    @property
    def stop(self):
        if self.app.stop:
            self.quit()
        return self.close.is_set()
    # </>

    # <> force implementation on children
    @abstractmethod
    async def start(self, *args, **kwargs):
        pass
    # </>

