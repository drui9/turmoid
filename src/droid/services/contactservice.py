from droid.builtin.extras import termux_get
from datetime import datetime
from .service import Service
from droid.base import Base
import queue
import json


@Base.service(alias='contact-service', autostart='off')
class ContactService(Service):
    def refresh(self):
        with termux_get('termux-contact-list') as proc:
            body = list()
            proc.wait()
            while line := proc.stdout.readline():
                body.append(line.strip(b'\n'))
            body = b''.join(body) or b'{}'
            try:
                body = json.loads(body.decode('utf8'))
            except json.decoder.JSONDecodeError:
                self.logger.exception("what?")
                return
            for contact in body:
                payload = {
                    'event': 'contact-info',
                    'data': contact
                }
                self.core.incoming.put(payload)
            # -- log
            self.logger.debug(f'{len(body)} contacts parsed at {datetime.now().ctime()}')  # noqa: E501

    #
    def start(self):
        with self.core.Subscribe('contact-update-request') as update:
            while not self.terminate.is_set():
                try:
                    if update.get(timeout=2):
                        self.refresh()
                except queue.Empty:
                    continue
