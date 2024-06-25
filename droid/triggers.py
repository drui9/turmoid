from droid.tool.emitter import Emitter
from threading import Thread
from droid import Droid
import asyncio

@Emitter.on('droid.INIT')
class Triggers:
    def __init__(self, app: Droid):
        self.app = app
        self.worker = None
        self.interval = 500
        self.start()

    def start(self):
        if self.worker and self.worker.is_alive():
            return
        self.worker = Thread(target=asyncio.run, args=(self.main(),))
        self.worker.name = 'triggers'
        self.worker.start()

    async def main(self):
        prox = asyncio.create_task(self.proximity())
        shake = asyncio.create_task(self.shake())
        flip = asyncio.create_task(self.flip())
        self.app.emit('droid.STANDBY', app=self.app)
        await asyncio.gather(prox, shake, flip)

    async def proximity(self):
        with self.app.sensor.on('proximal') as pr:
            proximal = pr[-1]
            with self.app.sensor.sense('proximity', self.interval) as prox:
                for data in proximal(prox):
                    if isinstance(data, str):
                        self.app.emit(data, self.app)
                    await asyncio.sleep(0)

    async def shake(self):
        with self.app.sensor.on('shake') as sk:
            shake = sk[-1]
            with self.app.sensor.sense('accelerometer', self.interval) as shk:
                for data in shake(shk):
                    if isinstance(data, str):
                        self.app.emit(data, self.app)
                    await asyncio.sleep(0)

    async def flip(self):
        with self.app.sensor.on('flipped') as fl:
            flip = fl[-1]
            with self.app.sensor.sense('accelerometer', self.interval) as accel:
                for data in flip(accel):
                    if isinstance(data, str):
                        self.app.emit(data, self.app)
                    await asyncio.sleep(0)

