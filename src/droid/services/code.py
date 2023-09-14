from droid.base import Base
from .service import Service

config = {
    'alias': 'code-service',
    'autostart': 'off' # on!=REQUIRED
}


@Base.service(config)
class CodeService(Service):
    def initialize(self):
        print('Code service initialized.')
        return False

    #
    def start(self):
        print('Code started.')
        breakpoint()
