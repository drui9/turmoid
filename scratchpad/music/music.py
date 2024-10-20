from .eventt import Eventt
from threading import Event
from . import durations, ranks
from queue import Queue, Empty

# <> Music Player
class Music:
    timeout = 3
    def __init__(self):
        self.played = list()
        self.emiter = Eventt()
        self.durations = durations
        self.playing = None
        self.ranks = ranks
        self.duration = 0
        # --
        self.events = Queue()
        self.terminate = Event()

    # <> fetch next
    def next(self):
        unplayed = [i for i in self.ranks if i not in self.played]
        max_score = unplayed[0] # todo: select highest ranking
        return max_score, self.durations[max_score]
    # </>

    # --<> is stop?
    @property
    def stop(self):
        if self.terminate.is_set():
            return True
    # -- </>

    # --<> on
    def on(self, evt: str, **kwargs):
        self.events.put((evt, kwargs))
    # --</>

    # -- <>
    def start(self):
        while not self.stop:
            try:
                evt, kwargs = self.events.get(timeout=self.timeout)
                self.emiter.on(evt, **kwargs)
            except Empty:
                continue
            except Exception:
                self.terminate.set()
                raise
    # --</>
# </>

