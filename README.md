# defect-detection

## Setup

### Local

```sh
apt-get install -y yasm pkg-config libass-dev libfreetype-dev libmp3lame-dev libopus-dev libvorbis-dev libnuma-dev libx264-dev libx265-dev
source ./scripts/env.sh
```

### docker

```sh
docker build --tag defect-detection:ffmpeg-fuzzing .
```