"""
Used at: droid.droid.DroidCore
"""
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from typing import Callable
import os

#
class Watchdog(FileSystemEventHandler):
    def __init__(self):
        self.observer = Observer()
        self.handlers = dict()
        self.directories = list()
        #
        for directory in self.directories:
            self.observer.schedule(self, directory, recursive=True)
        # deploy observer
        try:
            self.observer.start()
        except Exception:
            raise

    def handle(self, directory, event :str, validator : Callable):
        def wrapper(fn):
            if not os.path.exists(directory):
                raise RuntimeError(f'File: {directory} does not exist!')
            # create empty handlers list
            if not self.handlers.get(event):
                self.handlers.update({event: list()})
            # append validator and handler to handlers
            self.handlers[event].append((validator, fn))
            self.directories.append(directory)
            # if already running, add to schedule
            if self.observer.is_alive():
                self.observer.schedule(self, directory, recursive=True)
            return # block external calls
        return wrapper

    def on_any_event(self, event):
        if event.event_type not in self.handlers:
            return
        for validator, handler in self.handlers[event.event_type]:
            if validator(event):
                handler(event.src_path)

    def stop(self):
        self.observer.stop()
