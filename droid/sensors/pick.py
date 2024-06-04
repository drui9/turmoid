import json
import subprocess as sp
from loguru import logger
from contextlib import contextmanager

# --
def picked(interval=500):
    @contextmanager
    def runner():
        clean = sp.Popen(['termux-sensor', '-c'], stdout=sp.PIPE)
        clean.wait()
        if not clean.returncode:
            p = sp.Popen(['termux-sensor', '-s', 'ACC', '-d', str(interval)], stdout=sp.PIPE)
            yield p
            p.kill()
            p.wait()
        else:
            logger.warning('Sensor cleanup failed.')
            yield
    # --
    data = b''
    with runner() as p:
        if not p: return
        # -- read sensor vals
        while (ch := p.stdout.read(1)):
            if ch == b' ' or ch == b'\n':
                continue
            data += ch
            if b']}}' in data:
                try:
                    for _, v in json.loads(data.decode()).items():
                        y, z = v['values'][1:]
                        # --
                        if (y > 4.0) and (z < 8.0):
                            p.terminate()
                            return True
                except Exception:
                    pass
                finally:
                    data = b''

