from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from typing import Callable
from loguru import logger

#
class Watchdog(FileSystemEventHandler):
    def __init__(self, directory='.'):
        self.observer = Observer()
        self.directory = directory
        self.handlers = dict()

    def handle(self, event :str, validator : Callable):
        def wrapper(fn):
            if not self.handlers.get(event):
                self.handlers.update({event: list()})
            #
            self.handlers[event].append((validator, fn))
            return None # block external calls
        return wrapper

    def on_any_event(self, event):
        if event.event_type not in self.handlers:
            return
        for validator, handler in self.handlers[event.event_type]:
            if validator(event):
                handler(event.src_path)

    def start(self):
        logger.info(f'Watching for filesystem changes in: [{self.directory}]')
        self.observer.schedule(self, self.directory, recursive=True)
        self.observer.start()
