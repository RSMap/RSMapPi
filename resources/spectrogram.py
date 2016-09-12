#!/usr/bin/env python3
"""Show a text-mode spectrogram using live microphone data."""
import argparse
import logging
import math
import numpy as np
import shutil

usage_line = ' press <enter> to quit, +<enter> or -<enter> to change scaling '


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

levels = 100
threshold = 0.59
consequtive_blocks = 50

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('-l', '--list-devices', action='store_true',
                    help='list audio devices and exit')
parser.add_argument('-b', '--block-duration', type=float,
                    metavar='DURATION', default=50,
                    help='block size (default %(default)s milliseconds)')
parser.add_argument('-le', '--levels', type=int, default=levels,
                    help='width of spectrogram')
parser.add_argument('-d', '--device', type=int_or_str,
                    help='input device (numeric ID or substring)')
parser.add_argument('-g', '--gain', type=float, default=10,
                    help='initial gain factor (default %(default)s)')
parser.add_argument('-r', '--range', type=float, nargs=2,
                    metavar=('LOW', 'HIGH'), default=[100, 2000],
                    help='frequency range (default %(default)s Hz)')
args = parser.parse_args()

low, high = args.range
if high <= low:
    parser.error('HIGH must be greater than LOW')

# Create a nice output gradient using ANSI escape sequences.
# Stolen from https://gist.github.com/maurisvh/df919538bcef391bc89f
colors = 30, 34, 35, 91, 93, 97
chars = ' :%#\t#%:'
gradient = []
for bg, fg in zip(colors, colors[1:]):
    for char in chars:
        if char == '\t':
            bg, fg = fg, bg
        else:
            gradient.append('\x1b[{};{}m{}'.format(fg, bg + 10, char))

try:
    import sounddevice as sd

    if args.list_devices:
        print(sd.query_devices())
        parser.exit()

    samplerate = sd.query_devices(args.device, 'input')['default_samplerate']

    delta_f = (high - low) / (args.levels - 1)
    fftsize = math.ceil(samplerate / delta_f)
    low_bin = math.floor(low / delta_f)

    cumulated_status = sd.CallbackFlags()

    def callback(indata, frames, time, status):
        global cumulated_status
        global line_num
        cumulated_status |= status
        if any(indata):
            magnitude = np.abs(np.fft.rfft(indata[:, 0], n=fftsize))
            magnitude *= args.gain / fftsize
            row_sum = np.sum(magnitude[low_bin:low_bin + levels])

            if(row_sum > threshold):
                line_num += 1
            else:
                line_num = 0

            line = (gradient[int(np.clip(x, 0, 1) * (len(gradient) - 1))]
                    for x in magnitude[low_bin:low_bin + args.levels])
            print(*line, sep='', end=str(line_num) + ' ' + str(row_sum)+ ' ' + '\x1b[0m\n', flush=True)
        else:
            print('no input', flush=True)

    global line_num
    line_num = 0
    with sd.InputStream(device=args.device, channels=1, callback=callback,
                        blocksize=int(samplerate * args.block_duration / 1000),
                        samplerate=samplerate):
        while True:
            response = input()
            if response in ('', 'q', 'Q'):
                break
            for ch in response:
                if ch == '+':
                    args.gain *= 2
                elif ch == '-':
                    args.gain /= 2
                else:
                    print('\x1b[31;40m', usage_line.center(args.columns, '#'),
                          '\x1b[0m', sep='', flush=True)
                    break
    if cumulated_status:
        logging.warning(str(cumulated_status))
except KeyboardInterrupt:
    parser.exit('Interrupted by user')
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))