import json
import subprocess as sp
from loguru import logger
from .sensor import Sensors
from contextlib import contextmanager

# --
@Sensors.evt.on('interval')
def get_interval(vals):
    return min(vals)

# --
@Sensors.sense()
def listen(sensor, *args):
    @contextmanager
    def runner(interval):
        p = sp.Popen(['termux-sensor', '-s', sensor, '-d', str(interval)], stdout=sp.PIPE)
        yield p
        p.kill()
        p.wait()
    # -- parse args
    scope = args[1]
    intervals = list()
    for reader in scope['readers']:
        intervals.append(reader[args[0]])
    ok, _ = Sensors.evt.emit('interval', intervals)
    interval = ok[-1]
    # -- sensor-clean & start
    sp.Popen(['termux-sensor', '-c'], stdout=sp.PIPE).wait()
    while scope['active'].is_set():
        data = b''
        with runner(interval) as p:
            # -- read sensor vals
            while (ch := p.stdout.read(1)):
                if ch == b' ': continue
                if ch == b'\n':
                    if b']}}' in data:
                        try:
                            for _, v in json.loads(data.decode()).items():
                                ok, err = Sensors.evt.emit(sensor.lower(), *v['values'])
                                if not ok: # errored/no consumers
                                    scope['active'].clear()
                                    p.kill()
                                    logger.debug('{} stopped:{}:{}', sensor, ok, err)
                            if not scope['active'].is_set():
                                break
                        except Exception: pass
                        finally:
                            data = b''
                    continue
                data += ch
    logger.debug('{} thread stopped.', sensor)

