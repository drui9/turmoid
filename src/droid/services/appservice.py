import time
import queue
import random
import socket
import threading
import multiprocessing
from droid.base import Base
from .service import Service
from datetime import datetime
from contextlib import contextmanager
from droid.builtin.extras import from_sock, to_sock, termux_get


@Base.service(alias='app-service', autostart='on') # on = REQUIRED
class AppService(Service):
    def declare(self):
        """declare variables"""
        self.ui = { # socket connections
            'new': queue.Queue(),
            'connected': {
                'lock': threading.Lock(),
                'connections': dict()
            },
            'app-runtime': {
                'name': str(),
                'lock': threading.Lock(),
                'online': self.core.events.add('app-runtime')
            }
        }
        self.context = self.ui['connected']['lock']
        self.updating = self.core.events.add('applist-updating')

    #
    def start(self):
        """Start and manage apps"""
        try:
            upd = threading.Thread(target=self.update_manager)
            upd.name = 'UpdateManager'
            upd.start()
            with self.Connections():
                with self.AppManager():
                    self.Session()
        except Exception:
            self.logger.exception('what?')
        finally:
            self.core.terminate.set()

    #
    def update_manager(self):
        """Wait for update event and trigger shutdown"""
        with self.core.Subscribe('update-request') as update:
            while not self.terminate.is_set():
                try:
                    data = update.get(timeout=5)
                    if not (data := data.get('data')):
                        continue
                except queue.Empty:
                    continue
                # send notification of update and act on response
                event = {
                    'event': 'notification-response',
                    'data': {'action': 'update-now'}|data.get('requires', {})
                }
                notif_info = {
                    '-t': 'Update available',
                    '-c': 'Click to update.',
                    '--ongoing': None,
                    '--id': 'update-notice',
                    '--action': event,    #dict|list[dict]
                    '--alert-once': None
                }
                with self.core.Subscribe('notification-response') as update_notice:
                    self.core.internal.put({
                        'event': 'notification-request',
                        'data': notif_info
                    })
                    while not self.to_stop:
                        try:
                            note = update_notice.get(timeout=4)
                        except queue.Empty:
                            continue
                        if note['data'].get('action') == 'update-now':
                            self.post(note|{'event': 'package-manager-request'})
                            #
                            if self.core.events.wait('app-update-ready'):
                                if self.core.events.is_set('droid-update-done'):
                                    self.core.stop()
                                    self.ui['app-runtime']['online'].clear()
                                    return
                            break
                    #

    #
    def Session(self):
        while not self.terminate.is_set():
            time.sleep(random.randint(1,3))
            with self.context:
                if self.core.terminate.is_set():
                    return
                if not self.ui['connected']['connections']:
                    if self.core.events.wait('applist-updating'):
                        self.logger.debug('Applist updating.')
                    continue
                with self.app_notifications() as notices:
                    while not self.updating.is_set():
                        try:
                            notice = notices.get(timeout=2)
                        except queue.Empty:
                            if self.core.terminate.is_set():
                                return
                            continue
                        if data := notice.get('data'):
                            appnotice = data.get('name'), data.get('action'), data.get('timestamp')  # noqa: E501
                            name, action, stamp = appnotice
                            if action != 'app-launch':
                                continue
                            #
                            act = threading.Thread(target=self.app_action, args=(name, stamp))  # noqa: E501
                            act.name = f'{appnotice[0]}-handler'
                            act.start()
                            if not self.core.events.wait('app-runtime'):
                                return
                            self.logger.debug(f'Started app:{name}')
                            break
                # -- show app close notification
                with self.app_close_notice() as notice:
                    while self.ui['app-runtime']['online'].is_set():
                        try:
                            note = notice.get(timeout=2)
                        except queue.Empty:
                            if self.core.terminate.is_set():
                                return
                            continue
                        if data := note.get('data'):
                            appnotice = data.get('name'), data.get('action'), data.get('timestamp')  # noqa: E501
                            if appnotice[1] != 'app-close':
                                continue
                            self.ui['app-runtime']['online'].clear()
                            with self.ui['app-runtime']['lock']:
                                self.logger.debug(f'{appnotice[0]} stopped.')
                                break
                if not self.updating.is_set() and not self.ui['app-runtime']['online'].is_set():  # noqa: E501
                    continue
                elif self.core.events.wait('applist-updating'):
                    self.logger.debug('Applist updating at runtime.')
                    continue

    #
    @contextmanager
    def app_close_notice(self):
        """Show app close notification"""
        if not self.ui['app-runtime']['online'].is_set():
            return
        app = self.ui['app-runtime']['name']
        with self.core.Subscribe('notification-response') as notifier:
            event = {
                'event': 'notification-response',
                'data': {
                    'name': app,
                    'action': 'app-close',
                    'timestamp': time.time() # todo: calculate app uptime
                }
            }
            notice = {
                '-t': f'App::{app}',
                '-c': 'Click to close.',
                '--ongoing': None,
                '--id': app,
                '--action': event,    #dict|list[dict]
                '--alert-once': None
            }
            self.core.internal.put({
                'event': 'notification-request',
                'data': notice
            })
            yield notifier

    #
    def app_action(self, app, _):
        """Execute app action"""
        tm = datetime.now().ctime()
        with self.core.Subscribe('toast-ok') as notein:
            msg = f'{app} started on {tm}.'
            toast = {
                'event': 'toast-request',
                'data': {
                    'id': f'{app}-start-toast',
                    'message': msg
                }
            }
            self.post(toast)
            while not self.terminate.is_set():
                try:
                    note = notein.get(timeout=3)
                    data = note['data']
                except queue.Empty:
                    self.logger.debug('Toast notification timed out!')
                    continue
                if data['id'] == toast['data']['id']:
                    break
        with self.ui['app-runtime']['lock']:
            self.ui['app-runtime']['name'] = app
            self.ui['app-runtime']['online'].set()
            while self.ui['app-runtime']['online'].is_set():
                if self.terminate.is_set():
                    return
                time.sleep(1)
                self.logger.debug(f'{app} running...')
                # todo: 

    #
    @contextmanager
    def app_notifications(self):
        """List loaded applications"""
        with self.core.Subscribe('notification-response') as notices:
            for app in self.ui['connected']['connections']:
                event = {
                    'event': 'notification-response',
                    'data': {
                        'name': app,
                        'action': 'app-launch',
                        'timestamp': time.time()
                    }
                }
                notice = {
                    '-t': f'App::{app}',
                    '-c': 'Click to launch.',
                    '--ongoing': None,
                    '--id': app,
                    '--action': event,    #dict|list[dict]
                    '--alert-once': None
                }
                self.core.internal.put({
                    'event': 'notification-request',
                    'data': notice
                })
            yield notices
            for app in self.ui['connected']['connections']:
                with termux_get(['termux-notification-remove', app]) as proc:
                    proc.wait()

    #
    def app_handshake(self, conn) -> bool:
        """naive receive and validate handshake"""
        try:
            if self.terminate.is_set():
                return
            name = from_sock(conn)['name']
        except KeyError:
            self.logger.debug('Invalid app handshake.')
            return
        return self.app_add(name, conn)

    #
    def app_add(self, name, conn):
        """Add app to app-list"""
        if self.core.terminate.is_set():
            return
        self.logger.debug(f'Installing app: {name}')
        self.updating.set()
        with self.context:
            if prev := self.ui['connected']['connections'].get(name):
                prev.close()
                self.logger.critical(f'Updating app connection: {name}')
            #
            self.ui['connected']['connections'][name] = conn
            self.updating.clear()
        #
        addr = conn.getpeername()
        self.logger.debug(f'{name}@{addr[0]}:{addr[1]} installed.')
        return True

    #
    def app_pop(self, name):
        """Remove app from app-list"""
        self.logger.debug(f'Uninstalling {name}...')
        self.updating.set()
        try:
            with self.context:
                app = self.ui['connected']['connections'].pop(name)
                self.updating.clear()
            #
            self.logger.debug(f'{name} uninstalled.')
            return app
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
        # close app sockets to alert processes
        with self.context:
            disconn = {'event': 'app-terminate', 'data': {'time': time.time()}}
            for _, conn in self.ui['connected']['connections'].items():
                try:
                    if to_sock(conn, disconn):
                        conn.close()
                    conn.close()
                except Exception:
                    pass
        # --clean-up
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
                    if not self.app_handshake(conn):
                        conn.close()
                        continue
                except TimeoutError:
                    continue
                except Exception as e:
                    self.logger.debug(f'App connect failed: {e}')
        connect_manager = threading.Thread(target=conn_manager)
        connect_manager.name = 'ConnectManager'
        connect_manager.start()
        yield
        self.terminate.set()
        connect_manager.join()
        return server.close()
