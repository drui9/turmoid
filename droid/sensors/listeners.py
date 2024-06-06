import math
import queue
from . import Sensors, accelerometer

# --
def picked(interval=500):
    with accelerometer(interval=interval):
        source = queue.Queue()
        @Sensors.evt.on('accelerometer')
        def read(_, y, z):
            source.put((y, z))
        # --
        while sensor := source.get():
            y, z = sensor
            print(y, z)
            if (y > 4.0) and (z < 8.0):
                return True

# --
def putdown(interval=500):
    with accelerometer(interval=interval):
        source = queue.Queue()
        @Sensors.evt.on('accelerometer')
        def read(_, y, z):
            source.put((y, z))
        # --
        while sensor := source.get():
            y, z = sensor
            if (y < 1) and (z > 9):
                return True

# --
def shake(interval=400, threshold=20):
    with accelerometer(interval=interval):
        source = queue.Queue()
        @Sensors.evt.on('accelerometer')
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

