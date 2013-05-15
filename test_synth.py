import time
import os
import math
from synthesizer.module import *
from synthesizer.hardware import *

#modules
vco = VCO()
lfo = LFO()
lfo2 = LFO()
lfo3 = LFO()

filter = Filter()

sequencer = Sequencer()

#hardware
speaker = Speaker()
scope = Scope()
keyboard = MidiKeyboard()

#knobs
lfo.range = 2
lfo.frequency = 10
vco.cv2_gain = 0.01

lfo2.range = 2
lfo2.frequency = 4

lfo3.range = 0
lfo3.frequence = 2
vco.pw_cv2_gain = 0.01

vco.range = 0
vco.tune = 5

#sequencer.signals = "e2_d#2_e2_d#2_e2_b2_d2_c2_a2_c2_a2_c2_"
#sequencer.signals = "g#1f#1e1d1e1d1c#1b1a1c1a1c1a1a1a1a1b1"
sequencer.signals = "c1c0c2c0g2c0c2c0c1c0c2c0g2c0c2c0c1c0c2c0g2c0c2c0c1c0c2c0c2c0c2c0"
sequencer.clock = lfo2.pulse

#patches
#vco.cv1 = keyboard
vco.cv1 = sequencer
#vco.cv1 = Oscillator(Const(5))
#vco.cv2 = lfo.sine
vco.pw_cv2 = lfo.sine

filter.low = lfo3.sine
#filter.low = Oscillator(Const(0))
filter.input = vco.triangle
#speaker.input = filter
speaker.input = vco.pulse

#scope.input = filter
#scope.start()

speaker.start()
while True:
    time.sleep(1)
#keyboard.start()
