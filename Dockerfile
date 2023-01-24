FROM ubuntu:22.04

RUN apt-get -y update && \
    apt-get -y upgrade 
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get install -y -q aptitude git build-essential wget zlib1g-dev cmake python3 python3-pip && \
    apt-get install -y -q yasm && \
    apt-get install -y -q pkg-config libass-dev libfreetype-dev libmp3lame-dev libopus-dev libvorbis-dev libnuma-dev libx264-dev libx265-dev && \
    apt-get clean

ENV HOME=/root
ENV DETECTION_HOME=$HOME
ENV AFL=$DETECTION_HOME/AFLplusplus
ENV PATH=$PATH:$HOME/clang+llvm/bin
ENV LLVM=$HOME/clang+llvm
ENV FFMPEG=$DETECTION_HOME/FFmpeg

ARG CLANG_LLVM=clang+llvm-14.0.0-x86_64-linux-gnu-ubuntu-18.04
COPY scripts/*.sh $DETECTION_HOME/scripts/
RUN cd $DETECTION_HOME && ./scripts/init.sh

COPY scripts $DETECTION_HOME/scripts
COPY seeds $DETECTION_HOME/seeds

