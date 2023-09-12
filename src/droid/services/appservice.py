import time
import queue
import socket
import threading
import multiprocessing
from droid.base import Base
from .service import Service
from contextlib import contextmanager
from droid.builtin.extras import from_sock, to_sock

@Base.service(alias='app-service', autostart='on')
class AppService(Service):
    def declare(self):
        """declare variables"""
        self.ui = { # socket connections
            'new': queue.Queue(),
            'connected': {
                'lock': threading.Lock(),
                'connections': dict()
            }
        }
        self.context = self.ui['connected']['lock']
        self.updating = self.core.events.add('applist-updating')

    #
    def start(self):
        """Start and manage apps"""
        try:
            ses = threading.Thread(target=self.Session)
            ses.name = 'AppService::Session'
            ses.start()
            with self.Connections():
                with self.AppManager():
                    while not self.terminate.is_set():
                        try:
                            conn = self.ui['new'].get(timeout=3)
                        except queue.Empty:
                            continue
                        if not self.app_handshake(conn):
                            conn.close()
                    # close sockets on terminate
                    with self.context:
                        [v.close() for _, v in self.ui['connected']['connections'].items()]  # noqa: E501
        except Exception:
            self.logger.exception('what?')
        finally:
            self.core.terminate.set()
            ses.join()
        ses.join()

    #
    def Session(self):
        while not self.terminate.is_set():
            if not self.core.events.wait('applist-updating'):
                break
            self.updating.clear()
            with self.context:
                for app in self.ui['connected']['connections']:
                    self.logger.debug(app)
                    event = {
                        'event': 'app-launch',
                        'data': {
                            'name': app,
                            'timestamp': time.time()
                        }
                    }
                    notice = {
                        '-t': app,
                        '-c': 'Click to launch.',
                        '--on-going': None,
                        '--action': event,    #dict|list[dict]
                    }
                    self.core.internal.put({
                            'event': 'notification-request',
                            'data': notice
                        })
                    # todo: subscribe to notification-response
                    with self.core.Subscribe('notification-response') as resp:
                        while not self.updating.is_set():
                            try:
                                data = resp.get(timeout=2)
                            except queue.Empty:
                                if self.terminate.is_set():
                                    break
                                continue
                            self.logger.debug(data)
                            break

    #
    def app_handshake(self, conn) -> bool:
        """naive receive and validate handshake"""
        try:
            name = from_sock(conn)['name']
        except KeyError:
            self.logger.debug('Invalid app handshake.')
            return
        return self.app_add(name, conn)

    #
    def app_add(self, name, conn):
        """Add app to app-list"""
        self.updating.set()
        with self.context:
            if prev := self.ui['connected']['connections'].get(name):
                prev.close()
                self.logger.critical(f'Updating app connection: {name}')
            self.ui['connected']['connections'][name] = conn
            self.logger.debug(f'Loaded app:{name}')
            # todo: read/write from/to socket & detect disconnect
            return True

    #
    def app_pop(self, name):
        """Remove app from app-list"""
        self.updating.set()
        try:
            with self.context:
                self.logger.debug(f'Ejecting app:{name}')
                return self.ui['connected']['connections'].pop(name)
        except KeyError:
            return

    #
    @contextmanager
    def AppManager(self):
        """Start and restart static apps on termination"""
        def apphandler(appname):
            enter = self.core.apps['applist'][appname]['enter']
            data = self.core.apps['applist'][appname]['data']
            #
            args = {
                'remote': self.core.remote,
                'data': data
            }
            app = multiprocessing.Process(target=enter, args=(args,))
            app.name = appname
            app.start()
            app.join()
            if conn := self.app_pop(appname):
                conn.close()
            return
        #
        handlers = list()
        for app in self.core.apps['applist']:
            th = threading.Thread(target=apphandler, args=(app,))
            th.name = f'apphandler-{app}'
            th.start()
            handlers.append(th)
        yield
        # --clean-up
        self.terminate.set()
        [th.join() for th in handlers]
        self.logger.debug('App manager closed.')
        return self.core.stop()

    #
    @contextmanager
    def Connections(self):
        """Manage socket connections & yield server socket"""
        server = socket.create_server(self.core.remote)
        server.settimeout(4)
        #
        def conn_manager():
            while not self.terminate.is_set():
                try:
                    conn, addr = server.accept()
                    conn.settimeout(4)
                    self.ui['new'].put(conn)
                    self.logger.debug(f'{addr[0]}:{addr[1]} connected.')
                except TimeoutError:
                    continue
                except Exception as e:
                    self.logger.debug(f'App connect failed: {e}')
        connect_manager = threading.Thread(target=conn_manager)
        connect_manager.name = 'ConnectManager'
        connect_manager.start()
        yield
        # -- clean-up --
        self.terminate.set()
        connect_manager.join()
        return server.close()
