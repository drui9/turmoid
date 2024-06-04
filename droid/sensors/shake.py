import json
import math
import subprocess as sp
from loguru import logger
from contextlib import contextmanager

# --
def shake(interval=300, smoothing=10, threshold=3.0):
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
    oldest, thesum, count = 0.0, 0.0, 0
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
                        accel = math.sqrt(sum([math.pow(i, 2) for i in v['values'][:-1]]))
                        if count < smoothing:
                            thesum = (thesum - oldest) + accel
                            oldest = accel
                            count += 1
                            continue
                        thesum = (thesum - oldest) + accel
                        oldest, count = accel, count + 1
                        # --
                        if (thesum / smoothing)> threshold:
                            p.terminate()
                            return True
                except Exception:
                    pass
                finally:
                    data = b''

