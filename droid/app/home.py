from contextlib import contextmanager
from threading import Event, Thread
from glob import glob
from droid import Dru
from .app import App
import asyncio
import os

# --
@Dru.app(info= 'Standby app')
class Home(App):
    # <> init home app
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.notice = 4040
        self.scroll = {
            'selected': False,
            'data': {
                'index': 0,
                'listed': None,
                'updated': Event()
            }
        }
    # </>

    # <> session manager
    @contextmanager
    def session(self):
        modpath = self.app.modules['init']['path']
        modules = glob(os.path.join(modpath, '*.py'))
        loader = self.app.modules['init']['loader']
        yield loader(modules, self.app)
    # </>

    # <> react to notice & inputs
    async def reactor(self):
        with self.app.listener(self.notice, 2) as sock:
            self.log.debug('Reactor<{}>', self.notice)
            while not self.stop:
                try:
                    conn, addr = sock.accept()
                    out = conn.recv(64)
                    self.app.toast("{}:{}".format(*addr))
                    self.log.debug(out)
                    conn.close()
                except TimeoutError:
                    await asyncio.sleep(1)
    # </>

    # <> start
    def start(self):
        self.state['foreground'].set()
        while not self.stop:
            with self.session():
                self.log.debug(self.scroll)
                break
    # </>

    # <> shutdown
    def quit(self):
        super().quit()
        self.app.shutdown()
    # </>

