#!/bin/bash

tarball_name=$1
directory_name=$2
download_directory=$3

pkg_version=$(echo "$tarball_name" | cut -d "-" -f2-3)
srpm_path="MLNX_OFED_SRC-${pkg_version}/SRPMS/"

tar -xf "$tarball_name"
tar -xf "$directory_name/src/MLNX_OFED_SRC-${pkg_version}.tgz"
# This section of code gets specific SRPMs versions according
# to the OFED tarbal version,
if [ "$pkg_version" = "4.2-1.2.0.0" ]; then
    cp "$srpm_path/libibverbs-41mlnx1-OFED.4.2.1.0.6.42120.src.rpm" .
elif [ "$pkg_version" = "4.3-1.0.1.0" ]; then
    cp "$srpm_path/mlnx-ofa_kernel-4.3-OFED.4.3.1.0.1.1.g8509e41.src.rpm" .
    cp "$srpm_path/rdma-core-43mlnx1-1.43101.src.rpm" .
    cp "$srpm_path/libibverbs-41mlnx1-OFED.4.3.0.1.8.43101.src.rpm" .
elif [ "$pkg_version" = "4.3-3.0.2.1" ]; then
    cp "$srpm_path/mlnx-ofa_kernel-4.3-OFED.4.3.3.0.2.1.gcf60532.src.rpm" .
    cp "$srpm_path/rdma-core-43mlnx1-1.43302.src.rpm" .
    cp "$srpm_path/libibverbs-41mlnx1-OFED.4.3.2.1.6.43302.src.rpm" .
else
    echo "$pkg_version : unknown version"
fi
# Don't delete the original MLNX_OFED_LINUX tarball.
# We don't use it, but it will prevent re-downloading this file.
#   rm -f "$tarball_name"

rm -rf "MLNX_OFED_SRC-${pkg_version}"
rm -rf "$directory_name"
