from contextlib import contextmanager
from droid import Dru
from .app import App
import asyncio

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
        with self.app.listener(self.notice) as note:
            mods = self.app.context['data']['modules']
            for mod in mods:
                md = mods[mod]
                hsh = md['hash']
                nc = f'nc localhost {self.notice}'
                btn1 = ['--button1', 'Start', '--button1-action', f'echo {hsh}-start | {nc}']
                btn2 = ['--button2', 'Stop', '--button2-action', f'echo {hsh}-stop | {nc}']
                # btn3 = ['--button3', 'Send', '--button3-action', 'echo \\$REPLY | termux-toast']
                cnt = ['-c', 'Stopped', *btn1, *btn2]
                args = ['-t', mod.split('/')[-1], '-i', hsh, '--ongoing', '--alert-once', *cnt]
                self.app.query(['termux-notification', *args])
            yield note
            for mod in self.app.context['data']['modules'].values():
                self.app.query(['termux-notification-remove', mod['hash']])
        self.app.shutdown()
    # </>

    # <> react to notice & inputs
    async def reactor(self, sock):
        while not self.stop:
            try:
                conn, addr = sock.accept()
                out = conn.recv(64)
                self.app.toast("{}:{}".format(*addr))
                self.log.debug(out)
                conn.close()
            except TimeoutError:
                pass
    # </>

    # <> start
    async def start(self):
        self.foreground.set()
        with self.session() as note:
            await self.reactor(note)
    # </>

