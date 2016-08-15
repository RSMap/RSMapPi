import argparse
import logging
import numpy as np
import shutil
import sounddevice as sd

# Test

######


from queue import Queue, Empty
from threading import Thread

class Analyzer:
    def __init__(self):
        self.soundlibrary


_sentinel = object()

np.set_printoptions(threshold=np.inf)

n = 0

gain = 10
columns = 100
device = 2
block_duration = 100
samplerate = 44100
high = 2000
low = 450
delta_f = (high - low) / columns
fftsize = np.ceil(samplerate / delta_f).astype(int)
low_bin = np.floor(low / delta_f)
cumulated_status = sd.CallbackFlags()

colors = 30, 34, 35, 91, 93, 97
chars = ' :%#\t#%:'
gradient = []
for bg, fg in zip(colors, colors[1:]):
    for char in chars:
        if char == '\t':
            bg, fg = fg, bg
        else:
            gradient.append('\x1b[{};{}m{}'.format(fg, bg + 10, char))


def callback(indata, frames, time, status):
    global cumulated_status
    global line_num
    global fl
    global consequtive

    cumulated_status |= status

    if any(indata):
        magnitude = np.abs(np.fft.rfft(indata[:, 0], n=fftsize))
        magnitude *= gain / fftsize

        queue.put(np.sum(magnitude[low_bin:low_bin + columns]))

        line = ""

        for x in magnitude[low_bin:low_bin + columns]:
            line += (gradient[int(np.clip(x, 0, 1) * (len(gradient) - 1))])

        print(
            *line, sep='',
            end='\x1b[0m+ ' + str(np.sum(magnitude[low_bin:low_bin + columns])) + ' ' + str(line_num) + ' ' + str(consequtive)  + '\n',
            flush=True
            )

        print(
            line, sep='',
            end='\x1b[0m+ ' + str(np.sum(magnitude[low_bin:low_bin + columns])) + ' ' + str(line_num)+ ' ' + str(consequtive)  + '\n', file=fl,
            flush=True
            )

        line_num += 1

    else:
        print('no input', flush=True)

def producer(queue, line_num, fl):
    cont = True
    with sd.InputStream(device=device, channels=1, callback=callback,
                        blocksize=int(samplerate * block_duration / 1000),
                        samplerate=samplerate):
        while cont:
            response = input()
            if response in ('', 'q', 'Q'):
                queue.put(_sentinel)
                cont = False
                break
    fl.close()
    if cumulated_status:
        logging.warning(str(cumulated_status))

def consumer(queue, fo):
    global consequtive
    fo.write('[')
    while True:
        data = queue.get()
        if data is _sentinel:
            fo.write(']\n')
            fo.close()
            break
        row_sum = np.sum(data)

        if(row_sum > 0.59 ):
            consequtive += 1
        else:
            if(consequtive > 110):
                print("puede que mas de un coche!")
            elif(consequtive > 50):
                print("coche!")
            elif(consequtive > 38):
                print("puede que coche!")

            consequtive = 0

        fo.write(str(data))
        fo.write(', ')

global line_num
global consequtive

consequtive = 0
line_num = 0

fo = open('output', 'w')
global fl
fl = open('lines', 'w')

queue = Queue()

thread_prod = Thread(target=producer, args=(queue, line_num, fl))
thread_cons = Thread(target=consumer, args=(queue, fo))

thread_prod.start()
thread_cons.start()
