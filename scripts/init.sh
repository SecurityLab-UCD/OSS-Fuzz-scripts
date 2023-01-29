
# Which LLVM are we using?
CLANG_LLVM=clang+llvm-14.0.0-x86_64-linux-gnu-ubuntu-18.04

# Download and install LLVM
if [ ! -d $LLVM ]; then
    LLVM_SRC=https://github.com/llvm/llvm-project/releases/download/llvmorg-14.0.0/$CLANG_LLVM.tar.xz
    cd $EMBDING_HOME 
    wget $LLVM_SRC 
    tar -xvf $CLANG_LLVM.tar.xz
    rm $CLANG_LLVM.tar.xz 
    mv $CLANG_LLVM clang+llvm14 
    ln -s clang+llvm14 clang+llvm 
fi

# Download and install AFL
if [ ! -d $AFL ]; then
    git clone https://github.com/AFLplusplus/AFLplusplus.git
fi
cd $AFL; make -j; cd ..

if [ ! -d $FFMPEG ]; then
    git clone https://github.com/FFmpeg/FFmpeg.git
fi
cd $FFMPEG
./configure --prefix="$HOME/ffmpeg_build" --pkg-config-flags="--static" --extra-cflags="-I$HOME/ffmpeg_build/include" --extra-ldflags="-L$HOME/ffmpeg_build/lib" --extra-libs="-lpthread -lm" --bindir="$HOME/bin" --enable-gpl --enable-libass --enable-libfreetype --enable-libmp3lame --enable-libopus --enable-libvorbis --enable-libx264 --enable-libx265 --enable-nonfree --cc=$AFL/afl-clang-fast --cxx=AFL/afl-clang-fast++ --extra-cflags="-I$HOME/ffmpeg_build/include -O1 -fno-omit-frame-pointer -g" --extra-cxxflags="-O1 -fno-omit-frame-pointer -g" --extra-ldflags="-L$HOME/ffmpeg_build/include -fsanitize=address -fsanitize=undefined -lubsan" --enable-debug
make -j; cd ..

if [ ! -d $QEMU ]; then
    git clone https://github.com/qemu/qemu.git
fi
cd $QEMU;
git submodule update --init --recursive
mkdir -p build; cd build
# if --enable-debug make will fail
../configure --cc=$AFL/afl-clang-fast --cxx=$AFL/afl-clang-fast++
make -j; cd $DETECTION_HOME


