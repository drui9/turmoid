import os
import sys
import threading
from Droid.base import Base
from datetime import datetime


class Android(Base):
    def __init__(self):
        super().__init__()
        self.reboot = threading.Event()
        self.logger.info(f'Droid started at: {datetime.now().ctime()}')
        return

    def start(self):
        """Authorize admin then start filesystem monitor && scheduler"""
        # start session
        with self.authorize():
            if not self.active.is_set():
                self.logger.critical('Authorization failed!')
                return
            self.change_mon()
            self.schedule_routines()
            if not self.routines:
                self.logger.info('No routines scheduled.')
            else:
                self.logger.info('Routines completed.')
            #
            self.terminate.wait()
            self.shutdown()
        return

    def change_mon(self):
        """Prepares watchdog filesystem watcher"""
        # watch downloads
        directory = 'storage/shared/Download'
        @self.watcher.handle(directory, 'created', validator=lambda x: 'Download' in x.src_path)  # noqa: E501
        def new_download(path):
            self.logger.info(f'New download: {path}')
            self.terminate.set()
        # watch documents
        directory = 'storage/shared/Documents'
        @self.watcher.handle(directory, 'created', validator=lambda x: 'Documents' in x.src_path)  # noqa: E501
        def new_document(path):
            self.logger.info(f'New document: {path}')
            self.terminate.set()
        # start watcher
        self.watcher.start()
        return

    def shutdown(self, *args):
        """System shutdown"""
        if args:
            self.logger.debug(args)
        self.active.clear()
        self.terminate.set()
        self.watcher.stop()
        # shutdown notice
        self.get('termux-vibrate')
        self.logger.info('Shutdown sequence completed.')

    def restart(self):
        self.logger.info('Rebooting...')
        return os.execv(sys.executable, ['./venv/bin/python'] + sys.argv)
