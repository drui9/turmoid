from droid.base import Base
from .service import Service

config = {
    'alias': 'introspection-service',
    'autostart': 'on' # on=REQUIRED
}


@Base.service(config)
class IntrospectionService(Service):
    def initialize(self):
        print('Introspector initialized.')
        return True

    #
    async def start(self):
        print('Introspector started.')
