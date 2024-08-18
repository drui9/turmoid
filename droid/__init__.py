import subprocess as sp

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



# <> create app
def create_app():
    app = Dru()
    return app
# </>

