'''
@author: drui9
@thread-safety: false
'''
from typing import Callable

# <> Event emitter class
class Eventt:
    def __init__(self) -> None:
        self.handle = dict()
        return

    def on(self, evt :str, **kwargs):
        for handler in self.handle[evt]:
            handler(**kwargs)

    def link(self, fn: Callable, evt: str):
        if evt not in self.handle:
            self.handle[evt] = [fn]
        else:
            self.handle[evt].append(fn)

    def unlink(self, fn: Callable, evt: str|None = None):
        if evt:
            self.handle[evt].remove(fn)
        else:
            for fn_list in self.handle.values():
                if fn in fn_list:
                    fn_list.remove(fn)
#</>
