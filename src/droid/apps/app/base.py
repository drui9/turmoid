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
            while not self.terminate.is_set():
                with self.Connect() as conn:
                    while self.connected.is_set():
                        try:
                            data = from_sock(conn)
                            if not data:
                                raise RuntimeError(f'App::{self.name} disconnected.')
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
        while not self.terminate.is_set():
            try:
                conn = socket.create_connection(self.remote)
                break
            except Exception as e:
                self.logger.debug(f'Waiting to connect to server: {e}')
                time.sleep(random.randint(1,4))
        # handshake
        if to_sock(conn, {'name': self.name}):
            self.conn = conn
            self.connected.set()
        yield conn
        self.connected.clear()
        conn.close()

    #
    @contextmanager
    def Router(self):
        """Route data"""
        incoming = queue.Queue()
        def handler():
            while not self.terminate.is_set():
                try:
                    data = incoming.get(timeout=2)
                except queue.Empty:
                    continue
                self.logger.debug(data)
        handle = threading.Thread(target=handler)
        handle.name = f'{self.name}-router'
        handle.start()
        yield incoming
        self.terminate.set()
        handle.join()

    #
    def to_stop(self):
        return self.events.is_set('terminate')

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
