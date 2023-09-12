import os
import json
import queue
import secrets
import threading
from droid.base import Base
from .service import Service
from contextlib import contextmanager
from droid.builtin.extras import termux_get


@Base.service(alias='notification-service', autostart='off')
class NotificationService(Service):
    def declare(self):
        self.expects('notification-request')
        self.produces('notification-response')
        #
        basedir = '/data/data/com.termux/files/usr/tmp'
        self.noticename = os.path.join(basedir, secrets.token_hex(8))

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
            while not self.to_stop():
                with open(path) as notice:
                    data = json.load(notice)
                    self.core.internal.put(data)

    #
    def start(self):
        with self.core.Subscribe('notification-request') as notification:
            rec = threading.Thread(target=self.notice_receiver, args=(self.noticename,))
            rec.name = f'FifoReader:{self.noticename}'
            rec.daemon = True
            rec.start()
            while not self.to_stop():
                try:
                    notice = notification.get(timeout=2)
                    args = notice['data']
                except queue.Empty:
                    continue
                #
                out = list()
                for k, v in args.items():
                    if v:
                        if isinstance(v, dict):
                            v = f"echo '{json.dumps(v)}'>{self.noticename}"
                        elif k == '--id':
                            v = str(v)
                        out.append(k)
                        out.append(v)
                    else:
                        if k == '--ongoing':
                            if '--id' not in args:
                                __err = 'Ongoing notifications without an ID are not allowed!'  # noqa: E501
                                self.logger.critical(__err)
                                continue
                        out.append(k)
                #
                with termux_get(['termux-notification', *out]) as proc:
                    proc.wait()
                    out = proc.stdout.read() if proc.stdout else None # noqa: E501
                    if proc.returncode:
                        out = out or f'Subproces command failed: retcode: {proc.returncode}'  # noqa: E501
                        self.logger.critical(out)
                    elif out:
                        self.logger.debug(f'Subprocess says: {out}')
