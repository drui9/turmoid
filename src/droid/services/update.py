import os
import ssl
import queue
import socket
import loguru
import threading
from droid.base import Base
from .service import Service
from droid.builtin.extras import to_sock, from_sock


@Base.service(alias='update-service', autostart='on') # on=REQUIRED
class UpdateService(Service):
    def declare(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('0.0.0.0', 9090))
        except OSError:
            self.logger.critical('Another instance is running on port 9090!')
            self.core.terminate.set()
            self.stop()
            return
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_ctx.load_cert_chain(certfile='crypt/certificate.pem', keyfile='crypt/private.key')  # noqa: E501
        self.sock = ssl_ctx.wrap_socket(sock)
        self.sock.settimeout(7)
        self.sock.listen()
        #
        self.expects('package-manager-request')
        self.produces(['update-request'])
        self.updateinfo = {
            'ready': self.core.events.add('app-update-ready'),
            'lock': threading.Lock(),
            'zbytes': bytes(),
            'notice': dict()
        }
        #
        with open('requirements.txt') as depf:
            self.depends = [line.strip('\n') for line in depf.readlines()]
        #
        th = threading.Thread(target=self.packman)
        th.name = 'PackageInstaller'
        th.start()

    #
    @loguru.logger.catch
    def start(self):
        """Wait for package install/uninstall requests"""
        with self.core.Subscribe('package-manager-request') as pack:
            while not self.to_stop:
                try:
                    req = pack.get(timeout=5)
                    if data := req.get('data'):
                        new = data.get('new')
                        old = data.get('old')
                        if self.updator(new, old):
                            self.stop() # shutdown to signal reboot
                            self.updateinfo['ready'].set()
                            return
                except queue.Empty:
                    continue
            #

    #
    def updator(self, new, old):
        """install new, ask to uninstall old"""
        self.logger.info(f'Updating. Size: {len(self.updateinfo["zbytes"])/1024:.1f}kb')  # noqa: E501
        return True

    #
    def packman(self):
        """Wait for program updates via secure ssl"""
        while not self.to_stop:
            try:
                conn, _ = self.sock.accept()
                conn.settimeout(4)
            except TimeoutError:
                continue
            except OSError:
                continue
            if not (data := from_sock(conn)):
                conn.close()
                continue
            #
            time = data['data']['time']
            size = data['data']['size']
            depends = data['data']['requires']
            #
            if to_sock(conn, {'pid': os.getpid()}):
                if zbytes := conn.recv(size):
                    if not to_sock(conn, {'ok': True}):
                        conn.close()
                    #
                    upnotice = {
                        'event': 'update-request',
                        'data': {
                            'time': time
                        }
                    }
                    #
                    if set(self.depends) != set(depends):
                        upnotice['data']['requires'] = {
                            'new': [i for i in depends if i not in self.depends],
                            'old': [i for i in self.depends if i not in depends]
                        }
                    #
                    with self.updateinfo['lock']:
                        self.updateinfo['zbytes'] = zbytes
                        self.updateinfo['notice'] = upnotice
                    self.post(upnotice)
        # -- clean up
        self.sock.close()
