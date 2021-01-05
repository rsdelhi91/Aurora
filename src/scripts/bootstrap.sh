#!/bin/bash
# update package list
sudo apt update
# install pip3
sudo apt install python3-pip -y
# install venv
sudo apt install python3-venv -y
# create the aurora venv
python3 -m venv ./aurora
# activate the aurora venv
. ./aurora/bin/activate
# install dependencies for Aurora
pip3 install -r requirements.txt