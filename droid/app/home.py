from droid import Dru
from .app import App
import asyncio

# --
@Dru.app(info= 'Standby app')
class Home(App):
    # <> init home app
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    # </>

    # <> start
    async def start(self):
        self.foreground.set()
        while not self.stop:
            await asyncio.sleep(1)
            self.log.debug('{} : {}', self.name, self.foreground.is_set())
    # </>

