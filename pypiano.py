__author__ = 'johnnyeleven'


import numpy as np
import matplotlib.pyplot as plt
import pyaudio
from scipy.interpolate import interp1d


freqA4 = 440    # fundamental freq of A440
half_step = 2.0**(1.0/12.0)  # numerical half-step
rate = 44100    # changing digital data to analogue
modulator = np.array((0.5, 0.7, 0.9, 1.0, 0.4, 0.5, 0.5, 0.5, 0.4, 0.4))   # violin?
#modulator = np.array((1.0, 0.8, 0.6, 0.4, 0.2))  # piano


class Note:

    NOTES = {'c': 1, 'c#': 2, 'd': 3, 'd#': 4, 'e': 5, 'f': 6, 'f#': 7, 'g': 7, 'g#': 8, 'a': 9, 'a#': 10, 'b': 11,
             'p': 12}

    def __init__(self, notes, octave, length):
        self.note = self.NOTES[notes]
        self.length = length
        self.octave = octave
        self.freq = self.get_freq()

    def get_freq(self):
        if self.note == 12:
            return 0  # pause
        else:
            n = self.note - 9 + 12 * (self.octave - 4)
            return 440 * half_step ** n  # other note


class Musicpiece:

    def __init__(self, score_right, score_left, octave, unit=1.0, tempo=1.0):
        self.unit = unit / tempo
        self.melody = np.array(())
        self.octave = octave
        self.notes_right = self.set_notes(score_right)
        self.notes_left = self.set_notes(score_left)
        self.set_melody()

    def set_notes(self, score):
        note_list = score.split()
        notes = []
        for note in note_list:
            print(note)
            if len(note) == 2:
                notes.append(Note(note[1:], self.octave+int(note[0]), self.unit))
            elif len(note) == 3:
                if note[2] == '#':
                    notes.append(Note(note[1:2], self.octave+int(note[0]), self.unit))
                else:
                    notes.append(Note(note[1], self.octave+int(note[0]), self.unit * float(note[2:])))
            else:
                if note[2] == '#':
                    notes.append(Note(note[1:2], self.octave+int(note[0]), self.unit * float(note[3:])))
                else:
                    notes.append(Note(note[1], self.octave+int(note[0]), self.unit * float(note[2:])))
        return notes

    def set_melody(self):
        right = []
        left = []
        for note in self.notes_right:
            right.append(modulate(harmonic(note, 8)))
        for note in self.notes_left:
            left.append(modulate(harmonic(note, 8)))
        self.melody = np.concatenate(right) * 0.1 + np.concatenate(left) * 0.2

    def get_melody(self):
        return self.melody

def sine(freq, length):
    length *= rate
    data = (float(freq) * np.pi*2)/rate
    return np.sin(np.arange(length) * data)

def harmonic(note, n=1):
    har = 0
    for i in range(n):
        har += sine(note.freq * (i+1), note.length) * 1/(i+1)
    return har

def modulate(signal, type=modulator):
    f = interp1d(np.linspace(0, len(signal), len(type)), type, kind='cubic')
    x = np.arange(len(signal))
    return abs(f(x)) * signal

music_notes_right = '2e 2d# 2e 2d# 2e 1b 2d 2c 1a2 0p 1c 1e 1a 1b2 0p 1e 1g# 1b 2c2 0p 1e 2e 2d# 2e 2d# 2e 1b 2d 2c 1a2' \
              ' 0p 1c 1e 1a 1b2 0p 1e 2c 1b 1a2 0p 1b 2c 2d 2e3 1g 2f 2e 2d3 1f 2e 2d 2c3 1e 2d 2c 1b3 1b3'
music_notes_left = '0p2 0p6 0f 1c 1f 0p3 0c 1c 1e# 0p3 0f 1c 1f 0p3 0p48'

furElise = Musicpiece(music_notes_right, music_notes_left, 2, unit=1.0, tempo=4.0)

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32, channels=1, rate=44100, output=1)
stream.write(furElise.get_melody().astype(np.float32).tostring())
stream.close()
p.terminate()
