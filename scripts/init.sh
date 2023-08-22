pip3 install -r requirements.txt

# get clang+llvm 14
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
cd $OSSFUZZ_SCRIPTS_HOME

# get oss-fuzz and ReportPass
git submodule init
git submodule update

# build Java ReportAgent
cd $OSSFUZZ_SCRIPTS_HOME/java-io-capture
mvn clean package
cd $OSSFUZZ_SCRIPTS_HOME