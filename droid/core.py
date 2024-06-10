import subprocess as sp
from loguru import logger
from threading import Event
from .tool.emitter import Emitter
from contextlib import contextmanager

# --
class Core:
    evt = Emitter()
    modules = dict() # registered modules
    handlers = dict() # termux calls
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
        self.terminate = Event()
        self.events = dict() # -- hold self.get(...) event objects
        for mod in self.modules:
            mod.app = self # pointer to main activity
            self.modules[mod].update({'name': mod.__name__})
            module = mod(self.modules[mod])
            self.modules[mod]['instance'] = module

    # ---
    def get(self, evt):
        if evt not in self.events:
            self.events[evt] = Event()
        return self.events[evt]

    # --
    def query(self, cmd :list):
        """Validate and execute cmd[0] with cmd[1:] arguments"""
        if cmd[0] not in self.handlers:
            raise RuntimeError(f'Handler for [{cmd}] not registered!')
        for arg in cmd[1:]:
            if arg not in (args := self.handlers[cmd[0]]['args']):
                if '*' not in args:
                    invalid = [i for i in cmd[1:] if i not in args]
                    raise RuntimeError(f'Invalid parameter(s) {invalid} for {cmd[0]}')
        #
        ret = self.exec(cmd, capture_output=True, timeout=10)
        try:
            if not ret.returncode:
                return True, self.handlers[cmd[0]]['handler'](ret.stdout.read())
            raise RuntimeError(f'Exec:{cmd} failed with code: {ret.returncode}')
        except Exception as e:
            e.add_note(ret.stderr.read().decode())
            return False, e

    @contextmanager
    def listen(self, port):
        cmd = f'nc -l localhost {port}'.split(' ')
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

    def shutdown(self, *_):
        self.terminate.set()
        self.emit('droid.TERMINATE')
        return logger.debug('Terminated.')

