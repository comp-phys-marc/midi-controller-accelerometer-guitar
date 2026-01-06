import spidev
import time
import copy
import mido
import RPi.GPIO as gpio

#  MIDI setup as MIDI out device
midi_ports = mido.get_output_names()
print("Available MIDI output ports:", midi_ports)

found = False
for port in midi_ports:
    if 'fluid' in port.lower():
        found = True
        try:
            midi = mido.open_output(port) 
        except IOError:
            print("Could not open FluidSynth port. Make sure fluidsynth is running.")
            exit()
     
if not found:
    print("Could not find FluidSynth port. Make sure fluidsynth is running.")
    exit()
            
gpio.setmode(gpio.BOARD)

fret_pins = [
    32,
    36,
    31,
    33
]

string_pins = [
    11,
    13,
    15,
    12,
    16,
    18
]

string_inputs = []

for pin in string_pins:
    gpio.setup(pin, gpio.IN, pull_up_down=gpio.PUD_DOWN)
    string_inputs.append(pin)

fret_outputs = []

for pin in fret_pins:
    gpio.setup(pin, gpio.OUT)
    fret_outputs.append(pin)

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
    high_pos = -1
    fret_found = [
        [False, False, False, False],
        [False, False, False, False],
        [False, False, False, False],
        [False, False, False, False],
        [False, False, False, False],
        [False, False, False, False]
    ]
    last_fret_found = copy.deepcopy(fret_found)

    while True:
        # Debounce
        time.sleep(0.1)

        # Write a new fret low, or advance to final step
        high_pos = (high_pos + 1) % 5

        if high_pos == 4:
            print("Scan complete")
            
            print(last_fret_found)

            # We have completed a scan
            # Here we check if multiple fret positions are contacted,
            # or if multiple notes are played i.e. in a chord

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
                print(f"Highest fret in contact: {max_high}")

                # Remove irrelevant contacts (probably the one immediately to the left)
                for k in range(4):
                    if k == max_high:
                        fret_found[i][k] = True
                    else:
                        fret_found[i][k] = False
                        
                print(fret_found)

                if last_fret_found[i][max_high] == False and fret_found[i][max_high] == True:
                    # Calculate the played note index (without position, bend)
                    print(f"Note will be played: {i * 4 + max_high}")
                    note_indices.append(i * 4 + max_high)

            # If a note is pressed...
            for note_index in note_indices:
                # send the MIDI note, modified by neck position and any bend
                print(f"playing note {midi_notes[note_index]}")
                midi.send(mido.Message('note_on', note=midi_notes[note_index], velocity=120))
                time.sleep(0.1)
                midi.send(mido.Message('note_off', note=midi_notes[note_index]))

            last_fret_found = copy.deepcopy(fret_found)

        else:
            # Scan to next fret
            for pos, fret_pin in enumerate(fret_pins):
                print(f"fret {fret_pin} high")
                if pos == high_pos:
                    gpio.output(fret_pin, gpio.HIGH)
                else:
                    gpio.output(fret_pin, gpio.LOW)

            # Read the input from the mini guitar neck
            for i in range(6):
                inp = string_inputs[i]
                if gpio.input(inp):
                    print(f"string {i} pressed!")
                    fret_found[i][high_pos] = True
                else:
                    fret_found[i][high_pos] = False

except KeyboardInterrupt:
    exit()
