import time
import math
from loguru import logger
from threading import Event
from datetime import datetime

#--
class Scheduler:
    activities = dict()
    #--
    @classmethod
    def add(cls, interval):
        def registrar(func):
            if interval not in cls.activities:
                cls.activities[interval] = list()
            cls.activities[interval].append({
                'handler': func,
                'context': {
                    'last-run': -1,
                    'ok': True
                }
            })
            return func
        return registrar
    #--
    @classmethod
    def __get_lcm(cls, nums):
        """Get the least common multiple of List[nums]"""
        gcd = math.gcd(*nums)
        return abs(math.prod(nums)) // gcd
    #--
    @staticmethod
    def __get_next(start, end, intervals):
        """Get the index of the upcoming routine handler"""
        index = -1
        if len(intervals) == 1:
            return intervals[0]
        # --
        found = False
        for i in range(start, end):
            for intv in intervals:
                if i % intv == 0:
                    index = i
                    found = True
                    break
            if found: break
        return index
    #--
    @classmethod
    def __execute(cls, interval):
        """Execute a function routine and handle errors"""
        for task in cls.activities[interval]:
            if not task['context']['ok']: # there's a failed call
                continue
            #--
            try:
                task['handler'](task['context'])
                task['context']['last_run'] = datetime.now()
                logger.debug(f'{task["handler"].__name__} completed.')
            except Exception as e:
                logger.exception('what?')
                task['context']['ok'] = False
                task['context']['reason'] = str(e) or type(e)
        return
    #--
    @classmethod
    def schedule(cls, terminate: Event):
        """Scheduled at intervals"""
        intervals = [i for i in sorted(cls.activities) if i > 0]
        if (not cls.activities) or (not intervals):
            return
        #--
        sleeptime = 0
        lcm = cls.__get_lcm(intervals)
        while not terminate.is_set():
            if sleeptime % lcm == 0:
                sleeptime = 0
            #-- do work
            for interval in intervals:
                if sleeptime % interval == 0:
                    cls.__execute(interval)
            #-- find timeout to next work & sleep
            nextv = cls.__get_next(sleeptime + 1, lcm + 1, intervals)
            timeout = nextv - sleeptime
            sleeptime += timeout
            yield timeout

