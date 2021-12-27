# Yuri: technically an assistant

## Setup notes:


Dependencies
```
sudo apt install swig libpulse-dev libasound2-dev git uidmap pipenv \
	make build-essential libssl-dev zlib1g-dev \
	libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
	libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
	libffi-dev liblzma-dev python3-pyaudio portaudio19-dev

git clone https://github.com/pyenv/pyenv.git ~/.pyenv
cd ~/.pyenv && src/configure && make -C src
sudo curl -sSL https://get.docker.com/ | sh
```

You have to haver docker setup in rootless mode: https://docs.docker.com/engine/security/rootless/
```
sudo systemctl disable --now docker.service docker.socket
dockerd-rootless-setuptool.sh install
```

### Display
Download the setup scripts
```
cd ~
sudo pip3 install --upgrade adafruit-python-shell click==7.0
git clone https://github.com/adafruit/Raspberry-Pi-Installer-Scripts.git
cd Raspberry-Pi-Installer-Scripts
```

Setup the display
```
sudo python3 adafruit-pitft.py --display=st7789_240x240 --rotation=90 --install-type=fbcp
```
There was no exact match for the hat I'm using. But the display is the same resolution and whatnot.

_NOTE the display setup takes FOREVER and there's no progress bar/output to speak of_

### Tensorflow - install hell
Good guide: https://www.bitsy.ai/3-ways-to-install-tensorflow-on-raspberry-pi/

Find a compatible wheel here: https://www.tensorflow.org/install/pip#package-location
```
pipenv install https://compatible-wheel-uri
```
^ None of these wheels support 32 bit. Save yourself some trouble and install Rasbian in 64 bit mode 


#### From source
```
git clone https://github.com/tensorflow/tensorflow.git
cd tensorflow
tensorflow/tools/ci_build/ci_build.sh PI-PYTHON37 tensorflow/tools/ci_build/pi/build_raspberry_pi.sh AARCH64
``` 


### RPi.GPIO

If you keep getting this error:
```
    collect2: error: ld returned 1 exit status
    error: command '/usr/bin/aarch64-linux-gnu-gcc' failed with exit code 1
```

Set `export CFLAGS=-fcommon` and try again
