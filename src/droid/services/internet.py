from droid.base import Base
from .service import Service


@Base.service(alias='internet-service', autostart='off')
class InternetService(Service):
    def declare(self):
        pass

    #
    def start(self):
        return
