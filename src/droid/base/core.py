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
            self.logger.debug(event)
        return

    #
    @contextmanager
    def Subscribe(self, event :str):
        storage = queue.Queue()
        with self.subscribers['lock']:
            if event not in self.subscribers['events']:
                data = {
                    event : list()
                }
                self.subscribers['events'].update(data)
            # -- register storage
            self.logger.debug(f'Subscribed to {event}.')
            self.subscribers['events'][event].append(storage)
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
            if ( autostart := service['data'].get('autostart')) == 'on':
                serv = threading.Thread(target=service['enter'], args=(service['data'],))  # noqa: E501
                serv.name = sname
                serv.start()
                service['runtime']['task'] = serv
            elif autostart == 'delay':
                delay = service['data'].get('delay', datetime.timedelta(seconds=12)).total_seconds()  # noqa: E501
                serv = threading.Timer(delay, service['enter'], args=(service['data'],))  # noqa: E501
                serv.name = sname
                serv.start()
                service['runtime']['task'] = serv
        yield
        # -- terminate services
        services = self.services['servlist'].items()
        _= [v['runtime']['terminate'].set() for _, v in services]
        _= [v['runtime']['online'].clear() for _, v in services]
        return [v['runtime']['task'].join() for _, v in services if 'task' in v['runtime']]  # noqa: E501

