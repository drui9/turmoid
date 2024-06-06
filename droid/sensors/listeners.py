import math
import queue
from . import Sensors, listen

# --
def picked(interval=500):
    name = 'accelerometer'
    with listen(sensor=name, interval=interval):
        source = queue.Queue()
        @Sensors.evt.on(name)
        def read(_, y, z):
            source.put((y, z))
        # --
        while sensor := source.get():
            y, z = sensor
            if (y > 4.0) and (z < 8.0):
                return True

# --
def putdown(interval=500):
    name = 'accelerometer'
    with listen(sensor=name, interval=interval):
        source = queue.Queue()
        @Sensors.evt.on(name)
        def read(_, y, z):
            source.put((y, z))
        # --
        while sensor := source.get():
            y, z = sensor
            if (y < 1) and (z > 9):
                return True

# --
def shake(interval=400, threshold=20):
    name = 'accelerometer'
    with listen(sensor=name, interval=interval):
        source = queue.Queue()
        @Sensors.evt.on(name)
        def read(x, y, _):
            source.put((x, y))
        # --
        last = None
        while sensor := source.get():
            accel = math.sqrt(sum([math.pow(i, 2) for i in sensor]))
            if last == None:
                last = accel
                continue
            # --
            if (last < threshold) and (accel > threshold + 2):
                return True
            last = accel

# --
def flipped(interval=500):
    name = 'accelerometer'
    with listen(sensor=name, interval=interval):
        source = queue.Queue()
        @Sensors.evt.on(name)
        def read(_, __, z):
            source.put(z)
        # --
        last = None
        while True:
            sensor = source.get()
            if last == None:
                last = sensor
                continue
            # --
            if (sensor * (1 / last)) < - 0.8: # 90deg flip
                return True

# --
def dusk(high=10, low=5, interval=500):
    name = 'light'
    with listen(sensor=name, interval=interval):
        source = queue.Queue()
        @Sensors.evt.on(name)
        def read(value):
            source.put(value)
        # --
        highest = None
        while True:
            sensor = source.get()
            if highest == None:
                highest = sensor
                continue
            # --
            if (highest >= high) and (sensor <= low):
                return True
            highest = max(sensor, highest)

# --
def dawn(high=50, low=5, interval=500):
    name = 'light'
    with listen(sensor=name, interval=interval):
        source = queue.Queue()
        @Sensors.evt.on(name)
        def read(value):
            source.put(value)
        # --
        lowest = None
        while True:
            sensor = source.get()
            if lowest == None:
                lowest = sensor
                continue
            # --
            if (lowest <= low) and (sensor >= high):
                return True
            lowest = min(sensor, lowest)

# --
def proximal(interval=500):
    name = 'proximity'
    with listen(sensor=name, interval=interval):
        source = queue.Queue()
        @Sensors.evt.on(name)
        def read(value):
            source.put(value)
        # --
        prev = None
        while True:
            sensor = source.get()
            if prev == None:
                prev = sensor
                continue
            # --
            if sensor != prev:
                return True

