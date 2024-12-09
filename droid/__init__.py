from base64 import b64encode
import subprocess as sp
from hashlib import md5

# <> toast
def toast(what: str, bg = '#a67b1e', clr = 'white', g = 'middle'):
    tst = sp.Popen(['termux-toast', '-b', bg, '-c', clr, '-s', '-g', g, what])
    tst.wait()
    return tst
# </>

# <> ordered imports
from droid.droid import Dru
# --
from droid.tool.termcall import *
from droid.tool.sensors import *
from droid.app import *
# </>

# <> load modules
def loadmods(paths, app):
    old = app.modules['loaded']
    new = dict()
    for pth in paths:
        with open(pth, "rb") as md:
            src = md.read()
            hashed = md5(src).hexdigest()
            new[pth] = {
                'hash': hashed,
                'src': b64encode(src).hex()
            }
    app.modules['loaded'] = new
    return old, new
# </>

# <> create app
def create_app(mods: str):
    app = Dru()
    # --
    app.toast = toast
    app.modules |= {
        'init': {
            'loader': loadmods,
            'path': mods
        },
        'loaded': dict()
    }
    return app
# </>

