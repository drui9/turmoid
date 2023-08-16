from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from typing import Callable
from loguru import logger

#
class Watchdog(FileSystemEventHandler):
    def __init__(self, directory, callback :Callable|None=None):
        self.observer = Observer()
        self.callback, self.directory = callback, directory

    def on_any_event(self, event):
        if '.py' == event.src_path[-3:]:
            if event.event_type in ['closed', 'deleted']:
                if self.callback:
                    self.callback(self.directory, event.event_type)
                logger.info(f'File modified: {event.src_path}')

    def start(self):
        logger.info(f'Watching for changes in: {self.directory}')
        self.observer.schedule(self, self.directory, recursive=True)
        self.observer.start()
