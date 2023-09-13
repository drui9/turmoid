import threading
import time
import random
import queue
import loguru
import socket
import signal
from abc import ABC, abstractmethod
from contextlib import contextmanager
from droid.builtin.extras import to_sock, from_sock
from droid.builtin.events import EventGroup


class AppBase(ABC):
    logger = loguru.logger
    events = EventGroup()

    # -- start
    def __init__(self, data):
        self.conn = None
        self.remote = data['remote']
        self.events.set_parent(self)
        self.connected = self.events.add('app-connected')
        for k,v in data['data'].items():
            setattr(self, k, v)
        signal.signal(signal.SIGINT, self.stop)
        self.activate()

    #
    def activate(self):
        with self.Router() as incoming:
            while not self.to_stop:
                with self.Connect() as conn:
                    while self.connected.is_set():
                        try:
                            data = from_sock(conn)
                            if not data:
                                self.logger.debug(f'App::{self.name} disconnected.')
                                self.connected.clear()
                                break
                            incoming.put(data)
                        except TimeoutError:
                            continue
                        except Exception as e:
                            self.connected.clear()
                            self.logger.debug(e)
                            break

    #
    @contextmanager
    def Connect(self):
        """Connect to server"""
        self.connected.clear()
        self.logger.debug(f'{self.name} Connecting...')
        while not self.to_stop:
            try:
                conn = socket.create_connection(self.remote)
                break
            except Exception:
                self.logger.debug('Reconnecting...')
                time.sleep(random.randint(1,4))
        # handshake
        if to_sock(conn, {'name': self.name}):
            self.conn = conn
            self.connected.set()
        yield conn
        self.connected.clear()
        conn.close()
        self.terminate.set()

    #
    @contextmanager
    def Router(self):
        """Route data"""
        incoming = queue.Queue()
        def handler():
            while not self.to_stop:
                try:
                    data = incoming.get(timeout=2)
                except queue.Empty:
                    continue
                if evt := data.get('event'):
                    if evt == 'app-terminate':
                        self.stop()
                        continue
                self.logger.debug(data)
        # --start handler
        handle = threading.Thread(target=handler)
        handle.name = f'{self.name}-router'
        handle.start()
        yield incoming
        self.terminate.set()
        handle.join()

    #
    @property
    def to_stop(self):
        return self.terminate.is_set()

    #
    @property
    def socket(self):
        """Return active connection"""
        if self.events.wait('app-connected') and self.conn:
            return self.conn

    #
    def stop(self, *args):
        return self.events.set('terminate')

    #
    @abstractmethod
    def start():
        pass
