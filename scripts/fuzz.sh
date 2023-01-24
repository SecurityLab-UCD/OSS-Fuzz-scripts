#!/bin/bash

$AFL/afl-fuzz -D -V 60 -i seeds -o fuzz -t 50 $FFMPEG/ffmpeg