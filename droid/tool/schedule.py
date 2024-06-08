import time
import math
from loguru import logger
from datetime import datetime


class Scheduler:
    activities = dict()
    #
    @classmethod
    def __get_lcm(cls, nums):
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
                logger.debug(f'{task["handler"].__name__} completed.')
            except Exception as e:
                logger.exception('what?')
                task['context']['ok'] = False
                task['context']['reason'] = str(e) or type(e)
        return

    @classmethod
    def schedule(cls):
        """ 1+ -> Scheduled at intervals"""
        """ -1 -> Restroom while (x < -1) -> complements to (|x| - 1)"""
        intervals = [i for i in sorted(cls.activities) if i > 0]
        #
        if (not cls.activities) or (not intervals):
            return
        #
        lcm = cls.__get_lcm(intervals)
        sleeptime = 0
        #
        logger.info('Starting scheduler...')
        while True:
            logger.debug('Scheduler cycle started...')
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
            logger.debug(f'Sleeptime({timeout})')
            time.sleep(timeout)

