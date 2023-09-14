from droid.apps.app import App
from droid.base import Base

config = {
    'name': 'trebble'
}

@Base.app(config)
class Music(App):
    def start(self):
        self.logger.debug(f'{self.name} started.')
        if self.on('internet-connected'):
            self.logger.debug('Internet connected.')
