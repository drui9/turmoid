import os
from Droid.base import Base
from Droid.modified import Watchdog


class Android(Base):
    def __init__(self):
        super().__init__()
        self.watcher = Watchdog(os.getcwd(), self.shutdown)

    def shutdown(self, *args):
        if args:
            self.logger.debug(args)
        self.active.clear()
        self.terminate.set()

    def start(self):
        # ---business logic---
        if not self.termux.ready():
            self.logger.critical("Termux not ready!")
            return
        # start session
        with self.authorize():
            if not self.active.is_set():
                self.logger.critical('Authorization failed!')
                return
            # start watcher
            self.watcher.start()
            self.schedule_routines()
            self.logger.debug('Schedule routines completed.')
            self.terminate.wait()
        return
