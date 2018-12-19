#
# SPDX-License-Identifier: Apache-2.0
#

import unittest

from package import CentOSPackage
from threadpool import download, download_all, PackageResult
from yaml_parser import YamlParser
from test_yaml_parser import TempFiles, create_configuration_for_testing_yaml
from stx_exceptions import DownloadError, UnsupportedDownloadPackageType


def create_dummy_packages(dummy_yaml):
    tmp_input_file = TempFiles(dummy_yaml)
    conf = create_configuration_for_testing_yaml(tmp_input_file.name)
    yp = YamlParser()
    return yp.load(conf)

def update_download(pkgs, f):
    for p in pkgs:
        for l in pkgs[p]:
            l.download = f


class TestThreadPool(unittest.TestCase):

    def test_download_all_convert_dict_to_lists(self):
        test_yaml = """type: centos
rpms:
  - abattis-cantarell-fonts-0.0.25-1.el7.noarch.rpm
  - acl-2.2.51-14.el7.x86_64.rpm
  - acpica-tools-20160527-1.el7.x86_64.rpm
rpms3rdparty:
  - adwaita-cursor-theme-3.26.0-1.el7.noarch.rpm
  - adwaita-icon-theme-3.26.0-1.el7.noarch.rpm
  - alsa-lib-1.1.4.1-2.el7.x86_64.rpm
tarballs:
  - name: dpkg_1.18.24.tar.xz
    url: http://http.debian.net/debian/pool/main/d/dpkg/dpkg_1.18.24.tar.xz
  - name: drbd-8.4.3.tar.gz
    url: http://www.linbit.com/downloads/drbd/8.4/archive/drbd-8.4.3.tar.gz
    script: myscript.sh
  - http://www.linbit.com/downloads/drbd/8.4/drbd-8.4.7-1.tar.gz
bootfiles:
  - http://vault.centos.org/7.4.1708/os/x86_64/EFI/BOOT/grub.cfg
  - http://vault.centos.org/7.4.1708/os/x86_64/EFI/BOOT/BOOTX64.EFI
  - http://vault.centos.org/7.4.1708/os/x86_64/EFI/BOOT/grubx64.efi
3rdparty:
  - http://someurl.org/go-srpm-macros-2-3.el7.noarch.rpm
  - http://someurl.org/golang-1.10.2-1.el7.x86_64.rpm
  - http://someurl.org/golang-bin-1.10.2-1.el7.x86_64.rpm
"""

        def my_dummy_download():
            pass

        pkgs = create_dummy_packages(test_yaml)

        pkg_counter = 0
        for p in pkgs:
            for l in pkgs[p]:
                l.download = my_dummy_download
                pkg_counter += 1
        res = download_all(pkgs)
        self.assertEquals(len(res), pkg_counter)
        self.assertIsInstance(res[0], PackageResult)

    def test_download_success(self):
        test_yaml = """type: centos
rpms:
  - abattis-cantarell-fonts-0.0.25-1.el7.noarch.rpm
  - acl-2.2.51-14.el7.x86_64.rpm
  - acpica-tools-20160527-1.el7.x86_64.rpm
"""
        pkgs = create_dummy_packages(test_yaml)

        def my_dummy_download():
            return

        update_download(pkgs, my_dummy_download)

        res = download_all(pkgs)
        self.assertEquals(res[0].success, True)
        self.assertEquals(res[0].e, None)
        self.assertEquals(res[0].pkg, None)

    def test_download_return_exception(self):
        test_yaml = """type: centos
rpms:
  - abattis-cantarell-fonts-0.0.25-1.el7.noarch.rpm
  - acl-2.2.51-14.el7.x86_64.rpm
  - acpica-tools-20160527-1.el7.x86_64.rpm
"""
        pkgs = create_dummy_packages(test_yaml)

        def my_dummy_download():
            raise DownloadError

        update_download(pkgs, my_dummy_download)

        res = download_all(pkgs)
        self.assertEquals(res[0].success, False)
        self.assertNotEquals(res[0].e, None)
        self.assertNotEquals(res[0].pkg, None)

    def test_download_invalid_type(self):
        with self.assertRaises(UnsupportedDownloadPackageType):
            download("some invalid type")
