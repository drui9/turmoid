import queue
from droid.base import Base
from .service import Service
from droid.builtin.extras import termux_get


@Base.service(alias='toast-service', autostart='off')
class ToastNotificationService(Service):
    def declare(self):
        self.expects('toast-request')
        self.produces('toast-ok')

    #
    def start(self):
        """Executes toast notification and send ok if notice had id"""
        with self.core.Subscribe('toast-request') as toast:
            while not self.to_stop():
                try:
                    notice = toast.get(timeout=2)
                    if msg := notice['data'].get('message'):
                        args = ['-g', 'top', '-b', 'white', '-c', 'black', f'{msg}']
                        with termux_get(['termux-toast', *args]) as proc:
                            proc.wait()
                            out = {
                                'event': 'toast-ok',
                                'data': notice['data'] | {'ok': True}
                            }
                            if proc.returncode:
                                out['data']['ok'] = False
                            if notice['data'].get('id'):
                                self.core.incoming.put(out)
                except queue.Empty:
                    continue
            #
