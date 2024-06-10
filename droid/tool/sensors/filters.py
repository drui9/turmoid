import math
from .sensor import Sensor

#--
@Sensor.filter('light')
def dawn(source, high=10, low=5):
    lowest = None
    for sensor in source:
        light = sensor[-1]
        if lowest == None:
            lowest = light
            continue
        # --
        lowest = min(lowest, light)
        if (lowest < low) and (light >= high):
            lowest = light
            yield 'droid.sensor.DAWN'
            continue
        yield sensor

# --
@Sensor.filter('light')
def dusk(source, high=10, low=5):
    highest = None
    for sensor in source:
        light = sensor[-1]
        if highest == None:
            highest = light
            continue
        # --
        highest = max(highest, light)
        if (highest >= high) and (light <= low):
            highest = light
            yield 'droid.sensor.DUSK'
            continue
        highest = max(light, highest)
        yield sensor

#--
@Sensor.filter('proximity')
def proximal(values):
    prev = None
    for sensor in values:
        proximity = sensor[0]
        if prev == None:
            prev = proximity
            continue
        # --
        if proximity != prev:
            prev = proximity
            if proximity == 0:
                yield 'droid.sensor.NEAR'
            else:
                yield 'droid.sensor.FAR'
        yield sensor

#--
@Sensor.filter('accelerometer')
def held(source):
    prev = None
    for sensor in source:
        _, y, z = sensor
        y, z = abs(y), abs(z)
        if (y > 4.0) and (z < 8.0):
            if prev == None:
                prev = 1
                continue
            if prev != 1:
                prev = 1
                yield 'droid.sensor.PICKED'
                continue
        elif (y < 1) and (z > 9):
            if prev == None:
                prev = -1
                continue
            if prev != -1:
                prev = -1
                yield 'droid.sensor.PUTDOWN'
                continue
        yield sensor

# --
@Sensor.filter('accelerometer')
def shake(source, threshold=20):
    last = None
    for sensor in source:
        accel = math.sqrt(sum([math.pow(i, 2) for i in sensor]))
        if last == None:
            last = accel
            continue
        # --
        if (last < threshold) and (accel > threshold + 2):
            yield 'droid.sensor.SHAKE'
        last = accel
        yield sensor

# --
@Sensor.filter('accelerometer')
def flipped(source):
    last = None
    for sensor in source:
        if last == None:
            last = sensor
            continue
        # --
        if (sensor * (1 / last)) < - 0.8: # 90deg flip
            yield 'droid.sensor.FLIPPED'
        yield sensor

