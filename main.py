import argparse
import json
import numpy as np

from pydub import AudioSegment
from pydub.playback import play

def generate_binaural_beat(frequency_left, frequency_right, duration, volume=-20.0, sample_rate=44100):
    """
    Generate binaural beat with given frequencies for left and right channels, duration and volume.

    Args:
        frequency_left (float): Frequency of the left channel (Hz).
        frequency_right (float): Frequency of the right channel (Hz).
        duration (float): Duration of the binaural beat (seconds).
        volume (float): Volume of the binaural beat (dBFS).
        sample_rate (int): Sample rate (Hz).

    Returns:
        AudioSegment: Generated binaural beat.
    """
    t = np.arange(0, duration, 1 / sample_rate)
    left_wave = (np.sin(2 * np.pi * frequency_left * t) * 32767).astype(np.int16)
    right_wave = (np.sin(2 * np.pi * frequency_right * t) * 32767).astype(np.int16)
    stereo_wave = np.column_stack((left_wave, right_wave)).flatten()
    audio = AudioSegment(stereo_wave.tobytes(),
                         frame_rate=sample_rate,
                         sample_width=stereo_wave.dtype.itemsize,
                         channels=2)

    return audio + volume

def generate_and_store_beat(instruction, beats):
    duration = instruction['duration']
    loops = int(duration / 60)  # Calculate how many loops of 60 seconds we need
    remaining_time = duration % 60  # Calculate the remaining time

    # Generate the 60 seconds loops
    for _ in range(loops):
        beat = generate_binaural_beat(instruction['left_frequency'],
                                      instruction['right_frequency'],
                                      60,  # Maximum duration is 60 seconds
                                      instruction['volume'])
        beat_samples = np.array(beat.get_array_of_samples(), dtype=np.int16)  # Convert to numpy array
        beats = np.concatenate((beats, beat_samples))

    # Generate the remaining time beat
    if remaining_time > 0:
        beat = generate_binaural_beat(instruction['left_frequency'],
                                      instruction['right_frequency'],
                                      remaining_time,
                                      instruction['volume'])
        beat_samples = np.array(beat.get_array_of_samples(), dtype=np.int16)  # Convert to numpy array
        beats = np.concatenate((beats, beat_samples))

    return beats

def translate_new_spec_format(new_spec):
    base = new_spec['base']
    program = new_spec['program']
    translated_instructions = []

    for tone, duration in program:
        translated_instructions.append({
            'left_frequency': base,
            'right_frequency': base + tone,
            'duration': duration,
            'volume': -20.0  # default volume
        })

    return translated_instructions, new_spec.get('loop', False)

def main():
    parser = argparse.ArgumentParser(description='Binaural beat generator')
    parser.add_argument('-l', '--left_frequency', type=float, default=440.0, help='Left channel frequency (Hz)')
    parser.add_argument('-r', '--right_frequency', type=float, default=444.0, help='Right channel frequency (Hz)')
    parser.add_argument('-d', '--duration', type=float, default=10.0, help='Duration of the binaural beat (seconds)')
    parser.add_argument('-v', '--volume', type=float, default=-20.0, help='Volume of the binaural beat (dBFS)')
    parser.add_argument('-s', '--spec_file', type=str, help='Path to specification file')

    args = parser.parse_args()
    beats = np.array([])
    loop = False

    if args.spec_file:
        with open(args.spec_file, 'r') as f:
            instructions = json.load(f)

        # Check if the new spec format is used
        if 'base' in instructions:
            instructions, loop = translate_new_spec_format(instructions)
        for instruction in instructions:
            beats = generate_and_store_beat(instruction, beats)
    else:
        instruction = {
            'left_frequency': args.left_frequency,
            'right_frequency': args.right_frequency,
            'duration': args.duration,
            'volume': args.volume
        }
        beats = generate_and_store_beat(instruction, beats)

    # Repeat the beat sequence to form a continuous loop
    if loop:
        total_duration = sum(instruction['duration'] for instruction in instructions)
        desired_duration = 2 * 60 * 60
        repetitions = int(desired_duration / total_duration)
        beats = np.tile(beats, repetitions)

    beats = AudioSegment(
        beats.astype(np.int16).tobytes(),  # Ensure dtype is int16
        frame_rate=44100,
        sample_width=2,  # Set sample_width to 2 bytes
        channels=2,
    )

    if loop:
        while True:
            play(beats)
    else:
        play(beats)

if __name__ == '__main__':
    main()
