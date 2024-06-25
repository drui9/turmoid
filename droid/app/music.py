from droid import Droid as dru
from loguru import logger
from hashlib import md5
from . import session
import random
import time
import glob

# --
def score(matrix, i, j):
    update = [j]
    for k, v in matrix[i].items():
        if k == j: continue
        if v == 0: continue
        update.append(k)
    scr = 1 / len(update)
    for u in update:
        matrix[i][u] = scr
    return scr

# --
def get_next(data):
    nxt = random.choice(list(data['songs']))
    return data['songs'][nxt]

# --
def play(core, song, volume):
    core.query(['termux-volume', 'music', str(volume)])
    _, prev = core.query(['termux-media-player', 'info'])
    core.query(['termux-media-player', 'play', song])
    return prev

# --
@dru.app(
    on='droid.MUSIC',
    desc='Play & download audio music',
)
def music(*args):
    with session(*args) as context:
        core, init, data = context
        if not init.is_set():
            init.set()
            data['settings'] = {
                'shuffle': True,
                'volume': 2
            }
            data['matrix'] = dict()
            data['ranking'] = dict()
            data['songs'] = dict()
            # -- create music-file hashes
            for song in glob.glob('/data/data/com.termux/files/home/storage/music/*.mp3'):
                data['songs'][md5(song.encode()).hexdigest()] = song
            # --
            for song in data['songs']:
                # -- initialize ranks with equal weight
                data['ranking'][song] = 1/ len(data['songs'])
                # -- create play-step matrix
                data['matrix'][song] = dict()
                for inner in data['songs']:
                    data['matrix'][song][inner] = 0
        # --
        volume = data['settings']['volume']
        nxt = get_next(data)
        prev = play(core, nxt, volume).split('\n')
        if len(prev) > 3:
            name, pos = [i for i in data['songs'].values() if prev[1].split(': ')[-1] in i][-1], prev[2].split(': ')[-1]
            logger.debug('name: {}, position: {}', name, pos)
        time.sleep(5)
        core.emit('droid.SHUTDOWN')

