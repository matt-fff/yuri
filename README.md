# Yuri: technically an assistant

## New notes:

```
echo 'export LANG="en_US.UTF-8"' >> ~/.profile

# For PyEnv - https://github.com/pyenv/pyenv/wiki#suggested-build-environment=
sudo apt-get update; sudo apt-get install make build-essential libssl-dev zlib1g-dev \
	libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
	libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

# For other stuff
sudo apt install \
	git

curl https://pyenv.run | bash
```

Add the following to your bashrc:
```
export PYENV_ROOT="$HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```

Now install python (Yuri only works with 3.7.*)
```
source ~/.bashrc
pyenv install 3.7.13
```

```
git clone https://github.com/matt-fff/yuri.git
pyenv virtualenv 3.7.13 yuri
cd yuri
pyenv shell yuri
```



## HAT Setup
Yuri currently uses an [Adafruit BrainCraft HAT](https://www.adafruit.com/product/4374)
Follow their setup first: https://learn.adafruit.com/adafruit-braincraft-hat-easy-machine-learning-for-raspberry-pi

## Setup notes:


Dependencies
```
sudo apt install swig libpulse-dev libasound2-dev git uidmap \
	make build-essential libssl-dev zlib1g-dev \
	libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
	libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
	libffi-dev liblzma-dev python3-pyaudio portaudio19-dev \
	espeak ffmpeg libespeak1



git clone https://github.com/pyenv/pyenv.git ~/.pyenv
cd ~/.pyenv && src/configure && make -C src
sudo curl -sSL https://get.docker.com/ | sh
```

You have to have docker setup in rootless mode: https://docs.docker.com/engine/security/rootless/
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

### Audio
```
cd ~
sudo apt-get install -y git
git clone https://github.com/HinTak/seeed-voicecard
cd seeed-voicecard
git checkout v5.9
sudo ./install.sh
```

^ This doesn't help your audio if you have a non-standard output.

List the available output cards:
```
cat /proc/asound/modules
```


Modify your Alsa configuration to match
e.g. I had a USB speaker as card #2

`~/.asoundrc`:
```
pcm.!default {
        type plug
        slave {
                pcm "hw:2,0"
        }
}

ctl.!default {
        type hw
        card 2
}
```


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
