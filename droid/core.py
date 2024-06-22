import queue
import socket
import subprocess as sp
from loguru import logger
from threading import Lock
from threading import Event
from .tool.emitter import Emitter
from contextlib import contextmanager

# --
class Core(Emitter):
    context = { # [emit] record
        'lock': Lock(),
        'events': list(),
        'source': queue.Queue()
    }
    terminate = Event()
    modules = dict() # registered modules
    term_handlers = dict() # termux calls
    # --
    @classmethod
    def arg(cls, args :str|None=None):
        """Register command handler function."""
        def wrapper(fn):
            def wrapped(fn):
                name = fn.__name__.replace('_', '-')
                if not cls.term_handlers.get(name):
                    cls.term_handlers.update({name: {'handler': fn, 'args': args}})
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
        super().__init__()
        for mod in self.modules:
            mod.app = self # pointer to main activity
            self.modules[mod].update({'name': mod.__name__})
            module = mod(self.modules[mod])
            self.modules[mod]['instance'] = module

    # --
    def query(self, cmd :list):
        """Validate and execute cmd[0] with cmd[1:] arguments"""
        if cmd[0] not in self.term_handlers:
            raise RuntimeError(f'Handler for [{cmd}] not registered!')
        for arg in cmd[1:]:
            if arg not in (args := self.term_handlers[cmd[0]]['args']):
                if '*' not in args:
                    invalid = [i for i in cmd[1:] if i not in args]
                    raise RuntimeError(f'Invalid parameter(s) {invalid} for {cmd[0]}')
        #
        ret = self.exec(cmd, capture_output=True, timeout=10)
        try:
            if not (out := ret.stdout.read()):
                if err := ret.stderr.read().decode().strip():
                    raise RuntimeError(err)
                raise RuntimeError(f'{" ".join(cmd)} failed : {ret.returncode}\n{ret.stdout.read().decode()}')
            return True, self.term_handlers[cmd[0]]['handler'](out.decode())
        except Exception as e:
            e.add_note(ret.stderr.read().decode())
            return False, e

    def listen(self, port: int, stop: Event):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', port))
        sock.settimeout(10)
        sock.listen()
        while not self.terminate.is_set():
            if stop.is_set():
                sock.close()
                break
            try:
                conn, addr = sock.accept()
                conn.settimeout(3)
                line = conn.recv(1024).decode()
                yield line
            except Exception:
                continue

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

    def shutdown(self, *_):
        if self.terminate.is_set():
            return
        self.terminate.set()
        return logger.info('Terminated.')

