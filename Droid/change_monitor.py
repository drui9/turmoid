from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from typing import Callable
import loguru

#
class Watchdog(FileSystemEventHandler):
    def __init__(self, directory='.'):
        self.observer = Observer()
        self.directory = directory
        self.handlers = dict()
        self.logger = loguru.logger

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
        self.observer.schedule(self, self.directory, recursive=True)
        try:
            self.observer.start()
            self.logger.info(f'Watching filesystem at: [{self.directory}]')
        except OSError as e:
            self.logger.critical(str(e))
            raise
