import subprocess as sp
from contextlib import contextmanager
import os

@contextmanager
def modvol():
    os.system('termux-volume music 3')
    yield
    os.system('termux-volume music 8')

tts = sp.Popen(['termux-tts-speak', '-r', '1.2', '-s', 'ALARM'], stdin=sp.PIPE)
with modvol():
    while out := input(str('>> ')):
        if 'close' in out.lower():
            tts.terminate()
            break
        if out[-1] != '.':
            out += '.'
        tts.stdin.write(out.encode())
        tts.stdin.flush()
tts.kill()

