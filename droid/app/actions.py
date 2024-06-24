from droid.tool.emitter import Emitter
from contextlib import contextmanager
from threading import Thread
from loguru import logger
from droid import Droid

# <>
@Emitter.on('droid.INIT')
def oninit(app: Droid):
    with app.runtime('init') as init:
        if not init.get('shake'):
            def proximity():
                # <>
                with app.sensor.on('proximal') as pr:
                    proximal = pr[0]
                    with app.sensor.sense('proximity', 500) as prox:
                        for state in proximal(prox):
                            if isinstance(state, str):
                                app.emit(state)
                # </>
            init['shake'] = Thread(target=proximity)
            init['shake'].name = 'proximity-detector'
            init['shake'].start()
# </>

# <>
@Emitter.on('droid.youtube.DOWNLOAD')
def downloader(app):
    with app.runtime('yt-dlp') as ytdl:
        with app.runtime('tts') as tts:
            source = [i for i in ytdl.get("url").split('/') if 'you' in i][-1]
            tts['out'] = f'Downloading video from {source}'
            app.query(['termux-clipboard-set', ''])
        app.emit('droid.tts.OUT')
# </>


# <>
@Emitter.on('droid.sensor.NEAR')
def covered(app):
    with app.runtime('tts') as tts:
        tts['out'] = 'Hibernating'
    app.emit('droid.tts.OUT')
# </>

# <>
@Emitter.on('droid.sensor.FAR')
def uncovered(app):
    with app.runtime('tts') as tts:
        tts['out'] = 'Activated'
    app.emit('droid.tts.OUT')
# </>

# <>
@Emitter.on('droid.tts.OUT')
def speak(app):
    with app.runtime('tts') as tts:
        if not (volman := tts.get('volman')):
            # <>
            @contextmanager
            def volume_manager():
                ok, vols = app.query(['termux-volume'])
                if not ok: yield; return
                ok, _ = app.query(['termux-volume', 'alarm', '8'])
                if not ok: yield; return
                ok, _ = app.query(['termux-volume', 'music', '2'])
                yield ok
                for stream in vols:
                    if stream['stream'] == 'alarm':
                        _ = app.query(['termux-volume', 'alarm', str(stream['volume'])])
                    elif stream['stream'] == 'music':
                        _ = app.query(['termux-volume', 'music', str(stream['volume'])])
            # </>
            volman = volume_manager
            tts['volman'] = volman
        # --
        with volman() as ready:
            if ready:
                ok, out = app.query(['termux-tts-speak', '-r', '1.2', '-s', 'ALARM', tts['out']])
                if not ok:
                    logger.critical('TTS speech failed: {}', out)
# </>
