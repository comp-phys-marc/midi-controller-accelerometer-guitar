import spidev
import time
import board
import digitalio
import usb_midi
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff

# TODO: calibrate bend multiplier
MULTIPLIER = 1 / 50

position = 0
bend = 0

# SPI SETUP

CE0 = board.GP10
CE1 = board.GP11
MOSI = board.PG12
MISO = board.GP13
SCLK = board.GP14

# Open SPI bus 0, device (CS) 0
spi = spidev.SpiDev()
spi.open(0, 0)

# Set SPI speed and mode
spi.max_speed_hz = 50000
spi.mode = 0

#  MIDI setup as MIDI out device
midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)

fret_pins = [
    board.GP26,
    board.GP27,
    board.GP28,
    board.GP29
]

string_pins = [
    board.GP0,
    board.GP2,
    board.GP3,
    board.GP1,
    board.GP4,
    board.GP5
]

string_inputs = []

for pin in string_pins:
    string_pin = digitalio.DigitalInOut(pin)
    string_pin.direction = digitalio.Direction.INPUT
    string_pin.pull = digitalio.Pull.UP
    string_inputs.append(string_pin)

fret_outputs = []

for pin in fret_pins:
    fret_pin = digitalio.DigitalInOut(pin)
    fret_pin.direction = digitalio.Direction.OUTPUT
    fret_pin.pull = digitalio.Pull.UP
    fret_outputs.append(fret_pin)

# array of default MIDI notes
midi_notes = [
    # 40,  # open E
    41,  # F
    42,  # F#
    43,  # G
    44,  # G#
    # 45, open A
    46,  # A#
    47,  # B
    48,  # C
    49,  # C#
    # 50, open D
    51,  # D#
    52,  # E
    53,  # F
    54,  # F#
    # 55, open G
    56,  # G#
    57,  # A
    58,  # A#
    59,  # B
    # 59, open B
    60,  # middle C
    61,  # C#
    62,  # D
    63,  # D#
    # 64, open E
    65,  # F
    66,  # F#
    67,  # G
    68   # G#
]

try:
    low_pos = -1
    fret_found = [
        [False, False, False, False],
        [False, False, False, False],
        [False, False, False, False],
        [False, False, False, False],
        [False, False, False, False],
        [False, False, False, False]
    ]

    while True:
        # Debounce
        time.sleep(0.1)

        # Write a new fret low, or advance to final step
        low_pos = (low_pos + 1) % 5

        if low_pos == 4:
            last_fret_found = fret_found

            # We have completed a scan
            # Here we check if multiple fret positions are contacted,
            # or if multiple notes are played i.e. in a chord

            # Read from SPI twice
            read_one = ord(spi.xfer2(["/r"]))
            read_two = ord(spi.xfer2(["/r"]))

            # Figure out which response is position and which is bend
            if (0 <= read_one <= 5):
                bend = read_two
                position = read_one
            elif (6 <= read_one <= 100):
                bend = read_one
                position = read_two

            # Check for multiple fret contacts
            note_indices = []

            for i in range(6):
                j = 0

                # Find right-most contact for a string
                max_high = -1
                while j < 4:
                    if fret_found[i][j] and j > max_high:
                        max_high = j
                    j += 1

                # Remove irrelevant contacts (probably the one immediately to the left)
                for k in range(4):
                    if k == max_high:
                        fret_found[i][k] = True
                    else:
                        fret_found[i][k] = False

                if last_fret_found[i][max_high] == False and fret_found[i][max_high] == True:
                    # Calculate the played note index (without position, bend)
                    note_indices.append(i * 4 + max_high)

            # If a note is pressed...
            for note_index in note_indices:
                # send the MIDI note, modified by neck position and any bend
                midi.send(NoteOn(midi_notes[i] + 3 * position + bend * MULTIPLIER, 120))

            # If a string is released...
            for i in range(6):
                for j in range(4):
                    if last_fret_found[i][j] == True and fret_found[i][j] == False:
                        # stop sending the MIDI note
                        midi.send(NoteOff(midi_notes[i] + 3 * position + bend * MULTIPLIER, 120))

        else:
            # Scan to next fret
            pos = 0
            for fret_pin in fret_pins:
                if pos == low_pos:
                    fret_pin.value = False
                else:
                    fret_pin.value = True

            # Read the input from the mini guitar neck (float high, active low, due to pull-up)
            for i in range(6):
                input = string_inputs[i]
                if not input.value:
                    fret_found[i][low_pos] = True

except KeyboardInterrupt:
    spi.close()
