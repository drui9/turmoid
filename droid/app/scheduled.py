from droid.tool.schedule import Scheduler
from loguru import logger

# --
@Scheduler.add(1)
def check_clip(app):
    with app.runtime('clipboard') as clip:
        logger.debug(clip)

# --
@Scheduler.add(0)
def check_batt(app):
    logger.debug('Check batt')

