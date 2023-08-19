import os
import sys
import hashlib
import threading
import subprocess
from loguru import logger
from Droid.base import Base
from datetime import datetime


class Android(Base):
    def __init__(self):
        super().__init__()
        self.reboot = threading.Event()
        self.logger.info(f'Droid started at: {datetime.now().ctime()}')
        self.dependacy_hash = self.get_file_hash('requirements.txt')
        return

    def get_file_hash(self, fname :str):
        if not os.path.exists(fname):
            raise FileNotFoundError(fname)
        with open(fname, 'rb') as bfile:
            return hashlib.md5(bfile.read()).hexdigest()
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
            self.terminate.wait()
            if self.reboot.is_set():
                self.restart()
        return

    def change_mon(self):
        """Prepares watchdog filesystem watcher"""
        # handlers
        @self.watcher.handle('closed', validator=lambda x: x.src_path[-4:] == '.zip')
        def update_available(path):
            self.update(path)
        # start watcher
        self.watcher.start()
        return

    def shutdown(self, *args):
        """System shutdown"""
        if args:
            self.logger.debug(args)
        self.active.clear()
        self.terminate.set()
        self.watcher.observer.stop()
        self.logger.info('Shutdown requested.')
        self.terminate.wait()
        self.logger.info('Terminated.')

    def restart(self):
        self.logger.info('Rebooting...')
        return os.execv(sys.executable, ['./venv/bin/python'] + sys.argv)

    @logger.catch
    def update(self, package):
        """Unpack package and restart"""
        self.logger.info('Processing update...')
        up = subprocess.run(['make', 'unpack'], capture_output=True)
        if not up.returncode:
            dep_hash = self.get_file_hash('requirements.txt')
            if dep_hash != self.dependacy_hash:
                self.logger.info('Project dependancies changed!')
            self.reboot.set()
            self.shutdown()
        else:
            self.logger.critical(f'Update failed with code: {up.returncode}')
