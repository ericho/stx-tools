#!/bin/bash

tarball_name=$1
directory_name=$2
download_directory=$3

dest_dir=ibmtpm20tss-tss
for dl_src in $dl_source; do
    case $dl_src in
        $dl_from_stx_mirror)
            url="$(url_to_stx_mirror_url "$tarball_url" "$distro")"
            ;;
        $dl_from_upstream)
            url="$tarball_url"
            ;;
        *)
            echo "Error: Unknown dl_source '$dl_src'"
            continue
            ;;
    esac

    git clone $url $dest_dir
    if [ $? -eq 0 ]; then
        # Success
        break
    else
        echo "Warning: Failed to git clone from '$url'"
        continue
    fi
done

if [ ! -d $dest_dir ]; then
    echo "Error: Failed to git clone from '$tarball_url'"
    echo "$tarball_url" > "$output_log"
    error_count=$((error_count + 1))
    popd    # pushd $output_tarball
    continue
fi

pushd $dest_dir
branch=$util
git checkout $branch
rm -rf .git
popd
mv ibmtpm20tss-tss $directory_name
tar czvf $tarball_name $directory_name
rm -rf $directory_name
popd     # pushd $dest_dir
