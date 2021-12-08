# Yuri: technically an assistant

## Setup notes:


### Display
Download the setup scripts
```
cd ~
sudo pip3 install --upgrade adafruit-python-shell click==7.0
sudo apt-get install -y git
git clone https://github.com/adafruit/Raspberry-Pi-Installer-Scripts.git
cd Raspberry-Pi-Installer-Scripts
```

Setup the display
```
sudo python3 adafruit-pitft.py --display=st7789_240x240 --rotation=90 --install-type=fbcp
```
There was no exact match for the hat I'm using. But the display is the same resolution and whatnot.

_NOTE the display setup takes FOREVER and there's no progress bar/output to speak of_

