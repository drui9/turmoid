"""
 == core ==
Controlls scheduled functions and threading.Event(s) as a group
"""
import time
import math
import loguru
import threading
from datetime import datetime
from droid.events import EventGroup


class DroidCore:
    routines = dict()
    logger = loguru.logger
    events = EventGroup(threading.Event())
    #
    @classmethod
    def scheduler(cls):
        """Schedule functions to run at registered intervals"""
        if not cls.routines:
            cls.logger.info('No scheduled routines.')
            return
        elif cls.stopped():
            raise RuntimeError('Terminate flag is on!')
        #
        intervals = sorted(cls.routines)
        lcm = cls.__get_lcm(intervals)
        sleeptime = 0
        while not cls.stopped():
            if sleeptime % lcm == 0:
                sleeptime = 0
            # do work
            for interval in cls.routines:
                if sleeptime % interval == 0:
                    cls.__execute(interval)
            # find timeout to next work & sleep
            nextv = cls.__get_next(sleeptime + 1, lcm + 1, intervals)
            timeout = nextv - sleeptime
            sleeptime += timeout
            time.sleep(timeout)
        cls.logger.info('Scheduler closed.')
        return

    # add new routines
    @classmethod
    def routine(cls, interval):
        """Add a routine to execute at each interval time"""
        """execute routine as daemon thread if interval == 0"""
        def wrapper(fn):
            if interval == -1:
                return fn # allow external calls
            elif not interval:
                work = threading.Thread(target=fn)
                work.name = fn.__name__
                work.daemon = True
                work.start()
                return None # block external calls
            #
            if interval not in cls.routines:
                cls.routines.update({interval: list()})
            # append routine
            routine = {
                    'handler': fn,
                    'context': {
                        'runtime': {
                            'last_run': datetime.now(),
                            'reason': 'N/A',
                            'ok': True
                        }
                    }
                }
            cls.routines[interval].append(routine)
            return # block external calls
        return wrapper

    @staticmethod
    def __get_lcm(nums):
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
        """__execute a function routine and handle errors"""
        for task in cls.routines[interval]:
            if cls.stopped(): return  # noqa: E701
            if not task['context']['runtime']['ok']: # there's a failed call
                continue
            #
            try:
                task['handler'](task['context'])
                task['context']['runtime']['last_run'] = datetime.now()
            except Exception as e:
                task['context']['runtime']['ok'] = False
                task['context']['runtime']['reason'] = str(e)
                raise # todo: handle errors without raising
        return

    #
    @classmethod
    def stopped(cls):
        """Check termination flag"""
        return cls.events.terminate.is_set()

