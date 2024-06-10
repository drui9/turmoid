import json
from .filters import *
from .sensor import Sensor
from loguru import logger
#--
@Sensor.parser()
def listen(p):
    data = b''
    # -- read sensor vals
    while (ch := p.stdout.read(1)):
        if ch == b' ': continue
        if ch == b'\n':
            if b']}}' in data:
                try:
                    data = data.replace(b'{}', b'')
                    yield json.loads(data.decode())
                except Exception as e:
                    e.add_note(data.decode())
                    logger.exception('what?')
                finally:
                    data = b''
            continue
        data += ch
    return

__all__ = [
    'Sensor'
]
