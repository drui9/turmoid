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

def create_app():
    return Droid()

