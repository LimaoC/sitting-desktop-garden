#! /bin/bash
#I'm running on the Pi and I assume I can see pyproject.toml, requirements_uvonly.in
# and apt_packages.txt

sudo swapoff -a
sudo fallocate -l 4G /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

sudo python3.10 -m pip install rpi-libcamera -C setup-args="-Dversion=unknown"