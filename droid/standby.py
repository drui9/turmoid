from droid.tool.emitter import Emitter as emma
from loguru import logger

@emma.on('droid.STANDBY')
def standby(app):
    with app.context['app']['lock']:
        for name, appl in app.context['app']['data'].items():
            if name == 'standby' or appl['active'].is_set(): continue
            trigger = appl['on']
            action = f'echo {trigger} | nc localhost {app.port}'
            ok, _ = app.query(['termux-notification', '--ongoing', '-i', appl['id'], '-t', name, '-c', 'Click to launch', '--action', action])
            if ok:
                app.notices.append(appl['id'])
            logger.info('Listing app {}::{}', name, ok)

