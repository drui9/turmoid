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
            'index': 0,
            'listed': None,
            'updated': Event()
        }
    # </>

    # <> session manager
    @contextmanager
    def session(self):
        modpath = self.app.modules['init']['path']
        modules = glob(os.path.join(modpath, '*.py'))
        loader = self.app.modules['init']['loader']
        old, new = loader(modules, self.app)
        self.scroll['listed'] = list(new.keys())
        if old:
            self.log.debug('todo: Check old vs new modules diff')
        # --
        yield
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

    # --<> background: launch foreground task
    @contextmanager
    def background(self, appname):
        def run(appname):
            print(appname)
        try:
            self.state['foreground'].clear()
            worker = Thread(target=run, args=(appname,))
            yield worker
            worker.join()
            # todo: wait for module foreground, else foreground self
        finally:
            self.state['foreground'].set()
    # </>

    # <> start
    def start(self):
        self.state['foreground'].set()
        reset = False
        try:
            while not self.stop:
                with self.session(): # loads modules
                    reset = False
                    while (not self.stop) and (not reset):
                        # -- publish state
                        index = self.scroll['index']
                        appname = self.scroll['listed'][index]
                        print('name:', appname)
                        print('selected:', not self.state['foreground'].is_set())
                        print('index:', index)
                        # -- io
                        cmd = str(input('>> '))
                        if cmd.lower() == 'q':
                            self.quit()
                            break
                        if self.state['foreground'].is_set():
                            match cmd:
                                case 'prev':
                                    self.scroll['index'] = (index - 1) % len(self.scroll['listed'])
                                case 'next':
                                    self.scroll['index'] = (index + 1) % len(self.scroll['listed'])
                                case 'ok':
                                    with self.background(appname) as worker:
                                        worker.daemon = True
                                        worker.start()
                                case 'r':
                                    reset = True
                        else:
                            print('module data')
        finally:
            self.quit()
    # </>

    # <> shutdown
    def quit(self):
        """Terminate application."""
        super().quit()
        self.app.shutdown()
    # </>

