import loguru
import threading
from sqlalchemy import create_engine
from droid.builtin import EventGroup, Watchdog


class Base:
    events = EventGroup()
    watchdog = Watchdog()
    logger = loguru.logger
    #
    db = create_engine('sqlite:///:memory:', echo=False)
    services = {
        'lock': threading.Lock(),
        'servlist': dict()
    }
    apps = {
        'applist': dict(),
        'runtime': dict()
    }
    #
    @classmethod
    def app(cls, **kwargs):
        def wrapper(app_module):
            appname = kwargs.get('name') or app_module.__name__
            #
            appdata = {
                appname: {
                    'enter': app_module,
                    'data': kwargs
                }
            }
            cls.apps['applist'].update(appdata)
        return wrapper

    #
    @classmethod
    def service(cls, **kwargs):
        """Add a service. All services are builtin"""
        def wrapper(serv_module):
            sname = kwargs.get('alias') or serv_module.__name__
            #
            with cls.services['lock']:
                cls.services['servlist'][sname] = {
                    'enter': serv_module,
                    'data': kwargs,
                    'runtime': {
                        'online': cls.events.add(f'{sname}-online'),
                        'terminate': cls.events.add(f'{sname}-terminate')
                    }
                }
            return # no return
        return wrapper


    # -- trigger shutdown
    @classmethod
    def stop(cls, *args):
        """Set terminate flag"""
        cls.events.set('terminate')
        return
