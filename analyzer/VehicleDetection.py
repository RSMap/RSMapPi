import argparse
import logging
import numpy as np
import shutil
import sounddevice as sd
import subprocess
import requests
import sys
from queue import Queue, Empty
from threading import Thread

# Test
import time
import socket
######

# check if this client send data before
device_id = 'TFGDevice' # case sensitive
device_location = 'Avda Dilar'
latitude = '37.177336'
longitude = '-3.598557'
signal_type = 'u'
# level -1 means device is connected and it will send data soon.
level = '-1.0'
new_device_payload = {'device_id':device_id, 'lat':latitude, 'long':longitude, 'level':level, 'type':signal_type}
existing_device_payload = {'level': level}
signals_list_url = 'http://52.210.3.41/api/signals/'
signal_url = 'http://52.210.3.41/api/signal/'+device_id+'/'

req = requests.post(signals_list_url, new_device_payload)

if(req.status_code == 400):
    print("Device already exists, sending connect signal")
    req = requests.patch(signal_url, existing_device_payload)
    if(req.status_code == 200):
        print("Connection successful")
    else:
        print("Can't send connected signal, exiting")
        sys.exit()
elif(req.status_code == 201):
    print("Connection successful, device added to device's database")
else:
    print("Device can't connect to rest service, check your connection.")
    sys.exit()



# Connecting to DataSender socket on localhost
socket = socket.socket()
socket.connect(('localhost', 5000))
# Send device location
device_location_sock = device_location+"\n"
device_location_bytes = bytes(device_location_sock, 'utf-8')
socket.send(device_location_bytes)
# Send device id
device_id_sock = device_id+"\n"
device_id_bytes = bytes(device_id_sock, 'utf-8')
socket.send(device_id_bytes)

# Wait prudent time
time.sleep(20)

# Variable definition
_sentinel = object()
np.set_printoptions(threshold=np.inf) # full numpy array output (test purpose)

gain = 10 # multiplier factor
columns = 100 # numero de niveles de cuantización
device = 2 # id del dispositivo
block_duration = 100 # duración de cada bloque capturado (ms)
samplerate = 44100 # frecuencia de muestreo
high = 2000 # frecuencia de muestreo alta
low = 500 # frecuencia de muestreo baja
delta_f = (high - low) / columns # valor de cuantización
fftsize = np.ceil(samplerate / delta_f).astype(int) # definimos el número de bins usados para dividir la ventana en bandas, determina la resolucion en el dominio de la frecuencia
low_bin = np.floor(low / delta_f) # resolución de frecuencia de la ventana
cumulated_status = sd.CallbackFlags() # enable logging output


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

    # indata size = samplerate * block_duration / 1000
    if any(indata):
        #indata[:, 0] toma los valores de la primera dimension del array (solo tiene una dimension)
        # np.fft.rfft This function computes the one-dimensional n-point discrete Fourier Transform (DFT) of a real-valued array by means of an efficient algorithm called the Fast Fourier Transform (FFT).
        magnitude = np.abs(np.fft.rfft(indata[:, 0], n=fftsize))
        magnitude *= gain / fftsize

        # put row sum on queue to analyze it
        queue.put(np.sum(magnitude[low_bin:low_bin + columns]))

        line = ""

        for x in magnitude[low_bin:low_bin + columns]:
            line += (gradient[int(np.clip(x, 0, 1) * (len(gradient) - 1))])

        print(
            *line, sep='',
            end='\x1b[0m+ ' + str(np.sum(magnitude[low_bin:low_bin + columns])) + ' ' + str(line_num) + ' ' + str(consequtive)  + '\n',
            flush=True
            )

        # print(
        #     line, sep='',
        #     end='\x1b[0m+ ' + str(np.sum(magnitude[low_bin:low_bin + columns])) + ' ' + str(line_num)+ ' ' + str(consequtive)  + '\n', file=fl,
        #     flush=True
        #     )


        line_num += 1

    else:
        print('no input', flush=True)

def producer(queue, line_num):
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

    if cumulated_status:
        logging.warning(str(cumulated_status))

def consumer(queue):
    global consequtive
    send_queue = Queue()

    while True:
        data = queue.get()
        # print(data)
        if data is _sentinel:
            # sending end signal to java and wait to close all connections
            socket.send(b'q\n')
            time.sleep(5)

            # exit
            break

        if(data > 0.59 ):
            consequtive += 1
            # if detected > 50 send to api rest
            # add representative values to send if they represent a vehicle
            send_queue.put(data)
        else:
            detected = False
            if(consequtive > 110):
                # Multiples vehicles
                detected = True
                print("puede que mas de un coche!")
            elif(consequtive > 50):
                # Vehicle
                detected = True
                print("coche!")
            elif(consequtive > 38):
                # Fast vehicle or maybe noise
                detected = True
                print("puede que coche!")

            if(detected):
                #print("detectao")
                while not send_queue.empty():
                    #print("enviando")
                    # detected case, sending items to KAA SDK
                    item_to_send = send_queue.get()
                    linestr =str(item_to_send)+"\n"
                    linebytes = bytes(linestr, 'utf-8')
                    socket.send(linebytes)

            # clear send_queue
            send_queue = Queue()
            send_queue.queue.clear()
            consequtive = 0

global line_num
global consequtive

consequtive = 0
line_num = 0

queue = Queue()

thread_prod = Thread(target=producer, args=(queue, line_num, ))
thread_cons = Thread(target=consumer, args=(queue, ))

thread_prod.start()
thread_cons.start()


# time.sleep(20)
# # removing from database
# req = requests.delete(signal_url)
# if(req.status_code == 204):
#     print("Device removed from device's database")
