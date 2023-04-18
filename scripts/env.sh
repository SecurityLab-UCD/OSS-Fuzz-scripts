#!/bin/bash
# Environment setup for non-docker user.
export OSSFUZZ_SCRIPTS_HOME=`pwd`
export LLVM=$HOME/clang+llvm
export PATH=$PATH:$LLVM/bin
export CORES=`nproc`
export OSSFUZZ=$OSSFUZZ_SCRIPTS_HOME/oss-fuzz
