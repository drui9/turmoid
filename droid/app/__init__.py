from contextlib import contextmanager
from loguru import logger
import json
import os

DATA_DIR = 'secrets'

@contextmanager
def session(*args):
    appl_name, core = args
    with core.slot(appl_name) as slot:
        if not os.path.exists(DATA_DIR): os.mkdir(DATA_DIR)
        path = os.path.join(os.getcwd(), DATA_DIR, slot['id'])
        if not slot['initialized'].is_set():
            if os.path.exists(path):
                with open(path) as datafile:
                    slot[slot['id']] = json.load(datafile)
                    slot['initialized'].set()
        slot['active'].set()
        try:
            yield core, slot['initialized'], slot[slot['id']] # --
        except Exception as e:
            e.add_note(f'App: {appl_name}')
            logger.exception('what?')
        finally:
            slot['active'].clear()
            if slot[slot['id']] and slot['initialized'].is_set():
                with open(path, 'w') as datafile:
                    json.dump(slot[slot['id']], datafile, indent=2)
    core.emit('droid.STANDBY', app=core)

# <>
from .music import music
from .torch import torch
# </>
