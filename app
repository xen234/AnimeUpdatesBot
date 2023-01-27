#!/bin/bash
#Запускать из директории AnimeUpdatesBot
pip3 install -r requirements.txt
pip3 install -e .
python3 Bot/bot_main.py
