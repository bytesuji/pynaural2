import argparse
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


def main():
    parser = argparse.ArgumentParser(description='Binaural beat generator')
    parser.add_argument('-l', '--left_frequency', type=float, default=440.0, help='Left channel frequency (Hz)')
    parser.add_argument('-r', '--right_frequency', type=float, default=444.0, help='Right channel frequency (Hz)')
    parser.add_argument('-d', '--duration', type=float, default=10.0, help='Duration of the binaural beat (seconds)')
    parser.add_argument('-v', '--volume', type=float, default=-20.0, help='Volume of the binaural beat (dBFS)')

    args = parser.parse_args()
    binaural_beat = generate_binaural_beat(args.left_frequency, args.right_frequency, args.duration, args.volume)
    play(binaural_beat)


if __name__ == '__main__':
    main()
