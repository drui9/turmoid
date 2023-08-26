from droid.core import DroidCore
from droid.dirmon import Watchdog
from droid.termux import Termux


class DroidBase(DroidCore):
    # builtins
    dirmon = Watchdog()
    termux = Termux()

    # -- start ---
    def __init__(self):
        super().__init__()
        return

    # -- trigger shutdown
    @classmethod
    def stop(cls, reason :str|None = None):
        if reason:
            cls.logger.info(f'Shutting down: {reason}')
        cls.events.terminate.set()
