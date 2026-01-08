# fluidsynth -a alsa -m alsa_seq -g 1.0 /home/marcusedwards/Desktop/midi_guitar_rpi/60s_Rock_Guitar.SF2

import mido
import time

# List available output ports (optional, for verification)
print("Available MIDI output ports:", mido.get_output_names())

# Open the FluidSynth port.
try:
    outport = mido.open_output(mido.get_output_names()[1]) 
except IOError:
    print("Could not open FluidSynth port. Make sure fluidsynth is running.")
    exit()

print("Port opened:", outport.name)

# Define a function to play a note (Note On and Note Off)
def play_note(note, velocity, duration):
    # Create Note On message (channel 0 is default)
    msg_on = mido.Message('note_on', note=note, velocity=velocity)
    outport.send(msg_on)
    print(f"Sent: {msg_on}")
    
    # Wait for the specified duration
    time.sleep(duration)
    
    # Create Note Off message
    msg_off = mido.Message('note_off', note=note, velocity=velocity)
    outport.send(msg_off)
    print(f"Sent: {msg_off}")

try:
    # Play a simple sequence: C4, D4, E4, C4
    play_note(60, 100, 0.5) # C4
    play_note(62, 100, 0.5) # D4
    play_note(64, 100, 0.5) # E4
    play_note(60, 100, 0.5) # C4
    
except KeyboardInterrupt:
    pass

finally:
    outport.close()
