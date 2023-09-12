import queue
from droid.base import Base
from .service import Service
from droid.builtin.extras import termux_get


@Base.service(alias='notification-service', autostart='off')
class NotificationService(Service):
    def declare(self):
        self.expects('notification-request')
        self.produces('notification-response')

    #
    def start(self):
        with self.core.Subscribe('notification-request') as notification:
            while not self.terminate.is_set():
                try:
                    notice = notification.get(timeout=2)
                    args = notice['data']
                except queue.Empty:
                    continue
                self.logger.debug(args)
