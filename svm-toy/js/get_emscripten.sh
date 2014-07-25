#!/usr/bin/env bash

set -e

dir=`pwd`

echo "===== get emscripten ====="
if [ ! -e emscripten ] ; then
	git clone https://github.com/kripken/emscripten
fi


echo "===== get nodejs ====="
if [ ! -e node ] ; then
	git clone https://github.com/joyent/node
fi
cd node
./configure 
make -j 4
cd "$dir"


echo "===== get llvm ====="
if [ ! -e emscripten-fastcomp ] ; then
	git clone https://github.com/kripken/emscripten-fastcomp
fi
cd emscripten-fastcomp/tools
if [ ! -e clang ] ; then
	git clone https://github.com/kripken/emscripten-fastcomp-clang clang
fi
cd ..
mkdir -p build
cd build
../configure --enable-optimized --disable-assertions --enable-targets=host,js
make -j 4
cd "$dir"

$dir/emscripten/em++ --version

echo "===== paths of em++ and emcc ======"
echo $dir/emscripten/em++
echo $dir/emscripten/emcc
echo "===== please modify $HOME/.emscripten ======"
echo "EMSCRIPTEN_ROOT = '$dir/emscripten/'"
echo "LLVM_ROOT = '$dir/emscripten-fastcomp/build/Release/bin'"
echo "NODE_JS = '$dir/node/node'"
