class Emitter:
    def __init__(self):
        self.handlers = {}
        self.children = list()

    def child(self, chld):
        if isinstance(chld, type(self)):
            return self.children.append(chld)
        elif hasattr(chld, 'evt'):
            return self.children.append(chld.evt)
        raise RuntimeError('Invalid child event emitter!')

    def fetch(self, event):
        out = list()
        if event in self.handlers:
            out.append(self)
        for ch in self.children:
            if event in ch.handlers:
                out.append(ch)
        return out

    def emit(self, event, *args, **kwargs):
        err = list()
        for source in self.fetch(event):
            for handler in source.handlers[event]:
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    err.append((e, event, handler, source))
        return err

    def remove(self, event, handler):
        if handler in self.handlers[event]:
            self.handlers[event].remove(handler)
        return handler not in self.handlers[event]

    def on(self, event, *args):
        if args:
            if event not in self.handlers:
                self.handlers[event] = list()
            for handler in args:
                if handler not in self.handlers[event]:
                    self.handlers[event].append(handler)
        else:
            def wrapper(handler):
                if event not in self.handlers:
                    self.handlers[event] = list()
                if handler not in self.handlers[event]:
                    self.handlers[event].append(handler)
            return wrapper

