# Adjust audio parameters depending of environment


## Setup python environment
    * Install python utilities:
       ```bash
       $ sudo apt-get install virtualenvwrapper libffi-dev # optional
       $ mkvirtualenv -p /usr/bin/python3 py3 # venv named py3
       (py3) $ pip install numpy
       ```


[Step guide](https://github.com/motdotla/ansible-pi/blob/master/README.md)


## Identify and set default audio device
 * Install alsa-utils:
    ```bash
    $ sudo apt-get install alsa-utils
    ```

## Source info
 - [Usb install](http://picodotdev.github.io/blog-bitix/2014/01/iniciar-la-raspberry-pi-desde-un-disco-o-memoria-usb/)

 - [Network config](https://github.com/motdotla/ansible-pi)

 - [PyAudio record example](https://people.csail.mit.edu/hubert/pyaudio/)

 - [PyAudio related info](http://dsp.stackexchange.com/questions/13728/what-are-chunks-when-recording-a-voice-signal/13732)
