#!/bin/bash
# Environment setup for non-docker user.
export DETECTION_HOME=`pwd`
export LLVM=$HOME/clang+llvm
export PATH=$PATH:$LLVM
export CORES=`nproc`
export OSSFUZZ=$DETECTION_HOME/oss-fuzz

export REPORT_PASS=$DETECTION_HOME/ReportFunctionExecutedPass
export REPORT_FLAGS="-Xclang -load -Xclang $REPORT_PASS/report/libReportPass.so -flegacy-pass-manager"
export CFLAGS="$CFLAGS $REPORT_PASS/reporter.o $REPORT_FLAGS"
export CXXFLAGS="$CXXFLAGS $REPORT_PASS/reporter.o $REPORT_FLAGS"