import os
import math
import array
import numpy
from processor import *
from wave import *

class LFO(Processor):
    
    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, t):
        if 0 <= t <= 10:
            self._set_adder_input('frequency',Oscillator(Const(4*t/10.0)),1)
            self._frequency = t

    @property
    def range(self):
        return self._range

    @range.setter
    def range(self, r):
        r = int(r)
        if 0 <= r <= 2:
            self._set_adder_input('range',Oscillator(Const(2*r-6)),1)
            self._range = r

    @property
    def saw(self):
        return self._outputs['saw']

    @property
    def pulse(self):
        return self._outputs['pulse']

    @property
    def triangle(self):
        return self._outputs['triangle']

    @property
    def sine(self):
        return self._outputs['sine']

    def _set_adder_input(self, name, proc, weight):
        for v in self._outputs.values():
            a = v.cv
            if type(a) == Mixer:
                a.inputs[name] = proc
                a.weights[name] = weight
    
    def __init__(self):
        Processor.__init__(self)
        self._outputs = {}
        self._outputs['saw'] = Oscillator(Saw())
        self._outputs['pulse'] = Oscillator(Pulse())
        self._outputs['triangle'] = Oscillator(Triangle())
        self._outputs['sine'] = Oscillator(Sine())

        for k, v in self._outputs.items():
            v.cv = Mixer()
            v.amp = Oscillator(Const(2.5))

        self.range = 1
        self.frequency = 5


class VCO(Processor):
    
    @property
    def outputs(self):
        return self._outputs

    @property
    def tune(self):
        return self._tune

    @tune.setter
    def tune(self, t):
        if 0 <= t <= 10:
            self._set_adder_input('tune',Oscillator(Const((t-5)/10.0)),1)
            self._tune = t

    @property
    def range(self):
        return self._range

    @range.setter
    def range(self, r):
        r = int(r)
        if -2 <= r <= 2:
            self._set_adder_input('range',Oscillator(Const(r+2)),1)
            self._range = r

    @property
    def pw(self):
        return self._pw

    @pw.setter
    def pw(self, pw):
        if 0 <= pw <= 10:
            self._set_pw_adder_input('pw',Oscillator(Const(pw/10.0)),1)
            self._pw = pw

    @property
    def cv1(self):
        return self._cv1
    
    @cv1.setter
    def cv1(self, proc):
        self._cv1 = proc
        self._set_adder_input('cv1',proc,1)
        return self

    @property
    def cv2(self):
        return self._cv2
    
    @cv2.setter
    def cv2(self, proc):
        self._cv2 = proc
        self._set_adder_input('cv2',proc,self.cv2_gain)
        return self

    @property
    def cv2_gain(self):
        return self._cv2_gain

    @cv2_gain.setter
    def cv2_gain(self, gain):
        self._cv2_gain = gain
        for v in self._outputs.values():
            a = v.cv
            if type(a) == Mixer:
                a.weights['cv2'] = gain

    @property
    def pw_cv1(self):
        return self._pw_cv1
    
    @pw_cv1.setter
    def pw_cv1(self, proc):
        self._pw_cv1 = proc
        self._set_pw_adder_input('cv1',proc,1)
        return self

    @property
    def pw_cv2(self):
        return self._cv2
    
    @pw_cv2.setter
    def pw_cv2(self, proc):
        self._pw_cv2 = proc
        self._set_pw_adder_input('cv2',proc,self.pw_cv2_gain)
        return self

    @property
    def pw_cv2_gain(self):
        return self._pw_cv2_gain

    @pw_cv2_gain.setter
    def pw_cv2_gain(self, gain):
        self._pw_cv2_gain = gain
        for v in self._outputs.values():
            a = v.pw
            if type(a) == Mixer:
                a.weights['cv2'] = gain

    @property
    def saw(self):
        return self._outputs['saw']

    @property
    def pulse(self):
        return self._outputs['pulse']

    @property
    def triangle(self):
        return self._outputs['triangle']

    @property
    def sine(self):
        return self._outputs['sine']

    def _set_adder_input(self, name, proc, weight):
        for v in self._outputs.values():
            a = v.cv
            if type(a) == Mixer:
                a.inputs[name] = proc
                a.weights[name] = weight

    def _set_pw_adder_input(self, name, proc, weight):
        for v in self._outputs.values():
            a = v.pw
            if type(a) == Mixer:
                a.inputs[name] = proc
                a.weights[name] = weight
    
    def __init__(self):
        Processor.__init__(self)
        self._outputs = {}
        self._outputs['saw'] = Oscillator(Saw())
        self._outputs['pulse'] = Oscillator(Pulse())
        self._outputs['triangle'] = Oscillator(Triangle())
        self._outputs['sine'] = Oscillator(Sine())

        for k, v in self._outputs.items():
            v.cv = Mixer()
            v.pw = Mixer()

        self.range = 0
        self.tune = 5
        self.pw = 5
        self.cv2_gain = 5
        self.pw_cv2_gain = 5

