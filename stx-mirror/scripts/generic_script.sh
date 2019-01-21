#!/bin/bash

tarball_name=$1
directory_name=$2
download_directory=$3

pushd $download_directory
directory_name_original=$(tar -tf $tarball_name | head -1 | cut -f1 -d"/")
if [ "$directory_name" != "$directory_name_original" ]; then
    mkdir -p $directory_name
    tar xf $tarball_name --strip-components 1 -C $directory_name
    tar -czf $tarball_name $directory_name
    rm -r $directory_name
fi 
popd
