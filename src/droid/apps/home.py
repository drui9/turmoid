from droid.apps.app import App
from droid.base import Base


@Base.app(name='blackhole')
class Home(App):
    def start(self):
        self.logger.debug(f'{self.name} started.')
        if self.on('internet-connected'):
            self.logger.debug('Internet connected.')
