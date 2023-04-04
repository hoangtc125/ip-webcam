#!/bin/bash

# Install Gstreamer Ubuntu
apt-get -y install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
    libgstreamer-plugins-bad1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-doc \
    gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 \
    gstreamer1.0-qt5 gstreamer1.0-pulseaudio libgirepository1.0-dev python3-gi python-gst-1.0 \
    libcairo2-dev gir1.2-gstreamer-1.0 &&

# Install common python package
pip3 install --upgrade wheel pip setuptools &&
pip3 install -r requirements.txt
