import time
import glob
from droid import Droid
from loguru import logger
from threading import Event
from threading import Lock, Thread

# --
@Droid.module()
class Music:
    app :Droid
    music_dir = '/data/data/com.termux/files/home/storage/music'
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
        self.songs= glob.glob('{}/*.mp3'.format(self.music_dir))
        self.app.on('droid.MUSIC', self.activate)
        self.app.on('droid.SHUTDOWN', self.shutdown)

    def activate(self):
        if not self.context['worker']['lock'].locked():
            if self.app.terminate.is_set(): return
            with self.context['worker']['lock']:
                if not self.context['worker']['handle'] or (not self.context['worker']['handle'].is_alive()):
                    t = Thread(target=self.music)
                    t.name = self.name
                    t.start()
                    self.context['worker']['handle'] = t

    def music(self):
        self.context['active'].set()
        with self.context['worker']['lock']:
            logger.info(self.name)
            # --
            if self.context['on'].is_set():
                self.app.query(['termux-media-player', 'stop'])
                self.context['on'].clear()

    def shutdown(self):
        if self.context['worker']['lock'].locked():
            return self.context['active'].clear()

