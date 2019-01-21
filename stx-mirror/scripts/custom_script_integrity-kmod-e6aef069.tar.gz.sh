#!/bin/bash

tarball_name=$1
directory_name=$2
download_directory=$3

tar xf e6aef069b6e97790cb127d5eeb86ae9ff0b7b0e3.tar.gz
mv linux-tpmdd-e6aef06/security/integrity/ $directory_name
tar czvf $tarball_name $directory_name
rm -rf linux-tpmdd-e6aef06
rm e6aef069b6e97790cb127d5eeb86ae9ff0b7b0e3.tar.gz
