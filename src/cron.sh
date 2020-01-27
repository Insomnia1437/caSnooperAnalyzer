#!/bin/bash
dirname="/home/sdcswd/workspace/python/caSnooperAnalyzer"
cd $dirname || exit
/home/sdcswd/.pyenv/shims/python3 $dirname/src/caSA.py >> $dirname/log/caSA.log 2>&1