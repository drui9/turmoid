from threading import Event
import subprocess as sp
from hashlib import md5
from glob import glob
import os

# --
def toast(what: str, bg = '#a67b1e', clr = 'white'):
    tst = sp.Popen(['termux-toast', '-b', bg, '-c', clr, '-s', what])
    tst.wait()
    return tst

# <> ordered imports
from droid.droid import Dru
# --
from droid.tool.termcall import *
from droid.tool.sensors import *
from droid.app import *
# </>

# <> load modules
def loadmods(paths, app):
    mods = app.context['data']['modules']
    for pth in paths:
        with open(pth, "rb") as md:
            src = md.read()
            alias = md5(src).hexdigest()
            mods[pth] = {
                'hash': alias,
                'src': src,
                'runtime': {
                    'active': Event(),
                    'connection': None
                }
            }

# <> create app
def create_app(mods: str):
    modules = glob(os.path.join(mods, '*.py'))
    # --
    app = Dru()
    loadmods(modules, app)
    app.toast = toast
    return app
# </>

