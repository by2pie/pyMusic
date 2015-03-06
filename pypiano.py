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
    """ Class responsible for changing note into object with length and freq
    """
    NOTES = {'c': 1, 'c#': 2, 'd': 3, 'd#': 4, 'e': 5, 'f': 6, 'f#': 7, 'g': 7, 'g#': 8, 'a': 9, 'a#': 10, 'b': 11,
             'p': 12}   # associative array changing note to number (lookuptable)

    def __init__(self, notes, octave, length):
        """Constructor for Note class
        Keyword arguments:
        notes -- string descibing note
        octave -- int base octave 1-8
        length -- float measure of note(note length)
        """
        self.note = self.NOTES[notes]   # decoding string note name
        self.length = length
        self.octave = octave
        self.freq = self.get_freq()

    def get_freq(self):
        """Get a frequancy appropriate for given note
        return
        frequency - frequency of note
        """
        if self.note == 12:     #if pause
            return 0
        else:                   #not pause
            n = self.note - 9 + 12 * (self.octave - 4)  # number of steps between given note and A440
            return 440 * half_step ** n  # frequency of note


class Musicpiece:
    """Class responsible for representing given musicpiece containg notes"""
    def __init__(self, score_right, score_left, octave, unit=1.0, tempo=1.0):
        """Constructor for Musicpiece class
        Keyword arguments:
        score_right -- string notes for right hand separated by space
        score_left -- string notes for left hand separated by space
        octave -- int base octave 1-8
        unit -- float shortest note length
        tempo -- float adjustable music tempo
        """
        self.unit = unit / tempo
        self.melody = np.array(())
        self.octave = octave
        self.notes_right = self.set_notes(score_right)
        self.notes_left = self.set_notes(score_left)
        self.set_melody()

    def set_notes(self, score):
        """Get list of notes from given score

        Keyword arguments:
        score - string of notes sperated by spaces
        """
        note_list = score.split()    #  spliting long string containing notes separated by space
        notes = []
        for note in note_list:       #  saving notes to a list containg objects of class Note
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
        """Seting melody from lists of separated notes, also linking right hand with left one
        """
        right = []
        left = []
        for note in self.notes_right:
            right.append(modulate(harmonic(note, 8)))
        for note in self.notes_left:
            left.append(modulate(harmonic(note, 8)))
        self.melody = np.concatenate(right) * 0.1 + np.concatenate(left) * 0.2

    def get_melody(self):

        """returning melody
        """

        return self.melody

def sine(freq, length):
    """Function generating sine function of given length and frequency

        Keyword arguments:
        freq - frequency of osccilations
        length - length of sine function in seconds
    """
    length *= rate   #  length multiply by rate which is a number of points per second
    data = (float(freq) * np.pi*2)/rate
    return np.sin(np.arange(length) * data)

def harmonic(note, n=1):
    """Function generating set of nth first harmonics for note

        Keyword arguments:
        note - object of class note
        n - number of harmonics (default = 1)
    """
    har = 0
    for i in range(n):
        har += sine(note.freq * (i+1), note.length) * 1/(i+1)   # each harmonics added with a factor of 1/n
    return har

def modulate(signal, type=modulator):
    """Modulating tone of voice to make it sound more instrumental

        Keyword arguments:
        signal - sine-like function to modulate
        type - points on which we interpolate modulating function
    """
    f = interp1d(np.linspace(0, len(signal), len(type)), type, kind='cubic')    #interpolating using cubic function
    x = np.arange(len(signal))  # linespace
    return abs(f(x)) * signal   # modulating itself

#--------------------------------------------------------------------------------------------------
"""
Notes read from sheet music
It is by default set as set of few signs:
note -> <octave><note><length relative to shortest one>
example: 1a2 = first octave a-note twice as long as unit
"""

music_notes_right = '2e 2d# 2e 2d# 2e 1b 2d 2c 1a2 0p 1c 1e 1a 1b2 0p 1e 1g# 1b 2c2 0p 1e 2e 2d# 2e 2d# 2e 1b 2d 2c ' \
                    '1a2, 0p 1c 1e 1a 1b2 0p 1e 2c 1b 1a2 0p 1b 2c 2d 2e3 1g 2f 2e 2d3 1f 2e 2d 2c3 1e 2d 2c 1b3 1b3'
music_notes_left = '0p2 0p6 0f 1c 1f 0p3 0c 1c 1e# 0p3 0f 1c 1f 0p3 0p48'

#creating fur Elise object
furElise = Musicpiece(music_notes_right, music_notes_left, 2, unit=1.0, tempo=4.0)

#script playing furElise using pyAudio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32, channels=1, rate=44100, output=1)
stream.write(furElise.get_melody().astype(np.float32).tostring())
stream.close()
p.terminate()
