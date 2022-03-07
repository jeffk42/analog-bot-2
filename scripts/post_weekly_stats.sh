#!/bin/bash

cd /home/jkraus/work/analog-bot
python3 post_weekly_stats.py $(date -u +"%Y %W")
