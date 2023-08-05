from Droid.base import Base


class Android(Base):
    def __init__(self):
        super().__init__()

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
            self.schedule_routines()
        return
