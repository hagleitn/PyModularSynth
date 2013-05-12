import os
import math
import random
import abc


class Wave(object):

    @property
    def hz(self):
        return self._hz

    @hz.setter
    def hz(self, hz):
        self._hz = hz

    @property
    def amp(self):
        return self._amp

    @amp.setter
    def amp(self, amp):
        self._amp = math.fabs(amp)


    @property
    def pw(self):
        return self._pw

    @pw.setter
    def pw(self, pw):
        self._pw = pw
    
    def __init__(self):
        self.amp = 1
        self.hz = 440
        self._time = None
        self._last_time = None
        self._pw = 0.5

    def compute(self, time):
        if self._time == None:
            self._time = time
            self._last_time = time
        else:
            self._time = self._time + self.hz * (time - self._last_time)
            self._last_time = time
        self._time = self._time % 1
        return self._compute(self._time)

    @abc.abstractmethod
    def _compute(self, time):
        return


class Triangle(Wave):
    
    def _compute(self, time):
        if time < 0.5:
            return self.amp * (1-4*time)
        else:
            return self.amp*(-1 + 4 * (time-0.5))


class Noise(Wave):
    
    def _compute(self, time):
        return self.amp*random.random()*2-1


class Saw(Wave):
    
    def _compute(self, time):
        return self.amp * (1 - 2*time)


class Sine(Wave):
    
    def _compute(self, time):
        return self.amp*math.sin(2*math.pi*time)


class Square(Wave):
    
    def _compute(self, time):
        if time < 0.5:
            return -self.amp
        else:
            return self.amp

class Pulse(Wave):
    
    def _compute(self, time):
        if time < self.pw:
            return self.amp
        else:
            return -self.amp

class Const(Wave):

    @property
    def val(self):
        return self._val

    @val.setter
    def val(self, v):
        self._val = v
        return

    def __init__(self, val):
        Wave.__init__(self)
        self.val = val
    
    def _compute(self, time):
        return self.val
