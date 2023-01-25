mkdir -p seeds

mkdir -p seeds/ffmpeg
cd seeds/ffmpeg
wget http://samples.ffmpeg.org/A-codecs/24bit/UT-24bitPCM.avi
wget http://samples.ffmpeg.org/A-codecs/format-0x1500-OKRICKY.WAV

cd $DETECTION_HOME
mkdir -p seeds/qemu
cd seeds/qemu

cd $DETECTION_HOME