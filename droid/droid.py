from droid.tool.schedule import Scheduler
from droid.tool.watcher import Watchdog
from droid.tool.sensors import Sensor
from contextlib import contextmanager
from filelock import FileLock
from threading import Thread
from loguru import logger
from .core import Core
import signal
import queue
import time

# --
class Droid(Core):
    port = -1
    lock = '.turmoid'
    def __init__(self):
        self.config = dict()
        self.notices = list()
        self.dirmon = Watchdog()
        self.scheduler = Scheduler()
        self.sensor = Sensor(self.terminate)
        # -- setup termination methods
        self.on('droid.SHUTDOWN', self.shutdown)
        signal.signal(signal.SIGINT, self.shutdown)
        return super().__init__()

    # <> Run a droid session
    @contextmanager
    def session(self):
        nid = 2024
        self.notices.append(str(nid))
        logger.debug('Schedulling a new session.')
        ok, _ = self.query(['termux-notification', '-i', str(nid), '--ongoing', '-t', 'turmoid', '-c', 'Running'])
        logger.debug('Turmoid notice: <{}>', ok)
        worker = Thread(target=self.network_emitter)
        worker.name = self.network_emitter.__name__
        yield worker.start()
        for notice_id in self.notices:
            self.query(['termux-notification-remove', str(notice_id)])
        self.emit('droid.SHUTDOWN')
        worker.join()
        logger.debug('Session ended.')
    # </>
    # <> TCP listener for network events
    def network_emitter(self):
        logger.debug('Starting network listener on port: {}', self.port)
        for event in self.listen(self.port):
            event = event.decode().strip('\n')
            self.emit(event)
    # </>
    # <> Emit events
    def emit(self, *args, **kwargs):
        return self.context['events']['source'].put((args, kwargs))
    # </>
    # <> main loop
    def run(self):
        lock = FileLock(self.lock)
        with lock:
            with self.session():
                self.emit('droid.INIT', app=self)
                while not self.terminate.is_set():
                    try:
                        evt = self.context['events']['source'].get(timeout=5)
                        event, kwargs = evt[0][0], evt[1]
                        with self.context['events']['lock']:
                            self.context['events']['items'].append((event, time.time()))
                        try:
                            with self.context['app']['lock']:
                                for name, app in self.context['app']['data'].items():
                                    if event == app['on'] and (not app['active'].is_set()):
                                        t = Thread(target=app['app'], args=(name, self))
                                        t.daemon = True
                                        t.name = name
                                        t.start()
                        except Exception:
                            logger.exception('what?')
                        logger.info(event)
                        super().emit(event, **kwargs)
                    except queue.Empty:
                        continue
                    except Exception:
                        logger.exception('what?')
        # </> --end--
