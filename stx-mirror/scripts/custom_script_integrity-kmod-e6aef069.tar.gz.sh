#!/bin/bash

tarball_name=$1
directory_name=$2
download_directory=$3
pushd $download_directory
tar xf ${tarballl_name}
mv linux-tpmdd-e6aef06/security/integrity/ $directory_name
tar czvf $tarball_name $directory_name
rm -rf linux-tpmdd-e6aef06
popd
