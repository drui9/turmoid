from droid import Dru
from .app import App
import asyncio

# --
@Dru.app(info= 'Torch app with automatic actions')
class Torch(App):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    async def start(self):
        self.close.clear()
        while not self.stop:
            await asyncio.sleep(1)
            self.log.debug('{} : {}', self.name, self.foreground.is_set())

