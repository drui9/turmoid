import math
from loguru import logger
from threading import Lock, Thread, Event

# --
class ScheduleError(Exception):
    pass

#--
class Scheduler:
    activities = {
        'lock': Lock(),
        'changed': Event(),
        'handlers': dict()
    }
    # <> add interval task
    @classmethod
    def add(cls, interval, desc: str="<Task/>"):
        def registrar(func):
            with cls.activities['lock']:
                if interval not in cls.activities['handlers']:
                    cls.activities['handlers'][interval] = dict()
                    cls.activities['changed'].set()
                cls.activities['handlers'][interval] |= {
                    func.__name__ : {
                        'handler': func,
                        'description': desc
                    }
                }
                return func
        return registrar
    #</>
    #<> show registered tasks
    @classmethod
    def show(cls):
        out = dict()
        with cls.activities['lock']:
            for interval in cls.activities['handlers']:
                for name, task in cls.activities['handlers'][interval].items():
                    out |= {
                        name: {
                            'description': task['description'],
                            'interval': interval,
                            'context-keys': list(task['context'].keys())
                        }
                    }
        return out
    #</>
    # <> remove a registered task
    @classmethod
    def remove(cls, name):
        with cls.activities['lock']:
            locate = list()
            ejected = list()
            for interval in cls.activities['handlers']:
                if name in cls.activities['handlers'][interval]:
                    locate.append(interval)
            for interval in locate:
                out = cls.activities['handlers'][interval].pop(name)
                ejected.append(out)
                if not cls.activities['handlers'][interval]:
                    cls.activities['handlers'].pop(interval)
                    cls.activities['changed'].set()
            return ejected
    #</>
    # <> lcm, get_next
    @classmethod
    def __get_lcm(cls, nums):
        """Get the least common multiple of List[nums]"""
        gcd = math.gcd(*nums)
        return abs(math.prod(nums)) // gcd
    #--
    @staticmethod
    def __get_next(start, end, intervals):
        """Get the index of the upcoming routine handler"""
        if len(intervals) == 1:
            return intervals[0]
        # --
        for i in range(start, end):
            for intv in intervals:
                if i % intv == 0:
                    return i
        return -1
    # </>
    @classmethod
    def __execute(cls, interval, app):
        """Execute a function routine and handle errors"""
        # <>
        assert (not cls.activities['lock'].locked())
        with cls.activities['lock']:
            for key, task in cls.activities['handlers'][interval].items():
                try:
                    task['handler'](app)
                except Exception as e:
                    e.add_note(f'Schedule item: {key}')
                    logger.exception('what?')
        # </>
        return
    #--
    @classmethod
    def schedule(cls, main):
        """Scheduled at intervals"""
        # <>
        cls.activities['changed'].set()
        lcm = -1
        sleeptime = 0
        intervals = list()
        while not main.terminate.is_set():
            if cls.activities['changed'].is_set():
                with cls.activities['lock']:
                    intervals = [i for i in sorted(cls.activities['handlers']) if i > 0]
                    if (not cls.activities['handlers']) or (not intervals):
                        raise ScheduleError('No schedules!')
                    lcm = cls.__get_lcm(intervals)
                    cls.activities['changed'].clear()
            if sleeptime % lcm == 0:
                sleeptime = 0
            #-- do work
            for interval in intervals:
                if sleeptime % interval == 0:
                    cls.__execute(interval, main)
            #-- find timeout to next work & sleep
            nextv = cls.__get_next(sleeptime + 1, lcm + 1, intervals)
            timeout = nextv - sleeptime
            sleeptime += timeout
            yield timeout
        # </>
        return

