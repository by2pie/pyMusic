__author__ = 'johnnyeleven'

import numpy as np
import pyaudio

freqA4 = 440
half_step = 2.0**(1.0/12.0)
rate = 44100

def sine(freq, length):
    length = rate * length
    data = (float(freq) * np.pi*2)/rate
    return np.sin(np.arange(length) * data)

def harmonic(freq, length, n=1):
    har = 0
    for i in range(n):
        har += sine(freq * (i+1), length) * 1/(i+1)
    return har

a_note = harmonic(freqA4, 1)

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32, channels=1, rate=44100, output=1)
stream.write(a_note.astype(np.float32).tostring())
stream.close()
p.terminate()
