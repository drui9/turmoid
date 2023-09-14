from droid.apps.app import App
from droid.base import Base

config = {
    'name': 'home',
}

@Base.app(config)
class Home(App):
    def start(self):
        self.logger.debug(f'{self.name} started.')
        if self.on('internet-connected'):
            self.logger.debug('Internet connected.')
