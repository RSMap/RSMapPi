# Install and basic configuration (Raspbian on Raspberry pi and external sound device)

**Model: ** Raspberry pi B

**OS: ** [Raspbian Jessie](https://downloads.raspberrypi.org/raspbian/images/raspbian-2016-05-31/)

## Installing on SD card

After download raspbian image:

```bash
$ lsblk # show us our disks.
$ sudo dd bs=1M if=2016-05-27-raspbian-jessie.img of=/dev/sdb # copy raspbian to sd card (sdb).
$ sudo dd bs=1M if=/dev/sdb2 of=/dev/sdc # copy raspbian system partition to USB flash drive.
```

Edit **cmdline.txt** on SD **/boot** partition and modify **root** variable:

```bash
smsc95xx.turbo_mode=N dwc_otg.lpm_enable=0 console=ttyAMA0,115200 kgdboc=ttyAMA0,115200 console=tty1 root=/dev/sda1 rootfstype=ext4 elevator=noop rootwait # /dev/sda1 point to our USB drive
```

This way our OS run faster than using only a SD card, however **/boot** is needed on SD to boot our system so we need SD card and USB anyway.

## Configuring network access

Configure wifi adapter with Ansible in Raspberry pi.

[Step guide](https://github.com/motdotla/ansible-pi/blob/master/README.md)


## Identify and set default audio device
 * Install alsa-utils:
    ```bash
    $ sudo apt-get install alsa-utils
    ```

 * Checking usb devices:
    ```
    $ lsusb
    Bus 001 Device 005: ID 0d8c:000c C-Media Electronics, Inc. Audio Adapter
    Bus 001 Device 004: ID 0781:5567 SanDisk Corp. Cruzer Blade
    Bus 001 Device 003: ID 0424:ec00 Standard Microsystems Corp. SMSC9512/9514 Fast Ethernet Adapter
    Bus 001 Device 002: ID 0424:9514 Standard Microsystems Corp.
    Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
    ```
 * Identify sound device:
    ```
    $ aplay -l
    **** List of PLAYBACK Hardware Devices ****
    card 0: ALSA [bcm2835 ALSA], device 0: bcm2835 ALSA [bcm2835 ALSA]
      Subdevices: 8/8
      Subdevice #0: subdevice #0
      Subdevice #1: subdevice #1
      Subdevice #2: subdevice #2
      Subdevice #3: subdevice #3
      Subdevice #4: subdevice #4
      Subdevice #5: subdevice #5
      Subdevice #6: subdevice #6
      Subdevice #7: subdevice #7
    card 0: ALSA [bcm2835 ALSA], device 1: bcm2835 ALSA [bcm2835 IEC958/HDMI]
      Subdevices: 1/1
      Subdevice #0: subdevice #0
    card 1: Set [C-Media USB Headphone Set], device 0: USB Audio [USB Audio]
      Subdevices: 1/1
      Subdevice #0: subdevice #0
    ```

    In this case my device is called *C-Media USB Headphone SetC-Media USB Headphone Set*.

    At this point, the most important thing is take two numbers, with the above output. **card id** and **device id**

 * Setting our card as default system card (create or edit *~/.asoundrc*):

  ```bash
      pcm.!default {
    	type hw
    	card 1
    }

    ctl.!default {
    	type hw
    	card 1
    }
  ```
 In my case, card 1 identifies my USB Audio adapter.

## Testing record capability of our sound card:
 ```python
     """
    PyAudio example: Record a few seconds of audio and save to a WAVE
    file.
    """

    import pyaudio
    import wave
    import sys

    CHUNK = 512 # number of samples in each buffer
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100 # it's may change with different devices
    RECORD_SECONDS = 25
    WAVE_OUTPUT_FILENAME = "output.wav"

    if sys.platform == 'darwin':
        CHANNELS = 1

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
 ```
 Source from [here](https://people.csail.mit.edu/hubert/pyaudio/). (PyAudio docs)

## Source info
 - [Usb install](http://picodotdev.github.io/blog-bitix/2014/01/iniciar-la-raspberry-pi-desde-un-disco-o-memoria-usb/)

 - [Network config](https://github.com/motdotla/ansible-pi)

 - [PyAudio record example](https://people.csail.mit.edu/hubert/pyaudio/)

 - [PyAudio related info](http://dsp.stackexchange.com/questions/13728/what-are-chunks-when-recording-a-voice-signal/13732)
