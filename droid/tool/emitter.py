from loguru import logger

# --
class Emitter:
    def __init__(self):
        self.evt_handlers = {}
        self.children = list()

    def child(self, chld):
        if isinstance(chld, type(self)):
            return self.children.append(chld)
        elif hasattr(chld, 'evt'):
            return self.children.append(chld.evt)
        raise RuntimeError('Invalid child event emitter!')

    def fetch(self, event):
        out = list()
        if event in self.evt_handlers:
            out.extend(self.evt_handlers[event])
        for ch in self.children:
            if event in ch.evt_handlers:
                out.extend(ch.evt_handlers[event])
        return out

    def emit(self, event, *args, **kwargs):
        err = list()
        ok = list()
        for handler in self.fetch(event):
            try:
                ok.append(handler(*args, **kwargs))
            except Exception as e:
                e.add_note(event)
                logger.exception('what?')
                err.append(handler)
        return ok, err

    def remove(self, event, handler):
        if handler in self.evt_handlers[event]:
            self.evt_handlers[event].remove(handler)
        return handler not in self.evt_handlers[event]

    def on(self, event, *args):
        if args:
            if event not in self.evt_handlers:
                self.evt_handlers[event] = list()
            for handler in args:
                if handler not in self.evt_handlers[event]:
                    self.evt_handlers[event].append(handler)
        else:
            def wrapper(handler):
                if event not in self.evt_handlers:
                    self.evt_handlers[event] = list()
                if handler not in self.evt_handlers[event]:
                    self.evt_handlers[event].append(handler)
            return wrapper

