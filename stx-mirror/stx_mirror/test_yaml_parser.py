#
# SPDX-License-Identifier: Apache-2.0
#

import unittest
from yaml_parser import YamlParser
from yaml_parser import CentOSPackageList
from yaml_parser import CentOSPackage
from exceptions import *
import yaml
import tempfile
import os

#        import pdb; pdb.set_trace()

class TempFiles:
    def __init__(self, content):
        self.tmp_file = tempfile.NamedTemporaryFile()
        self.name = self.tmp_file.name
        self.tmp_file.write(content)
        self.tmp_file.flush()

    def close(self):
        self.tmp_file.close()


class TestYamlParser(unittest.TestCase):
    def test_load_missing_yaml_file(self):
        yp = YamlParser()
        with self.assertRaises(IOError):
            _ = yp.load("somefile")

    def test_load_invalid_yaml_file(self):
        yp = YamlParser()
        tmp_file = TempFiles("Testing\n\n--:::")
        with self.assertRaises(yaml.YAMLError):
            _ = yp.load(tmp_file.name)
        tmp_file.close()

    def test_load_basic_valid_yaml(self):
        yp = YamlParser()
        test_yaml = """type: centos
rpms:
  - abattis-cantarell-fonts-0.0.25-1.el7.noarch.rpm
  - acl-2.2.51-14.el7.x86_64.rpm
  - acpica-tools-20160527-1.el7.x86_64.rpm
        """
        tmp_file = TempFiles(test_yaml)
        try:
            _ = yp.load(tmp_file.name)
        except Exception as e:
            self.assertTrue(False, "Exception received: {}".format(e))
        tmp_file.close()

    def test_load_and_compare_types(self):
        yp = YamlParser()
        test_yaml = """type: centos
rpms:
  - abattis-cantarell-fonts-0.0.25-1.el7.noarch.rpm
  - acl-2.2.51-14.el7.x86_64.rpm
  - acpica-tools-20160527-1.el7.x86_64.rpm
        """
        tmp_file = TempFiles(test_yaml)
        pkgs = yp.load(tmp_file.name)
        self.assertIsInstance(pkgs, CentOSPackageList)
        self.assertEquals(3, len(pkgs['rpms']))
        self.assertIsInstance(pkgs['rpms'][0], CentOSPackage)

    def test_load_with_invalid_type(self):
        yp = YamlParser()
        test_yaml = """type: sometype
rpms:
  - abattis-cantarell-fonts-0.0.25-1.el7.noarch.rpm
  - acl-2.2.51-14.el7.x86_64.rpm
  - acpica-tools-20160527-1.el7.x86_64.rpm
        """
        tmp_file = TempFiles(test_yaml)
        with self.assertRaises(UnsupportedPackageListType):
            _ = yp.load(tmp_file.name)

    def test_load_without_type(self):
        yp = YamlParser()
        test_yaml = """rpms:
  - abattis-cantarell-fonts-0.0.25-1.el7.noarch.rpm
  - acl-2.2.51-14.el7.x86_64.rpm
  - acpica-tools-20160527-1.el7.x86_64.rpm
        """
        tmp_file = TempFiles(test_yaml)
        with self.assertRaises(MissingPackageListType):
            _ = yp.load(tmp_file.name)


    def test_load_with_sections(self):
        yp = YamlParser()
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
        tmp_file = TempFiles(test_yaml)
        pkgs = yp.load(tmp_file.name)
        for section in ['rpms',
                        'rpms3rdparty',
                        'tarballs',
                        'bootfiles',
                        '3rdparty']:
            self.assertTrue(section in pkgs)
            self.assertEquals(3, len(pkgs[section]))


    def test_load_invalid_type(self):
        yp = YamlParser()
        test_yaml = """type: centos
  - abattis-cantarell-fonts-0.0.25-1.el7.noarch.rpm
  - acl-2.2.51-14.el7.x86_64.rpm
  - acpica-tools-20160527-1.el7.x86_64.rpm
"""
        tmp_file = TempFiles(test_yaml)
        with self.assertRaises(UnsupportedPackageListType):
            _ = yp.load(tmp_file.name)
