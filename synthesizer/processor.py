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

    @property
    def low(self):
        return self._low

    @low.setter
    def low(self, l):
        self._low = l
        return self
    
    @property
    def hi(self):
        return self._hi

    @hi.setter
    def hi(self, hi):
        self._hi = hi
        return self
    
    def __init__(self):
        Processor.__init__(self)
        self._low = None
        self._hi = None
        self._w = 200
        self._in = None
        self._ring = []
        self._curr = 0

    def _volt_to_freq(self, v):
        return (C_NEG_1)*(2**(v+10))
    
    def hi_filter(self,freq,cutoff):
        freq = math.fabs(freq)
        if freq >= cutoff:
            return 1
        return 2**float(freq-cutoff)
        #return 1/2 * (1 - math.sin(math.pi*(f - self._hi)/2*self._w))

    def low_filter(self,freq,cutoff):
        freq = math.fabs(freq)
        if freq <= cutoff:
            return 1
        return 2**float(cutoff-freq)
        #return 1/2 * (1 - math.sin(math.pi*(cutoff - freq)/2*self._w))

    def combine(self, fb, fb2, fb3):
        if not fb:
            return fb2
        fbc = array.array('f')
        for i in range(len(fb)):
            fbc.append(fb[i])
        for i in range(len(fb2)):
            fbc.append(fb2[i])
        for i in range(len(fb3)):
            fbc.append(fb3[i])
        return fbc

    def take_middle(self, fb, steps):
        fbr = array.array('f')
        for i in range(steps):
            fbr.append(fb[len(fb)-2*steps+i])
        return fbr

    def process(self, start, steps, rate):
        if self.input:
            low = None
            hi = None
            if self.low:
                low_fb = self.low.process(start, steps, rate)
                low = self._volt_to_freq(low_fb[int(steps/2)])
            if self.hi:
                hi_fb = self.hi.process(start, steps, rate)
                hi = self._volt_to_freq(hi_fb[int(steps/2)])
            in_fb = self.input.process(start, steps, rate)

            if len(self._ring) < 3:
                self._ring.append(in_fb)
                return [ 0 for _ in range(steps) ]

            self._ring[self._curr] = in_fb
            self._curr = (self._curr + 1) % 3

            in_fb = self.combine(self._ring[self._curr],self._ring[(self._curr+1)%3],self._ring[(self._curr+2)%3])

            fs = rfft(in_fb)
            freqs = fftfreq(len(fs), 1/float(rate))
            for i in range(len(fs)):
                if hi:
                    fs[i] = self.hi_filter(freqs[i], hi)*fs[i]
                if low:
                    fs[i] = self.low_filter(freqs[i], low)*fs[i]
            filtered =  irfft(fs)
            #return filtered
            return self.take_middle(filtered, steps)


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


class Sequencer(Processor):

    NOTES = ["c","c#","d","d#","e","f","f#","g","g#","a","b"]
    
    @property
    def clock(self):
        return self._clock

    @clock.setter
    def clock(self, c):
        self._clock = c

    @property
    def signals(self):
        return self._signals

    @signals.setter
    def signals(self, s):
        if type(s) is str:
            self.active = []
            self._signals = []
            note = None
            octave = None
            for i in range(len(s)):
                if s[i] == '#':
                    note = note + "#"
                elif s[i] == '_':
                    self.active.append(False)
                    self._signals.append(0)
                elif str(s[i]).isdigit():
                    octave = int(str(s[i]))
                else:
                    self._add_note(note, octave)
                    note = s[i]
            self._add_note(note, octave)
        else:
            self._signals = s

    def _add_note(self, note, octave):
        if note:
            if not octave:
                octave = 0
            index = None
            for j in range(len(Sequencer.NOTES)):
                if note == Sequencer.NOTES[j]:
                    index = j
            self._signals.append(octave+(1/12.0)*index)
            self.active.append(True)

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, a):
        self._active = a

    def __init__(self):
        Processor.__init__(self)
        self._clock = None
        self._signals = []
        self._active = []
        self._current = 0
        self._gate = 0.75
        self._low = True

    def process(self, start, steps, rate):
        fb = array.array('f')
        clock_fb = self._clock.process(start, steps, rate)
        
        for i in range(steps):
            if clock_fb[i] > self._gate:
                if self._low:
                    self._current = (self._current + 1) % len(self.signals)
                    self._low = False
            else:
                self._low = True
            
            if self._active[self._current]:
                fb.append(self.signals[self._current])
            else:
                fb.append(0)

        return fb
