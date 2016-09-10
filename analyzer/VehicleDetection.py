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
import time
import socket


# check if this client send data before
# device id (case sensitive)
device_id = 'TFGDevice'
# device location (name)
device_location = 'Avda Dilar'
# device coordinates
latitude = '37.177336'
longitude = '-3.598557'
# signal_type (default unknown)
signal_type = 'u'
# level -1 means device is connected and it will send data soon.
level = '-1.0'
# new_device_payload contains all related info with a map structure
new_device_payload = {'device_id':device_id, 'lat':latitude, 'long':longitude, 'level':level, 'type':signal_type}
# if device exists, only level is needed
existing_device_payload = {'level': level}
# rest urls
signals_list_url = 'http://52.210.3.41/api/signals/'
signal_url = 'http://52.210.3.41/api/signal/'+device_id+'/'

# rest first request
req = requests.post(signals_list_url, new_device_payload)

# check rest response
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
# sentinel indicates end queue processing
_sentinel = object()
# full numpy array output (testing purposes)
np.set_printoptions(threshold=np.inf)

 # multiplier factor
gain = 10
 # number of cuantization levels
levels = 100
# system device id
device = 2
# block time (ms)
block_duration = 100
# sample rate
samplerate = 44100
# high sample rate
high = 2000
# low sample rate
low = 450
# cuantization value
delta_f = (high - low) / levels
# window will divided in bands, fftsize defines the resolution on freq domain
fftsize = np.ceil(samplerate / delta_f).astype(int)
# window freq resolution
low_bin = np.floor(low / delta_f)
# vehicle threshold
threshold = 0.59
# consequtive blocks, its may depend of the road conditions
consequtive_blocks = 50

 # enable logging output
cumulated_status = sd.CallbackFlags()

# callback will called from producer for each block
def callback(indata, frames, time, status):
    global cumulated_status
    global consequtive

    # logging purpose
    cumulated_status |= status

    # indata size = samplerate * block_duration / 1000
    if any(indata):
        # computes the one-dimensional n-point discrete Fourier Transform (DFT)
        # of a real-valued array by the Fast Fourier Transform (FFT).
        magnitude = np.abs(np.fft.rfft(indata[:, 0], n=fftsize))
        # signal values amplification
        magnitude *= gain / fftsize

        # put row sum on queue to analyze it
        queue.put(np.sum(magnitude[low_bin:low_bin + levels]))

    else:
        print('no input', flush=True)

# producer interacts with our sound card and calls callback function
def producer(queue):
    cont = True
    # sounddevice method, open an input stream to selected device
    with sd.InputStream(device=device, channels=1, callback=callback,
                        blocksize=int(samplerate * block_duration / 1000),
                        samplerate=samplerate):
        while cont:
            # checks if exists stop signal
            response = input()
            if response in ('', 'q', 'Q'):
                queue.put(_sentinel)
                cont = False
                break
    # show logging
    if cumulated_status:
        logging.warning(str(cumulated_status))

# reads data from queue and discard undesired values
def consumer(queue):
    global consequtive
    # this queue stores valid data which it will sended to rest and cassandra
    send_queue = Queue()
    # local variables allows send signals for a defined number of blocks
    local_consequtive = 0
    local_data_sum = 0.0

    while True:
        data = queue.get()
        # print(data)
        if data is _sentinel:
            # delete device via rest
            req = requests.delete(signal_url)
            if(req.status_code == 204):
                print("Device removed from device's database")
            # sending end signal to java and wait to close all connections
            socket.send(b'q\n')
            time.sleep(5)
            # exit
            break

        if(data > threshold ):
            # global block consequtive count
            consequtive += 1
            local_consequtive += 1
            local_data_sum += data
            if(local_consequtive == consequtive_blocks):
                # if detected > consequtive_blocks send to api rest
                existing_device_payload = {'level': str(local_data_sum)}
                req = requests.patch(signal_url, existing_device_payload)

                print(str(consequtive_blocks) + " consequtive blocks, sending to rest API " + str(local_data_sum))
                local_consequtive = 0
                local_data_sum = 0.0

            # add representative values to send_queue
            send_queue.put(data)
        else:
            if(consequtive > consequtive_blocks):
                print("Sending data to cassandra")
                while not send_queue.empty():
                    # detected case, sending items to KAA SDK via TCP socket
                    item_to_send = send_queue.get()
                    linestr =str(item_to_send)+"\n"
                    linebytes = bytes(linestr, 'utf-8')
                    socket.send(linebytes)

            # consequtive was not bigger than consequtive_blocks, cleaning resources
            send_queue = Queue()
            send_queue.queue.clear()
            consequtive = 0
            local_consequtive = 0
            local_data_sum = 0.0



global consequtive
consequtive = 0

queue = Queue()

# thread instances
thread_prod = Thread(target=producer, args=(queue, ))
thread_cons = Thread(target=consumer, args=(queue, ))

# thread init
thread_prod.start()
thread_cons.start()
