from droid.tool.schedule import Scheduler
from droid.tool.watchdog import Watchdog
from droid.tool.sensors import Sensor
from contextlib import contextmanager
from threading import Thread, Event
from filelock import FileLock
from loguru import logger
from .core import Core
import signal
import queue
import time

# --
class Droid(Core):
    lock = '.turmoid'
    def __init__(self):
        self.config = dict()
        self.dirmon = Watchdog()
        self.scheduler = Scheduler()
        self.sensor = Sensor(self.terminate)
        super().__init__()
        # -- setup termination methods
        signal.signal(signal.SIGINT, self.shutdown)
        return self.on('droid.SHUTDOWN', self.shutdown)

    # <> Run a droid session
    @contextmanager
    def session(self):
        logger.debug('Schedulling a new session.')
        works = [self.run_scheduler, self.collector]
        workers = list()
        for work in works:
            worker = Thread(target=work)
            worker.name = 'scheduler'
            worker.start()
            workers.append(worker)
        yield
        self.emit('droid.SHUTDOWN')
        for worker in workers: worker.join()
        logger.debug('Session ended.')
    # </>
    # <> TCP listener for network events
    def collector(self):
        port = 9798
        logger.debug('Starting network listener on port: {}', port)
        for event in self.listen(port):
            if self.terminate.is_set(): break
            event = event.decode().strip('\n')
            self.emit(event)
    # </>
    # <> Generate dynamic refresh-time, based on battery status
    def refresh_wait(self, suggestion):
        return suggestion * 3
    # </>
    # <> Execute scheduled tasks
    def run_scheduler(self):
        prev = time.time()
        for sleeptime in self.scheduler.schedule(self):
            latency = time.time() - prev
            if latency < 3.0:
                time.sleep(self.refresh_wait(sleeptime))
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
        lock.blocking = False
        with lock:
            with self.session():
                while not self.terminate.is_set():
                    try:
                        evt = self.context['events']['source'].get(timeout=5)
                        event, kwargs = evt[0][0], evt[1]
                        with self.context['events']['lock']:
                            self.context['events']['items'].append((event, time.time()))
                        super().emit(event, **kwargs)
                    except queue.Empty:
                        continue
                    except Exception:
                        logger.exception('what?')
        self.shutdown()
        # </> --end--
