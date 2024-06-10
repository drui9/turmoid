from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from contextlib import contextmanager
from threading import Lock
from loguru import logger
import os

#
class Watchdog(FileSystemEventHandler):
    def __init__(self):
        self.lock = Lock()
        self.directories = {
            'recursive': list(),
            'single': list()
        }
        self.observer = Observer()
        self.observer.start()
    #--
    def watch(self, directory, recursive):
        if not os.path.exists(directory):
            raise RuntimeError(f'Non-existend directory: {directory}')
        with self.lock:
            path = 'recursive' if recursive else 'single'
            self.directories[path].append(directory)
            if not self.observer.is_alive():
                try:
                    self.observer.start()
                except Exception:
                    self.observer = Observer()
                    self.observer.start()
            for path, directories in self.directories.items():
                recursive = True if path == 'recursive' else False
                for directory in directories:
                    self.observer.schedule(self, directory, recursive=recursive)
    #--
    def on_any_event(self, event):
        logger.debug('{}:{}', event, event.event_type)
    #--
    def stop(self):
        self.observer.stop()

