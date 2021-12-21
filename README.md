# Yuri: technically an assistant

## Setup notes:

### Audio
https://learn.adafruit.com/adafruit-braincraft-hat-easy-machine-learning-for-raspberry-pi/audio-setup

Check if audio is working:
```
sudo i2cdetect -y 1
```

Installing the onboard audio
```
cd ~
sudo apt-get install -y git
git clone https://github.com/HinTak/seeed-voicecard
cd seeed-voicecard
```

Determine the right branch with `uname -r`
for 5.4 use `v5.5`; for 5.10 and higher, use `v5.9`

e.g. with 5.10.63-v8+
```
git checkout v5.9
sudo ./install.sh
```

Changing the default device - use pulseaudio. Find the desired device with `pactl list short sinks` then use it with `pactl set-default-sink`, e.g.
```
pactl set-default-sink alsa_output.usb-Jieli_Technology_UACDemoV1.0_1120022704050903-01.analog-stereo 
```

### Dependencies
```
sudo apt install swig libpulse-dev libasound2-dev git uidmap pipenv \
	make build-essential libssl-dev zlib1g-dev \
	libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
	libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
	libffi-dev liblzma-dev neovim tmux fzf silversearcher-ag \
	pkg-config libhdf5-dev

git clone https://github.com/pyenv/pyenv.git ~/.pyenv
cd ~/.pyenv && src/configure && make -C src

# the sed invocation inserts the lines at the start of the file
# after any initial comment lines
sed -Ei -e '/^([^#]|$)/ {a \
export PYENV_ROOT="$HOME/.pyenv"
a \
export PATH="$PYENV_ROOT/bin:$PATH"
a \
' -e ':a' -e '$!{n;ba};}' ~/.profile
echo 'eval "$(pyenv init --path)"' >>~/.profile
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

sudo curl -sSL https://get.docker.com/ | sh
```

You have to haver docker setup in rootless mode: https://docs.docker.com/engine/security/rootless/
```
dockerd-rootless-setuptool.sh install
```

### On the main system
```
scp .tmux.conf* yuri:~/
scp .ssh/github.p* yuri:~/.ssh/
scp .gitconfig yuri:~/
scp .ssh/config yuri:~/.ssh/
scp .config/nvim/init.vim
```

### Clone the repo
```
cd ~
git clone git@github.com:typenil/yuri.git
cd yuri
pyenv install 3.7.12
pyenv local 3.7.12
pipenv shell
pipenv install
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



#### Tensorflow - install hell
Good guide: https://www.bitsy.ai/3-ways-to-install-tensorflow-on-raspberry-pi/

Find a compatible wheel here: https://www.tensorflow.org/install/pip#package-location
```
pipenv install https://compatible-wheel-uri
```
^ None of these wheels support 32 bit. Save yourself some trouble and install Rasbian in 64 bit mode 


##### From community binaries
Find a compatible wheel here: https://github.com/bitsy-ai/tensorflow-arm-bin
```
pipenv install https://github.com/bitsy-ai/tensorflow-arm-bin/releases/download/v2.4.0/tensorflow-2.4.0-cp37-none-linux_aarch64.whl
```


##### From source
```
git clone https://github.com/tensorflow/tensorflow.git
cd tensorflow
tensorflow/tools/ci_build/ci_build.sh PI-PYTHON37 tensorflow/tools/ci_build/pi/build_raspberry_pi.sh
``` 


