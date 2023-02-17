# defect-detection

## Setup

### Local

```sh
# requirements for oss-fuzz
apt-get install docker docker-engine docker.io containerd runc
source ./scripts/env.sh
```

### docker

```sh
docker build --tag defect-detection:ffmpeg-fuzzing .
```