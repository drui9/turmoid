"""
Handles multiple threading.Event variables to prevent deadlock
and unify control flow.
"""
import threading
import loguru

class EventGroup:
    def __init__(self, terminate :threading.Event, sleeptime=3):
        self.logger = loguru.logger
        self.terminate = terminate
        self.sleeptime = sleeptime
        self.events = dict()

    def add(self, name :str) -> threading.Event:
        """Add a new threading.Event with name to Dict[str, threading.Event]"""
        e = threading.Event()
        self.events.update({name :e})
        return e

    def clear(self, name :str) -> threading.Event:
        """Clear set() value of event at name"""
        if (evt := self.get(name)):
            evt.clear()
            return evt

    def get(self, name :str):
        """Get event of name from self.events"""
        if name not in self.events:
            return
        return self.events.get(name)

    def wait(self, name :str) -> threading.Event:
        """Wait for event to be set"""
        if (evt := self.get(name)):
            while not self.terminate.is_set():
                print('waiting')
                if evt.wait(timeout=self.sleeptime):
                    return evt
        return

    def set(self, name :str):
        """Call threading.Event().set on event of `name`"""
        evt = self.get(name)
        evt.set()
        return True

    def is_set(self, name :str):
        """Check if event of `name` is set()"""
        evt = self.get(name)
        if evt:
            return evt.is_set()
        raise RuntimeError(f'Event {name} is undefined!')
