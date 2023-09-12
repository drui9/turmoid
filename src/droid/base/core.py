import random
import queue
import datetime
import threading
from droid.base import Base
from contextlib import contextmanager
from droid.models import Base as db_base


#
class Core(Base):
    def __init__(self):
        self.remote = ('127.0.0.1', random.randint(1001, 3003))
        db_base.metadata.create_all(bind=self.db)
        self.events.set_parent(self)
        # data channels
        self.outgoing = queue.Queue()
        self.incoming = queue.Queue()
        self.internal = queue.Queue()
        self.register = {
            'lock': threading.Lock(),
            'products': dict(),
            'expects': dict()
        }
        self.subscribers = {
            'lock': threading.Lock(),
            'events': dict()
        }
        # app loop
        try:
            with self.Services():
                self.start()
        except Exception as e:
            self.logger.exception(e)

    # -- main entry
    def start(self):
        """Start droid Core and parse events."""
        while not self.terminate.is_set():
            try:
                event = self.internal.get(timeout=3)
            except queue.Empty:
                continue
            self.logger.debug(f'Event received: {event["event"]}')
            with self.subscribers['lock']:
                if event['event'] in self.subscribers['events']:
                    [i.put(event) for i in self.subscribers['events'][event['event']]]
        return

    #
    @contextmanager
    def Subscribe(self, event :str):
        with self.register['lock']:
            found = None
            for serv,products in self.register['products'].items():
                if event in products:
                    found = serv
                    break
            if found: # debug tip: log when not found
                if self.services['servlist'][found]['data']['autostart'] == 'off':
                    if not self.events.is_set(f'{found}-online'):
                        self.internal.put({'event': f'{found}-start'}) # start service
                        while not self.terminate.is_set():
                            if self.events.get(f'{found}-online').wait(timeout=5): # wait for service  # noqa: E501
                                break
                            self.logger.debug(f'Timed out waiting for service: {found}')
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
            if not self.terminate.is_set():
                self.logger.debug(f'Subscribed to {event}.')
        yield storage
        with self.subscribers['lock']:
            if len(self.subscribers['events'][event]) == 1:
                del self.subscribers['events'][event]
            else:
                self.subscribers['events'][event].remove(storage)
            self.logger.debug(f'Unsubscribed from {event}.')

    #
    @contextmanager
    def Services(self):
        for sname, service in self.services['servlist'].items():
            extra = {'core': self, 'terminate': self.events.get(f'{sname}-terminate')}
            service['data'] = service['data'] | extra
            #
            serv = threading.Thread(target=service['enter'], args=(service['data'],))  # noqa: E501
            serv.name = sname
            serv.start()
            service['runtime']['task'] = serv
        yield
        # -- terminate services
        services = self.services['servlist'].items()
        _= [v['runtime']['terminate'].set() for _, v in services]
        _= [v['runtime']['online'].clear() for _, v in services]
        return [v['runtime']['task'].join() for _, v in services if 'task' in v['runtime']]  # noqa: E501

