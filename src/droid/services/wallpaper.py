import os
from droid.base import Base
from .service import Service


@Base.service(alias='wallpaper-service', autostart='on') # on!=REQUIRED
class WallpaperService(Service):
    def declare(self):
        photodir = '/data/data/com.termux/files/home/storage/pictures/Wallpapers'
        pics = [f for f in os.listdir(photodir)]
        self.logger.debug(pics)

    #
    def start(self):
        self.logger.critical('wallpaper-service')
