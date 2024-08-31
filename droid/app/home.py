from contextlib import contextmanager
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
    # </>

    # <> session manager
    @contextmanager
    def session(self):
        modpath = self.app.modules['init']['path']
        modules = glob(os.path.join(modpath, '*.py'))
        loader = self.app.modules['init']['loader']
        loader(modules, self.app)
        yield
    # </>

    # <> react to notice & inputs
    async def reactor(self):
        with self.app.listener(self.notice, 2) as sock:
            while not self.stop:
                try:
                    conn, addr = sock.accept()
                    out = conn.recv(64)
                    self.app.toast("{}:{}".format(*addr))
                    self.log.debug(out)
                    conn.close()
                except TimeoutError:
                    await asyncio.sleep(0)
    # </>

    # <> start
    async def start(self):
        self.foreground.set()
        try:
            while not self.stop:
                with self.session():
                    print(self.app.modules)
                    self.quit()
        finally:
            self.app.shutdown()
    # </>

