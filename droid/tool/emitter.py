from loguru import logger

# --
class Emitter:
    evt_handlers = {}
    children = list()

    @classmethod
    def fetch(cls, event):
        if event in cls.evt_handlers:
            return cls.evt_handlers[event]
        return list()

    @classmethod
    def emit(cls, event, *args, **kwargs):
        err = list()
        ok = list()
        for handler in cls.fetch(event):
            try:
                ok.append(handler(*args, **kwargs))
            except Exception as e:
                e.add_note(event)
                logger.exception('what?')
                err.append(handler)
        return ok, err

    @classmethod
    def remove(cls, event, handler):
        if handler in cls.evt_handlers[event]:
            cls.evt_handlers[event].remove(handler)
        return handler not in cls.evt_handlers[event]

    @classmethod
    def on(cls, event, *args):
        def wrapper(handler):
            if event not in cls.evt_handlers:
                cls.evt_handlers[event] = list()
            if handler not in cls.evt_handlers[event]:
                cls.evt_handlers[event].append(handler)
        if args:
            if event not in cls.evt_handlers:
                cls.evt_handlers[event] = list()
            for handler in args:
                if handler not in cls.evt_handlers[event]:
                    cls.evt_handlers[event].append(handler)
        return wrapper

