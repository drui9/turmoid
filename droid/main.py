from contextlib import contextmanager
from .sensors import Sensors
from threading import Event
from .tool import Emitter
from loguru import logger
import subprocess as sp
import time

# --
class Droid:
    name = 'main'
    modules = dict()
    # --
    @classmethod
    def module(cls):
        def wrapper(module):
            cls.modules[module] = dict()
            return module
        return wrapper
    # --
    def __init__(self):
        self.evt = Emitter()
        self.sence = Sensors()
        self.terminate = Event()
        return self.sence.evt.child(self)

    @contextmanager
    def session(self):
        logger.debug('Schedulling a new session.')
        with self.listen(4040) as nc:
            nc.stdin.write(b'>>')
            nc.stdin.flush()
            print(nc.stdout.readline())
        yield
        logger.debug('Closing session.')
        self.emit('shutdown')

    def run(self):
        self.on('shutdown', self.shutdown)
        while not self.terminate.is_set():
            with self.session():
                logger.debug('Session running...')
        return

    def notify(self, title, content):
        pass

    @contextmanager
    def listen(self, port, once=True):
        cmd = f'nc -l localhost {port}'.split(' ')
        if not once:
            cmd[1] = '-lk'
        line_in, line_out, line_err = (sp.PIPE, sp.PIPE, sp.PIPE)
        task = sp.Popen(cmd, stdin=line_in, stdout=line_out, stderr=line_err)
        yield task
        if task.returncode == None:
            task.kill()
        task.wait()
        return task.returncode

    def exec(self, cmd, capture_output=False, timeout=None):
        out, err = (sp.PIPE, sp.PIPE) if capture_output else (None, None)
        task = sp.Popen(cmd.split(' '), stdout=out, stderr=err)
        if timeout != None:
            try:
                task.wait(timeout=timeout)
            except sp.TimeoutExpired:
                task.kill()
            finally:
                task.wait()
        else:
            task.wait()
        return task.returncode

    def on(self, *args, **kwargs):
        return self.evt.on(*args, **kwargs)

    def emit(self, *args, **kwargs):
        return self.evt.emit(*args, **kwargs)

    def shutdown(self):
        self.terminate.set()
        return logger.debug('Terminated.')

