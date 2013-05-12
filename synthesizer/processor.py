import os
import math
import abc
import array
import numpy
from wave import *
from numpy.fft import *

C_NEG_1=8.176

class Processor(object):
    
    @abc.abstractmethod
    def process(self, start, steps, rate):
        return

    def __init__(self):
        pass


class Oscillator(Processor):
    
    @property
    def cv(self):
        return self._cv

    @cv.setter
    def cv(self, proc):
        self._cv=proc
        return self

    @property
    def amp(self):
        return self._amp

    @amp.setter
    def amp(self, amp):
        self._amp = amp
        return self

    @property
    def pw(self):
        return self._pw

    @pw.setter
    def pw(self, pw):
        self._pw = pw
        return self
    
    def __init__(self, wave):
        Processor.__init__(self)
        self._wave = wave

        self._cache = None
        if type(wave) == Const:
            self._use_cache = True
        else:
            self._use_cache = False

        self._cv = None
        self._amp = None
        self._pw = None

    def _volt_to_freq(self, v):
        return C_NEG_1*(2**v)

    def process(self, start, steps, rate):
        if self._cache:
            return self._cache

        fb = array.array('f')

        amp_fb = None
        if self.amp:
            amp_fb = self.amp.process(start, steps, rate)

        cv_fb = None
        if self.cv:
            cv_fb = self.cv.process(start, steps, rate)

        pw_fb = None
        if self.pw:
            pw_fb = self.pw.process(start, steps, rate)

        for t in range(steps):
            if cv_fb:
                self._wave.hz = self._volt_to_freq(cv_fb[t])
            if amp_fb:
                self._wave.amp = amp_fb[t]
            if pw_fb:
                self._wave.pw = pw_fb[t]

            fb.append(self._wave.compute(start + t/rate))

        if self._use_cache and not self._cache:
            self._cache = fb

        return fb


class Filter(Processor):

    @property
    def input(self):
        return self._in
    
    @input.setter
    def input(self, proc):
        self._in = proc
        return self
    
    def __init__(self, low, hi):
        Processor.__init__(self)
        self._low = low
        self._hi = hi
        self._w = 300
        self._in = None
    
    def hi_filter(self,f):
        if f > self._hi + self._w:
            return 0
        if f < self._hi - self._w:
            return 1
        return 1/2 * (1 - math.sin(math.pi*(f - self._hi)/2*self._w))

    def low_filter(self,f):
        if f < self._low - self._w:
            return 0
        if f > self._low + self._w:
            return 1
        return 1/2 * (1 - math.sin(math.pi*(self._low - f)/2*self._w))

    def process(self, start, steps, rate):
        if self.input:
            in_fb = self.input.process(start, steps, rate)
            fs = rfft(in_fb)
            freqs = fftfreq(len(fs), 1/float(rate))
            for i in range(len(fs)):
                    fs[i] = self.hi_filter(freqs[i])*fs[i]
                    fs[i] = self.low_filter(freqs[i])*fs[i]
            return irfft(fs)


class Mixer(Processor):

    @property
    def inputs(self):
        return self._inputs

    @property
    def weights(self):
        return self._weights

    @property
    def linear(self):
        return self._linear

    @linear.setter
    def linear(self, l):
        self._linear = l
    
    def __init__(self, linear=True):
        Processor.__init__(self)
        self._inputs = {}
        self._weights = {}
        self._linear = linear

    def process(self, start, steps, rate):
        fb = array.array('f')

        vals = []
        weights = []
        for k, v in self.inputs.items():
            vals.append(v.process(start,steps,rate))
            if k in self.weights:
                if self._linear:
                    weights.append(self.weights[k])
                else:
                    waights.append(math.log1p(math.e*self.weights[k]))
            else:
                weights.append(1)

        for i in range(steps):
            fb.append(0)

        for k in range(len(weights)):
            for i in range(steps):
                fb[i] = fb[i] + weights[k] * vals[k][i]

        return fb


