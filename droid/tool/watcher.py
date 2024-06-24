from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from contextlib import contextmanager
from threading import Lock
from loguru import logger
import queue
import os

# --
class Watchdog(FileSystemEventHandler):
    def __init__(self):
        self.handle = {
            'lock': Lock(),
            'observer': -1,
            'directories': {
                'recursive': dict(),
                'single': dict()
            }
        }
    # --
    @contextmanager
    def watch(self, directory, mode='single'):
        index = 0
        mode = mode.lower()
        with self.handle['lock']:
            if self.handle['observer'] == -1 or \
                    not self.handle['observer'].is_alive():
                self.handle['observer'] = Observer()
                self.handle['observer'].start()
            # --
            if directory not in self.handle['directories'][mode]:
                self.handle['directories'][mode][directory] = dict()
                recursive = True if mode == 'recursive' else False
                logger.debug('Schedulling {}', directory)
                self.handle['observer'].schedule(self, directory, recursive=recursive)
            else:
                index = len(self.handle['directories'][mode][directory])
            self.handle['directories'][mode][directory] |= {index: queue.Queue()}
        yield self.handle['directories'][mode][directory][index]
        with self.handle['lock']:
            self.handle['directories'][mode][directory].pop(index)
            if not self.handle['directories'][mode][directory]:
                self.handle['directories'][mode].pop(directory)
                # -- restart observer
                if self.handle['directories']['recursive'] or \
                        self.handle['directories']['single']:
                    for mode, paths in self.handle['directories'].items():
                        recursive = True if mode == 'recursive' else False
                        for directory in paths:
                            logger.debug('Reschedulling {}', directory)
                            self.handle['observer'].schedule(self, directory,recursive=recursive)
                else:
                    self.handle['observer'].stop()
                    self.handle['observer'].join()
        logger.warning('State: {}', self.handle['observer'].is_alive())
    # --
    def on_any_event(self, event):
        evt = {
            'type': event.event_type,
            'src': event.src_path,
            'dest': event.dest_path,
            'is_dir': event.is_directory,
            'is_synth': event.is_synthetic
        }
        src_path = '/'.join(event.src_path.split('/')[:-1])
        with self.handle['lock']:
            for v in self.handle['directories'].values():
                if src_path in v:
                    for slot in v.values():
                        for dest in slot.values():
                            dest.put(evt)

