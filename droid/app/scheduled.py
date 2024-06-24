from droid.tool.schedule import Scheduler
# from loguru import logger
import re

link = re.compile(r'https:\/\/[\w\.-]+\/[\w\.-]+')
# --
@Scheduler.add(1)
def check_clip(app):
    ok, content = app.query(['termux-clipboard-get'])
    if ok and content:
        with app.runtime('clipboard') as clip:
            if clip.get('content') != content:
                clip['content'] = content
                if match := re.search(link, content):
                    _= app.query(['termux-toast', '-s', '-b', 'black', 'Link copied'])
                    with app.runtime('yt-dlp') as downloader:
                        downloader['url'] = match.string
                    app.emit('droid.youtube.DOWNLOAD')
                else:
                    with app.runtime('tts') as tts:
                        tts['out'] = content
                    app.emit('droid.tts.OUT')

# --
@Scheduler.add(2)
def check_batt(app):
    ok, status = app.query(['termux-battery-status'])
    if ok and isinstance(status, dict):
        with app.runtime('battery') as batt:
            if batt.get('status') and status['status'] != batt['status']:
                app.emit('droid.battery.{}'.format(status['status']))
                with app.runtime('tts') as tts:
                    tts['out'] = f'Device {status["status"].lower()} at {status["percentage"]}'
                app.emit('droid.tts.OUT')
            batt |= status

