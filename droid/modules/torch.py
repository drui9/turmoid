from droid import Droid
from loguru import logger
from threading import Event
from threading import Lock, Thread

# --
@Droid.module()
class Torch:
    app :Droid
    # --
    def __init__(self, spec):
        self.context = {
            'on': Event(),
            'active': Event(),
            'worker': {
                'lock': Lock(),
                'handle': None
            }
        }
        self.name = spec['name']
        self.app.on('droid.TORCH', self.activate)
        self.app.on('droid.SHUTDOWN', self.shutdown)

    def activate(self):
        if not self.context['worker']['lock'].locked():
            if self.app.terminate.is_set(): return
            with self.context['worker']['lock']:
                if not self.context['worker']['handle'] or (not self.context['worker']['handle'].is_alive()):
                    t = Thread(target=self.torch)
                    t.name = self.name
                    t.start()
                    self.context['worker']['handle'] = t

    def torch(self):
        self.context['active'].set()
        with self.context['worker']['lock']:
            with self.app.sensor.sense('light', 500) as light:
                for value in light:
                    value = value[-1]
                    if value < 50 and (not self.context['on'].is_set()):
                        self.app.query(['termux-torch', 'on'])
                        self.context['on'].set()
                    elif value > 50 and self.context['on'].is_set():
                        self.app.query(['termux-torch', 'off'])
                        self.context['on'].clear()
                    elif not self.context['active'].is_set():
                        break
            # --
            if self.context['on'].is_set():
                self.app.query(['termux-torch', 'off'])
                self.context['on'].clear()

    def shutdown(self):
        if self.context['worker']['lock'].locked():
            return self.context['active'].clear()

