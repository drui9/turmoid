from droid import Droid as dru
from loguru import logger
from . import session
import time

@dru.app(
    on='droid.TORCH',
    desc='Light up dark caves',
)
def torch(*args):
    with session(*args) as context:
        core, init, data = context
        init.clear() # -- prevent save
        if 'state' not in data:
            data['state'] = 'off'
        if data.get('state') == 'off':
            data['state'] = 'on'
            ok, _= core.query(['termux-torch', 'on'])
        else:
            data['state'] = 'off'
            ok, _= core.query(['termux-torch', 'off'])

