from contextlib import contextmanager
from .sensors import Sensors
from threading import Event
from .tool import Emitter
from loguru import logger
import subprocess as sp

# --
class Droid:
    name = 'main'
    modules = dict()
    handlers = dict()
    # --
    @classmethod
    def arg(cls, args :str|None=None):
        """Register command handler function."""
        def wrapper(fn):
            def wrapped(fn):
                name = fn.__name__.replace('_', '-')
                if not cls.handlers.get(name):
                    cls.handlers.update({name: {'handler': fn, 'args': args}})
                return fn
            return wrapped(fn)
        return wrapper
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
    # --
    def query(self, cmd :list):
        """Validate and execute cmd[0] with cmd[1:] arguments"""
        if cmd[0] not in self.handlers:
            raise RuntimeError(f'Handler for [{cmd}] not registered!')
        for arg in cmd[1:]:
            if arg not in (args := self.handlers[cmd[0]]['args']):
                # if '-' in arg:
                #     prev_index = arg.find('-') - 1
                #     if arg[prev_index] != '\\':
                #         raise RuntimeError(f'Please escape [-] in argument <{arg}> for {cmd[0]}.')
                if '*' not in args:
                    invalid = [i for i in cmd[1:] if i not in args]
                    raise RuntimeError(f'Invalid parameter(s) {invalid} for {cmd[0]}')
        #
        try:
            print(cmd)
            ret = self.exec(cmd, capture_output=True, timeout=10)
            if not ret.returncode:
                return self.handlers[cmd[0]]['handler'](ret.stdout.read())
            raise RuntimeError(f'Exec:{cmd} failed with code: {ret.returncode}')
        except Exception as e:
            return False, e
    # --
    @contextmanager
    def session(self):
        logger.debug('Schedulling a new session.')
        action = 'termux-toast "hello, world!"'
        out = self.query(['termux-notification', '-t', 'Start:Droid', '-c', 'Click me!', '--action', action])
        print(out)
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

    def exec(self, cmd :list|str, capture_output=False, timeout=None):
        cmd = cmd.split(' ') if isinstance(cmd, str) else cmd
        out, err = (sp.PIPE, sp.PIPE) if capture_output else (None, None)
        task = sp.Popen(cmd, stdout=out, stderr=err)
        if timeout != None:
            try:
                task.wait(timeout=timeout)
            except sp.TimeoutExpired:
                task.kill()
            finally:
                task.wait()
        else:
            task.wait()
        return task

    def on(self, *args, **kwargs):
        return self.evt.on(*args, **kwargs)

    def emit(self, *args, **kwargs):
        return self.evt.emit(*args, **kwargs)

    def shutdown(self):
        self.terminate.set()
        return logger.debug('Terminated.')

