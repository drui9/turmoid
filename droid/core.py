import time
import queue
import socket
import signal
import subprocess as sp
from loguru import logger
from threading import Lock
from threading import Event
from .tool.emitter import Emitter

# --
class Core(Emitter):
    context = {
        'termux': {
            'lock': Lock(),
            'handlers': dict()
        },
        'runtime': {
            'call': { # -- unused
                'name': str(),
                'args': None,
                'kwargs': None,
            },
            'data': {
                'apps': dict(),
                'terminate': Event()
            }
        }
    }
    # <> add termux-calls
    @classmethod
    def command(cls, args :str|None=None):
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

    # <> register an app
    @classmethod
    def app(cls, *args, **kwargs):
        def wrapper(theapp):
            data = cls.context['runtime']['data']
            data['apps'] |= {
                theapp.__name__: {
                    'args': args,
                    'kwargs': kwargs,
                    'handle': {
                        'enter': theapp,
                        'instance': None,
                        'data': dict()
                    }
                }
            }
            return theapp
        return wrapper
    # </>

    # <> initialize core
    def __init__(self):
        super().__init__()
        signal.signal(signal.SIGINT, self.shutdown)
    # </>

    # <> call a termux method
    def query(self, cmd :list):
        """Validate and execute cmd[0] with cmd[1:] arguments"""
        with self.context['termux']['lock']:
            if cmd[0] not in self.context['termux']['handlers']:
                raise RuntimeError(f'Handler for [{cmd}] not registered!')
            for arg in cmd[1:]:
                if arg not in (args := self.context['termux']['handlers'][cmd[0]]['args']):
                    if '*' not in args:
                        invalid = [i for i in cmd[1:] if i not in args]
                        raise RuntimeError(f'Invalid parameter(s) {invalid} for {cmd[0]}')
        #
        start = time.time()
        ret = self.exec(cmd, capture_output=True, timeout=12)
        if (latency := time.time() - start) > 10:
            logger.debug('Excess exec latency: {}', latency)
        try:
            if not (out := ret.stdout.read()):
                if err := ret.stderr.read().decode().strip():
                    return False, f'{" ".join(cmd)} failed : {ret.returncode}\n{err}'
            with self.context['termux']['lock']:
                handler = self.context['termux']['handlers'][cmd[0]]['handler']
            return True, handler(out.decode())
        except Exception as e:
            e.add_note(ret.stderr.read().decode())
            raise
    # </>

    # <> run a network listener
    def listen(self, port: int):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('127.0.0.1', port))
        sock.settimeout(10)
        sock.listen()
        while not self.stop:
            conn = -1
            try:
                conn, addr = sock.accept()
                logger.debug('Connection from: {}:{}', addr[0], addr[1])
                conn.settimeout(3)
                out = conn.recv(128)
                conn.send('--close--\n'.encode())
                conn.close()
                yield out
            except socket.timeout:
                if conn != -1:
                    conn.send('--close--\n'.encode())
                    conn.close()
                continue
        sock.close()
    # </>

    # <> Execute a subprocess task
    def exec(self, cmd :list|str, capture_output=False, timeout=None):
        cmd = cmd.split(' ') if isinstance(cmd, str) else cmd
        sin, out, err = (sp.PIPE, sp.PIPE, sp.PIPE) if capture_output else (None, None, None)
        task = sp.Popen(cmd, stdin=sin, stdout=out, stderr=err)
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

    # <> check stop
    @property
    def stop(self):
        return self.context['runtime']['data']['terminate'].is_set()
    # </>

    # <> shut down
    def shutdown(self, *_, **__):
        if not self.context['runtime']['data']['terminate'].is_set():
            self.context['runtime']['data']['terminate'].set()
            return logger.debug('Terminated.')
    # </>

