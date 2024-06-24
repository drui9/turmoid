from droid.droid import Droid

# <>
from droid.app import *
from droid.tool.termcall import *
from droid.tool.sensors import *
# </>

def create_app(port):
    Droid.port = port
    return Droid()

