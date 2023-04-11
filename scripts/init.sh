
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


if [ ! -d $OSSFUZZ ]; then
    git clone https://github.com/SecurityLab-UCD/oss-fuzz.git
fi

if [ ! -d $REPORT_PASS ]; then
    git clone https://github.com/SecurityLab-UCD/ReportFunctionExecutedPass.git
fi
cd $REPORT_PASS
make reporter.o pass
cd ..