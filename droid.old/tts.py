from . import droid
from queue import Empty, Queue


@droid.activity(0, io=(Queue(), 'w', str))
def text_to_speech(ctx):
    io, modes, _type = ctx['io']
    proc = droid.termux.query('termux-tts-speak')
    while not droid.events.is_set('terminate'):
        try:
            if out := io.get(timeout=5):
                if not isinstance(out, _type):
                    droid.logger.critical(f'Type: {type(out)} != {_type}')
                    continue
                #
                proc.stdin.write(out.encode('utf8'))
                if '\n' not in out:
                    proc.stdin.write(b'\n')
                proc.stdin.flush()
        except Empty:
            continue
        except Exception as e:
            droid.logger.exception(e)
