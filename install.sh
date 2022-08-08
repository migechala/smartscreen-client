#!/bin/bash

sudo apt install build-essential libsdl2-dev libsdl2-ttf-dev python3-aiohttp

pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthli python-weather

cd lib
make

cp obj/main /usr/bin/smartscreen

echo "Done! Just restart your terminal and run \"smartscreen\", and press \"Escape\" when you want to exit."