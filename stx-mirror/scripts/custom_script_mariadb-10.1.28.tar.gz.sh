#!/bin/bash

tarball_name=$1
directory_name=$2
download_directory=$3

pushd $download_directory

mkdir $directory_name
tar xf $tarball_name --strip-components 1 -C $directory_name
rm $tarball_name
pushd $directory_name
rm -rf storage/tokudb
rm ./man/tokuft_logdump.1 ./man/tokuftdump.1
sed -e s/tokuft_logdump.1//g -i man/CMakeLists.txt
sed -e s/tokuftdump.1//g -i man/CMakeLists.txt
popd
tar czvf $tarball_name $directory_name
rm -rf $directory_name
popd
