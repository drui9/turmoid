from droid.main import Droid
from .sensors.listeners import (
    proximal,
    putdown,
    flipped,
    picked,
    shake,
    dusk,
    dawn
)
from .modules import Torch
from .termcalls import *

def create_app():
    return Droid()

