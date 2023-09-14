import json
import random
import threading


class EventGroup:
    """Thread safety: False"""
    def __init__(self, exit_evt):
        self.events = dict()
        self.terminate = exit_evt
        self.events['terminate'] = exit_evt
        return

    #
    def add(self, name :str, overwrite=True) -> threading.Event:
        """Add a new threading.Event with name to Dict[str, threading.Event]"""
        if not (e := self.get(name)):
            e = threading.Event()
            self.events.update({name :e})
            return e
        elif not overwrite:
            raise RuntimeError(f'Event({name}) is already taken!')
        return e

    #
    def pop(self, name) -> threading.Event:
        """Detach and return threading.Event() where key==`name`"""
        if name in self.events:
            return self.events.pop(name)

    #
    def clear(self, name :str) -> threading.Event:
        """Clear set() value of event at name"""
        if (evt := self.get(name)):
            evt.clear()
            return evt

    #
    def get(self, name :str):
        """Get event of name from self.events"""
        if name not in self.events:
            return
        return self.events.get(name)

    #
    def wait(self, name :str) -> bool:
        """Wait for event to be set"""
        if (evt := self.get(name)):
            while not self.get('terminate').is_set():
                if evt.wait(timeout=random.randint(1,3)):
                    return True
        return False

    #
    def set(self, name :str):
        """Call threading.Event().set on event of `name`"""
        if (evt := self.get(name)):
            return evt.set()
        raise RuntimeError(f'Event({name}) is undefined.')

    #
    def is_set(self, name :str):
        """Check if event of `name` is set()"""
        if evt := self.get(name):
            return evt.is_set()
        raise RuntimeError(f'threading.Event({name}) is undefined!')

    #
    def __repr__(self):
        return json.dumps([{'name': k, 'is-set': v.is_set()} for k,v in self.events.items()])  # noqa: E501
