from Droid.base import Base


class Android(Base):
    def __init__(self):
        super().__init__()

    def start(self):
        # start session
        with self.authorize():
            if not self.active.is_set():
                self.logger.critical('Authorization failed!')
                return
            # monitor changes
            self.change_mon()
            # start scheduler
            self.schedule_routines()
            self.logger.debug('Schedule routines completed.')
            self.terminate.wait()
        return

    def change_mon(self):
        # handlers
        @self.watcher.handle('modified', validator=lambda x: x[-3:] == '.py')
        def script_changed(path):
            self.shutdown()
        # start watcher
        self.watcher.start()

    def shutdown(self, *args):
        if args:
            self.logger.debug(args)
        self.active.clear()
        self.terminate.set()
