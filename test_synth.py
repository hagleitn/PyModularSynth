import os
import math
from synthesizer.module import *
from synthesizer.hardware import *

#modules
vco = VCO()
lfo = LFO()
lfo2 = LFO()

filter = Filter(-6000, 3000)

#hardware
speaker = Speaker()
scope = Scope()
keyboard = MidiKeyboard()

#knobs
lfo.range = 2
lfo.frequency = 5
vco.cv2_gain = 0.01

lfo2.range = 2
lfo2.frequency = 5
vco.pw_cv2_gain = 0.01

vco.range = 0
vco.tune = 5

#patches
vco.cv1 = keyboard
vco.cv2 = lfo.sine
#vco.pw_cv2 = lfo2.sine

#speaker.input = filter.input = vco.pulse
speaker.input = vco.sine

scope.input = vco.pulse
#scope.start()

speaker.start()
keyboard.start()
