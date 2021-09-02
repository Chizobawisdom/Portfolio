#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 29 15:40:33 2021

@author: Chizoba Wisdom Favour

@description: This program is building a music sheet player using simpleaudio

"""
# Declaration


import numpy as np  # numpy array for numerical calculations
import simpleaudio as sa  # simple audio module that plays a numpy array

fs = 44100  # 44100 samples per second
noteFreq = {
    "3A": 880.00, "3G": 783.99, "6A": 1760, "6F": 1397, "6G": 1568, "6C": 1047
}  # standard note frequencies for specific notes , where 3A is A5, 3G is G5


# Input
notes = [
    ["6A", 2], ["6G", 2], ["6F", 2], ["6G", 2], ["6A", 2], ["6A", 2], ["6A", 2],
    ["3G", 2], ["3G", 2], ["3G", 2], ["6A", 2], ["6C", 2], ["6C", 2], ["6A", 2],
    ["6G", 2], ["6F", 2], ["6G", 2], ["6A", 2], ["6A", 2], ["6A", 2], ["6A", 2],
    ["3G", 2], ["3G", 2], ["3A", 2], ["3G", 2], ["6F", 1]]
# score for mary had a little lamb


# Processing
freq = []

for sublist in notes:
    freq.append(sublist[0])
# print(freq)
for i in freq:
    f1 = noteFreq.get(i)  # to fetch frequencies from noteFreq  using notes as keys
    print(f1)

beats = []
for sublist in notes:
    beats.append(sublist[1])
for i in beats:
    d = i
    # print(d)  # tone duration in seconds


def createNote(f1, d):  # function to create a music note using sine wave
    td = d / 2
    sd = 100e-3  # space duration in seconds

    # Generate array with (td*fs) steps, ranging between 0 and td
    tv = np.linspace(0, td, int(td * fs), False)

    # Generate sine wave
    tone = np.sin(2 * np.pi * f1 * tv)

    # Generate space, an array with (sd*fs) steps, of of 0-s  = ranging between 0 and 0
    space_tone = np.linspace(0, 0, int(sd * fs), False)

    dtone_space = np.concatenate((tone, space_tone))

    # Ensure that highest value is in 16-bit range
    dtone_seq = dtone_space * (2**15 - 1) / np.max(np.abs(dtone_space))

    # Convert to 16-bit data
    return dtone_seq.astype(np.int16)

key_tones = np.array([])  # function to play notes according to arrangement in notes

for i in freq:
    next_dtone = createNote(noteFreq.get(i), d)
    if len(key_tones) != 0:
        key_tones = np.concatenate((key_tones, next_dtone))
    else:
        key_tones = next_dtone


# Output


play_obj = sa.play_buffer(key_tones, 1, 2, fs)  # Start playback

play_obj.wait_done()  # Wait for playback to finish before exiting
