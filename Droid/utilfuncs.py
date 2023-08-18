from loguru import logger
from datetime import timedelta


def get_duration(duration :str):
    """Get call-log duration from string of format mm:ss"""
    duration = duration[-5:].split(':')
    total_time = (int(duration[0]) * 60) + int(duration[1])
    return timedelta(seconds=total_time)

def get_sender(value : str):
    """todo: describe"""
    logger.debug(f'todo: describe {value}')
    num = value.replace(' ','').replace('-','')
    try:
        _ = int(num)
    except ValueError:
        return value
    return num[-9:]
