import random
import queue
import threading
from droid.base import Base
from contextlib import contextmanager
from droid.models import Base as db_base

config = {
    #
    'domain': ('127.0.0.1', random.randint(10001, 30003)),

    # data channels
    'incoming': queue.Queue(),
    'outgoing': queue.Queue(),

    # name-table
    'register': {'products': dict(), 'expects': dict()},

    # nodes
    'nodes': dict()
}

#
class Core(Base):
    def __init__(self):
        self.logger.add("logs/droid_{time}.log")
        # -- initializations
        with self.get('core>apps<') as core:
            self.logger.debug(core)
            breakpoint()
            core.update({**config})
        with self.get('core>database<') as db:
            db_base.metadata.create_all(bind=db)
        # app loop
        try:
            with self.Services():
                self.start()
        except Exception as e:
            self.logger.exception(e)

    # -- event router main entry
    def start(self):
        """Start droid Core and parse events."""
        with self.get('core>apps>incoming>') as  incoming:
            while not self.terminate.is_set():
                try:
                    evt = incoming.get(timeout=5)
                except queue.Empty:
                    continue
                self.logger.debug(f'Event dropped: {evt}')
        return

    #
    @contextmanager
    def Subscribe(self, event :str):
        with self.get('core<') as core:
            found = None
            # breakpoint()
            for serv,products in self.register['products'].items():
                if event in products:
                    found = serv
                    break
            if found:
                if self.services['servlist'][found]['data']['autostart'] == 'off':
                    if not self.events.is_set(f'{found}-online'):
                        self.internal.put({'event': f'{found}-start'}) # start service
                        while not self.terminate.is_set():
                            if self.events.get(f'{found}-online').wait(timeout=7): # wait for service  # noqa: E501
                                self.logger.debug(f'{found} is online.')
                                break
                            self.logger.debug(f'Timed out waiting for {found}')
                else:
                    while not self.terminate.is_set():
                        if self.events.get(f'{found}-online').wait(timeout=7): # wait for service  # noqa: E501
                            break
                        self.logger.debug(f'Timed out waiting for {found}')
        #
        storage = queue.Queue()
        with self.subscribers['lock']:
            if event not in self.subscribers['events']:
                data = {
                    event : list()
                }
                self.subscribers['events'].update(data)
            # -- register storage
            self.subscribers['events'][event].append(storage)
        yield storage
        with self.subscribers['lock']:
            if len(self.subscribers['events'][event]) == 1:
                del self.subscribers['events'][event]
            else:
                self.subscribers['events'][event].remove(storage)

    #
    @contextmanager
    def Services(self):
        with self.get('core>database<') as db:
            with self.get('core>services>enter<') as servlist:
                for service in servlist:
                    enter, config = service
                    alias = config.get('alias', enter.__name__)
                    online = self.events.add(f'{alias}-online')
                    extra = {
                        'db': db,
                        'core': self,
                        'online': online,
                        'events': self.events,
                        'logger': self.logger
                    }
                    #
                    self.logger.debug(f'{alias} starting...')
                    th = threading.Thread(target=enter, args=(extra|config,))
                    th.name = alias
                    th.start()
        yield
