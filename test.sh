#!/bin/bash
# 281,5
time python3 ActEV_Scorer.py ActEV_SDL_V2  -FdmS -n 6 -v \
    -o ../scorer_output \
    -a ../system/activity-index.json \
    -f ../system/file-index.json \
    -r ../system/activities.json \
    -s ../system/system-output.json
