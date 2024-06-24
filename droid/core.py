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
    context = {
        'events': { # <> [emit] record
            'lock': Lock(),
            'items': list(),
            'source': queue.Queue()
        },
        'termux': {
            'lock': Lock(),
            'handlers': dict()
        },
        'runtime': {
            'lock': Lock(),
            'contexts': dict()
        } # </>
    }
    terminate = Event()
    # <> add a termux-call
    @classmethod
    def arg(cls, args :str|None=None):
        """Register command handler function."""
        def wrapper(fn):
            def wrapped(fn):
                with cls.context['termux']['lock']:
                    name = fn.__name__.replace('_', '-')
                    if not cls.context['termux']['handlers'].get(name):
                        cls.context['termux']['handlers'].update({name: {'handler': fn, 'args': args}})
                return fn
            return wrapped(fn)
        return wrapper
    # </>

    # <> initialize core
    def __init__(self):
        super().__init__()
        @contextmanager
        def slot(name: str):
            # <> Register & fetch runtime data
            with self.context['runtime']['lock']:
                if name not in self.context['runtime']['contexts']:
                    self.context['runtime']['contexts'][name] = {
                        'lock': Lock(),
                        'data': dict()
                    }
            with self.context['runtime']['contexts'][name]['lock']:
                yield self.context['runtime']['contexts'][name]['data']
            # </>
        self.runtime = slot
    # </>

    # <> call a termux method
    def query(self, cmd :list):
        """Validate and execute cmd[0] with cmd[1:] arguments"""
        with self.context['termux']['handlers']:
            if cmd[0] not in self.context['termux']['handlers']:
                raise RuntimeError(f'Handler for [{cmd}] not registered!')
            for arg in cmd[1:]:
                if arg not in (args := self.context['termux']['handlers'][cmd[0]]['args']):
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
            with self.context['termux']['lock']:
                handler = self.context['termux']['handlers'][cmd[0]]['handler']
            return True, handler(out.decode())
        except Exception as e:
            e.add_note(ret.stderr.read().decode())
            return False, e
    # </>

    # <> run a network listener
    def listen(self, port: int):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('127.0.0.1', port))
        sock.settimeout(10)
        sock.listen()
        while not self.terminate.is_set():
            conn = -1
            try:
                conn, addr = sock.accept()
                logger.debug('Connection from: {}:{}', addr[0], addr[1])
                conn.settimeout(3)
                out = conn.recv(128)
                conn.send('--close--'.encode())
                conn.close()
                yield out
            except socket.timeout:
                if conn != -1:
                    conn.send('--close--'.encode())
                    conn.close()
                continue
        sock.close()
    # </>

    # <> Execute a subprocess task
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
    # </>

    # <> shut down
    def shutdown(self, *_):
        if self.terminate.is_set():
            return
        self.terminate.set()
        return logger.debug('Terminated.')
    # </>

