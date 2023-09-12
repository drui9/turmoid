"""
 == core ==
Controlls scheduled functions and threading.Event(s) as a group
"""
import time
import math
import loguru
import threading
from datetime import datetime


class DroidCore:
    activities = dict()
    logger = loguru.logger
    # -- instance initialization
    def __init__(self):
        self.events.set_parent(self)
        return
    #
    @classmethod
    def activity(cls, interval=-1, **kwargs):
        """Register a new activity"""
        if interval < -1:
            interval -= 1
        #
        def wrapper(fn):
            if interval not in cls.activities:
                cls.activities.update({interval: list()})
            #
            if interval > 0:
                if 'notify' in kwargs:
                    complement = (-1 * interval) - 1
                    if complement not in cls.activities:
                        cls.activities.update({complement: list()})
                    kwargs.update({'notify': complement})
            if 'io' in kwargs:
                cls.io.add(fn.__name__, kwargs['io'])
            # append routine
            routine = {
                    'handler': fn,
                    'context': {
                        'last_run': datetime.now(),
                        'reason': 'N/A',
                        'ok': True
                    } | kwargs
                }
            cls.activities[interval].append(routine)
            return # block external calls
        return wrapper

    def __get_lcm(self, nums):
        """Get the least common multiple of List[nums]"""
        gcd = math.gcd(*nums)
        return abs(math.prod(nums)) // gcd

    @staticmethod
    def __get_next(start, end, intervals):
        """Get the index of the upcoming routine handler"""
        if len(intervals) == 1:
            return intervals[0]
        for i in range(start, end):
            for intv in intervals:
                if i % intv == 0:
                    return i

    @classmethod
    def __execute(cls, interval):
        """execute a function routine and handle errors"""
        for task in cls.activities[interval]:
            if not task['context']['ok']: # there's a failed call
                continue
            #
            try:
                task['handler'](task['context'])
                task['context']['last_run'] = datetime.now()
                cls.logger.debug(f'{task["handler"].__name__} completed.')
            except Exception as e:
                e.add_note(f'{task["handler"].__name__}')
                cls.logger.exception(e)
                task['context']['ok'] = False
                task['context']['reason'] = str(e) or type(e)
        return

    def scheduler(cls):
        """ 1+ -> Scheduled at intervals"""
        """ 0 -> Spawned in separate process"""
        """ -1 -> Restroom while (x < -1) -> complements to (|x| - 1)"""
        intervals = [i for i in sorted(cls.activities) if i > 0]
        cls.logger.info('Starting persistent threads...')
        for twork in (cls.activities.get(0) or list()):
            handler = twork['handler']
            ctx = twork['context']
            tw = threading.Thread(target=handler, args=(ctx,))
            ctx['last_run'] = datetime.now()
            tw.name = handler.__name__
            tw.daemon = True
            tw.start()
        cls.logger.info('Persistent threads started.')
        #
        if (not cls.activities) or (not intervals):
            return
        #
        lcm = cls.__get_lcm(intervals)
        sleeptime = 0
        #
        cls.logger.info('Starting scheduler...')
        while not cls.stopped():
            cls.logger.debug('Scheduler cycle started...')
            if sleeptime % lcm == 0:
                sleeptime = 0
            # do work
            for interval in intervals:
                if sleeptime % interval == 0:
                    cls.__execute(interval)
            # find timeout to next work & sleep
            nextv = cls.__get_next(sleeptime + 1, lcm + 1, intervals)
            timeout = nextv - sleeptime
            sleeptime += timeout
            cls.logger.debug(f'Sleeptime({timeout})')
            time.sleep(timeout)
        #
        cls.logger.info('Scheduler stopped.')
        return

    #
    @classmethod
    def stopped(cls):
        """Check termination flag"""
        cls.logger.debug('Stop flag checked.')
        return cls.events.get('terminate').is_set()
