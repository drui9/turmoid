import os
import json
import queue
import secrets
import threading
from droid.base import Base
from .service import Service
from contextlib import contextmanager
from droid.builtin.extras import termux_get


@Base.service(alias='notification-service', autostart='off') # on!=REQUIRED
class NotificationService(Service):
    def declare(self):
        self.expects('notification-request')
        self.produces('notification-response')
        #
        self.runtime = {
            'new': queue.Queue(),
            'pending': set()
        }
        basedir = '/data/data/com.termux/files/usr/tmp'
        self.noticename = os.path.join(basedir, secrets.token_hex(8))
        return

    #
    def executor(self):
        """Send notifications and monitor their lifetime"""
        # todo: handle termux-get
        pass

    #
    def notice_receiver(self, path :str):
        """Receive notices"""
        @contextmanager
        def noticefifo():
            if not os.path.exists(path):
                os.mkfifo(path)
            yield
            return os.unlink(path)
        #
        with noticefifo():
            while not self.to_stop:
                with open(path) as notice:
                    out = json.load(notice)
                    if evt := out.get("event"):
                        self.logger.debug(f'Notification: {evt}')
                    else:
                        self.logger.debug('Notification.')
                    self.post(out)

    #
    def start(self):
        with self.core.Subscribe('notification-request') as notification:
            rec = threading.Thread(target=self.notice_receiver, args=(self.noticename,))
            rec.name = f'FifoReader:{self.noticename}'
            rec.daemon = True
            rec.start()
            while not self.to_stop:
                try:
                    notice = notification.get(timeout=2)
                    if not (args := notice.get('data')):
                        continue
                except queue.Empty:
                    continue
                #
                out = list()
                for k, v in args.items():
                    if v:
                        if isinstance(v, dict):
                            v = f"echo '{json.dumps(v)}'>{self.noticename};termux-toast -b black -c white '$_executed'"  # noqa: E501
                        elif k == '--id':
                            v = str(v)
                        out.append(k)
                        out.append(v)
                    else:
                        if k == '--ongoing':
                            if '--id' not in args:
                                out.append(['--id', secrets.token_hex(8)])
                        out.append(k)
                #
                with termux_get(['termux-notification', *out]) as proc:
                    self.logger.debug('Notification sent.')
                    proc.wait()
                    out = proc.stdout.read() if proc.stdout else None # noqa: E501
                    if proc.returncode:
                        out = out or f'Subproces command failed: retcode: {proc.returncode}'  # noqa: E501
                        self.logger.critical(out)
                    elif out:
                        self.logger.debug(f'Subprocess says: {out}')
            #
            self.logger.debug('Notification service exited.')
