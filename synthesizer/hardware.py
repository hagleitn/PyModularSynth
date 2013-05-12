import threading
import Tkinter as tk
import pyaudio
import struct
import time
import sys
from processor import *
from wave import *
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation


class Speaker(Processor):
    
    @property
    def input(self):
        return self._input

    @input.setter
    def input(self, input):
        self._input = input

    def __init__(self):
        Processor.__init__(self)
        self.input = Oscillator(Const(0))
        self._p = pyaudio.PyAudio()
        # self._rate = 44100
        self._rate = 22050
        self._count = 0

    def callback(self, in_data, frame_count, time_info, status):
        self._count = self._count + 1
        #if self._count % 100 == 0:
        #    print self._stream.get_cpu_load()
        data = self.input.process(time_info['output_buffer_dac_time'], frame_count, float(self._rate))
        data = struct.pack('%sf' % len(data), *data)
        return (data, pyaudio.paContinue)

    def start(self):
        self._stream = self._p.open(format=pyaudio.paFloat32,
                                    channels=1,
                                    frames_per_buffer=1024,
                                    rate=self._rate,
                                    output=True,
                                    stream_callback=self.callback)

        
        self._stream.start_stream()
        
#        while self._stream.is_active():
#            time.sleep(0.1)

    def stop(self):
        self._stream.stop_stream()
        self._stream.close()
            
        self._p.terminate()
            

class Scope(Processor):

    @property
    def input(self):
        return self._input

    @input.setter
    def input(self, proc):
        self._input = proc

    def __init__(self):
        Processor.__init__(self)
        self.input = Oscillator(Const(0))
        self._rate = 41000.0
        self._count = 0
        self._num_frames = 1024

    def start(self):
        x = np.linspace(0,10,self._num_frames,endpoint=True)
        y = np.sin(x)

        fig = plt.figure()
        plot, = plt.plot(x,y)
        plt.xlim(-0.1,10.1)
        plt.ylim(-2.6,2.6)
        ani = animation.FuncAnimation(fig, self.callback, frames=xrange(self._num_frames),fargs=(x,plot), interval=100)
        #threading.Thread(target = plt.show).start()
        plt.show()
        return ani


    def callback(self, i, x, plot):
        y = self.input.process(i*self._num_frames/self._rate, self._num_frames, self._rate)
        plot.set_ydata(y)
        return plot,


class MidiKeyboard(Processor):
    
    def __init__(self):
        Processor.__init__(self)
        self._keys = ['a','w','s','e','d','f','t','g','y','h','u','j','k','o','l','p',';','\'']
        self._key = None
        self._octave = 3
        self._voltages = {}
        for i in range(len(self._keys)):
            self._voltages[self._keys[i]] = i * (1/12.0)

    def process(self, start, steps, rate):
        fb = array.array('f')
        if self._key in self._voltages:
            v = self._octave + self._voltages[self._key]
        else:
            v = self._octave

        for i in range(steps):
            fb.append(v)

        return fb

    def keypress(self, event):
        if event.keysym == 'Escape' or event.char == 'c':
            self._root.destroy()
        self._key = event.char
    
    def start(self):
        self._root = tk.Tk()
        print "Press a key (Escape key to exit):"
        self._root.bind_all('<Key>', self.keypress)
        
        #self._root.withdraw()
        #threading.Thread(target=self._root.mainloop).start()
        self._root.mainloop()

