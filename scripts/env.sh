#!/bin/bash
# Environment setup for non-docker user.
export DETECTION_HOME=`pwd`
export AFL=$DETECTION_HOME/AFLplusplus
export LLVM=$HOME/clang+llvm
export PATH=$PATH:$LLVM:$AFL
export AFL_NO_UI=1
unset AFL_CUSTOM_MUTATOR_LIBRARY
unset AFL_CUSTOM_MUTATOR_ONLY
export AFL_LLVM_INSTRUMENT=unset PCGUARD 
export CORES=`nproc`
unset AFL_EXIT_ON_SEED_ISSUES
export FFMPEG=$DETECTION_HOME/FFmpeg
export QEMU=$DETECTION_HOME/qemu
