# defect-detection

## Setup

### Local

```sh
# requirements for FFmpeg
apt-get install -y\
    yasm pkg-config libass-dev libfreetype-dev libmp3lame-dev libopus-dev libvorbis-dev libnuma-dev libx264-dev libx265-dev
# requirements for qumu
apt-get install libpixman-1-dev flex meson bison
source ./scripts/env.sh
```

### docker

```sh
docker build --tag defect-detection:ffmpeg-fuzzing .
```