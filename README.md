# An Accelerometer Based MIDI Controller for Guitarists

This repository contains code for a custom MIDI controller made from a piece of pine wood, a Raspberry Pi 2, wearable Adafruit Flora and a LSM303 accelerometer module.

# Software

## Flora + Accelerometer

In this repository are two files, one that runs on an RPi and one that runs on an Adafruit Flora. The RPi and the Flora communicate through Serial Peripheral Interface (SPI) in order to coordinate.

Largely, the Processing code written for the Flora is repsonsible for interpreting the data from the LSM303 accelerometer module. This module can detect motion in X, Y and Z dimensions. In our case, a quick motion in the negative Y direction shifts the MIDI notes corresponding to the 4 frets physically present on the instrument up by 4 fret positions, as they would appear on a traditional guitar neck. A motion in the opposite direction shifts back down the "imaginary" guitar neck, so you are playing lower notes again. This is analogous to the octave up / down buttons you might find on an off-the-shelf MIDI controller.

A motion in the positive x direction is interpreted more granularly. After a cutoff, the extent to which the neck is moved upward in space corresponds to the pitch of a bend, like you might get by bending a string on a traditional guitar.

## Raspberry Pi

The Python code written for the RPi is responsible for fetching the position and any bend extent from the Flora over SPI. It is also responsible for decoding the current note(s) that are being played on the neck by combining information about the position, bend extent and signals read from the 6 strings. A high voltage is swept across each of the 4 frets in a time-multiplexed scanning pattern, and the voltage on each string is read in a loop. This allows us to find which note(s) are played at any given time, by virtue of the fact that both the frets and strings are conductive, and that they make contact when a string is pressed against the fretboard. The RPi behaves as a MIDI controller and starts / stops the corresponding notes accordingly.

To play the guitar, install `FluidSyth` and move the soundfont provided in `./midi_guitar_flora`, or whatever soundfont you like, onto the RPi.
Install `pulseaudio`. Then run:

```
fluidsynth -a alsa -m alsa_seq -g 1.0 <path_to_sf2>/60s_Rock_Guitar.SF2 &
```

Next, run `main.py` on the Pi.

# Project Status

> [!WARNING]  
> While the basics work, it is a little finicky to play. This software is provided with no guarantees or warranties of any kind.

# Photos

![signal-2025-12-29-210033](https://github.com/user-attachments/assets/33b4c451-1a4a-4857-acd1-b6221ea26c6a)

![signal-2025-12-29-210031](https://github.com/user-attachments/assets/96dcfaa6-8937-4e93-bdbb-2470fb5bc91c)

![signal-2025-12-29-210028](https://github.com/user-attachments/assets/cf7c0b90-d2d2-4f73-86f5-48594a28ce34)
