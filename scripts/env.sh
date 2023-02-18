#!/bin/bash
# Environment setup for non-docker user.
export DETECTION_HOME=`pwd`
export LLVM=$HOME/clang+llvm
export PATH=$PATH:$LLVM
export CORES=`nproc`
export OSSFUZZ=$DETECTION_HOME/oss-fuzz