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
        logger.debug('Schedulling a new session.')
        ok, _ = self.query(['termux-notification', '-i', str(nid), '--ongoing', '-t', 'turmoid', '-c', 'Running'])
        logger.debug('Turmoid notice: <{}>', ok)
        works = [self.run_scheduler, self.collector]
        workers = list()
        for work in works:
            worker = Thread(target=work)
            worker.name = 'scheduler'
            worker.start()
            workers.append(worker)
        yield
        self.emit('droid.SHUTDOWN')
        self.query(['termux-notification-remove', str(nid)])
        for worker in workers: worker.join()
        logger.debug(self.context['runtime']['contexts'])
        logger.debug('Session ended.')
    # </>
    # <> TCP listener for network events
    def collector(self):
        logger.debug('Starting network listener on port: {}', self.port)
        for event in self.listen(self.port):
            if self.terminate.is_set(): break
            event = event.decode().strip('\n')
            self.emit(event)
    # </>
    # <> Generate dynamic refresh-time, based on battery status
    def refresh_wait(self, suggestion, latency):
        logger.debug('Latency: {}', latency)
        return time.sleep(suggestion)
    # </>
    # <> Execute scheduled tasks
    def run_scheduler(self):
        prev = time.time()
        for sleeptime in self.scheduler.schedule(self):
            latency = time.time() - prev
            self.refresh_wait(sleeptime, latency)
            if self.terminate.is_set():
                break
            prev = time.time()
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
                self.emit('droid.INIT')
                while not self.terminate.is_set():
                    try:
                        evt = self.context['events']['source'].get(timeout=5)
                        event, kwargs = evt[0][0], evt[1] | {'app': self}
                        with self.context['events']['lock']:
                            self.context['events']['items'].append((event, time.time()))
                        super().emit(event, **kwargs)
                    except queue.Empty:
                        continue
                    except Exception:
                        logger.exception('what?')
        # </> --end--
