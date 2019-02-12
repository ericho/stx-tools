#!/bin/bash

tarball_name=$1
directory_name=$2
download_directory=$3

pushd $download_directory

tar xf $tarball_name
mv linux-tpmdd-e6aef06/drivers/char/tpm $directory_name
tar czvf $tarball_name $directory_name
rm -rf linux-tpmdd-e6aef06
rm -rf $directory_name

popd
