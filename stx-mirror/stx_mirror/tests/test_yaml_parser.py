#
# SPDX-License-Identifier: Apache-2.0
#

import unittest
from yaml_parser import YamlParser
from yaml_parser import CentOSPackageList
from yaml_parser import CentOSPackage
from stx_exceptions import *
import yaml
import tempfile
from configuration import Configuration

def create_configuration_for_testing_yaml(file_name):
        test_cfg = """[DownloadSettings]
base: ./output
release: stx-r1
distro: CentOS
openstack: pike
booturl: http://vault.centos.org/7.4.1708/os/x86_64/
maxthreads: 4
log: ./LogMirrorDownloader.log
input: {}""".format(file_name)
        tmp_test_file = TempFiles(test_cfg)
        config = Configuration()
        config.load(tmp_test_file.name)
        tmp_test_file.close()
        return config

class TempFiles:
    def __init__(self, content):
        self.tmp_file = tempfile.NamedTemporaryFile()
        self.name = self.tmp_file.name
        self.tmp_file.write(content)
        self.tmp_file.flush()

    def close(self):
        self.tmp_file.close()


class TestYamlParser(unittest.TestCase):

    def test_load_unsupported_config_file(self):
        yp = YamlParser()
        with self.assertRaises(UnsupportedConfigurationType):
            _ = yp.load("somefile")
        with self.assertRaises(UnsupportedConfigurationType):
            var = YamlParser()
            _ = yp.load(var)

    def test_load_incomplete_config_file(self):
        test_cfg = """[DownloadSettings]
base: ./output
release: stx-r1
booturl: http://vault.centos.org/7.4.1708/os/x86_64/
maxthreads: 4
log: ./LogMirrorDownloader.log
input: ../manifests/manifest.yaml"""
        tmp_test_file = TempFiles(test_cfg)
        config = Configuration()
        # forgot the load so config is incomplete...
        yp = YamlParser()
        try:
            _ = yp.load(config)
        except UnsupportedConfigurationType as e:
            self.assertTrue(True, "Exception received: {}".format(e))
        tmp_test_file.close()

    def test_load_missing_yaml_file(self):
        config = create_configuration_for_testing_yaml('doesntexist.yaml')
        yp = YamlParser()
        with self.assertRaises(IOError):
            _ = yp.load(config)

    def test_load_invalid_yaml_file(self):
        tmp_input_file = TempFiles("Testing\n\n--:::")
        config = create_configuration_for_testing_yaml(tmp_input_file.name)

        yp = YamlParser()

        with self.assertRaises(yaml.YAMLError):
            _ = yp.load(config)

        tmp_input_file.close()

    def test_load_basic_valid_yaml(self):
        test_yaml = """type: centos
rpms:
  - abattis-cantarell-fonts-0.0.25-1.el7.noarch.rpm
  - acl-2.2.51-14.el7.x86_64.rpm
  - acpica-tools-20160527-1.el7.x86_64.rpm
        """
        tmp_input_file = TempFiles(test_yaml)
        config = create_configuration_for_testing_yaml(tmp_input_file.name)

        yp = YamlParser()
        try:
            _ = yp.load(config)
        except Exception as e:
            self.assertTrue(False, "Exception received: {}".format(e))

        tmp_input_file.close()


    def test_load_and_compare_types(self):
        test_yaml = """type: centos
rpms:
  - abattis-cantarell-fonts-0.0.25-1.el7.noarch.rpm
  - acl-2.2.51-14.el7.x86_64.rpm
  - acpica-tools-20160527-1.el7.x86_64.rpm
        """
        tmp_input_file = TempFiles(test_yaml)
        config = create_configuration_for_testing_yaml(tmp_input_file.name)

        yp = YamlParser()
        pkgs = yp.load(config)

        self.assertIsInstance(pkgs, CentOSPackageList)
        self.assertEquals(3, len(pkgs['rpms']))
        self.assertIsInstance(pkgs['rpms'][0], CentOSPackage)

        tmp_input_file.close()

    def test_load_with_invalid_type(self):
        test_yaml = """type: sometype
rpms:
  - abattis-cantarell-fonts-0.0.25-1.el7.noarch.rpm
  - acl-2.2.51-14.el7.x86_64.rpm
  - acpica-tools-20160527-1.el7.x86_64.rpm
        """
        tmp_input_file = TempFiles(test_yaml)
        config = create_configuration_for_testing_yaml(tmp_input_file.name)

        yp = YamlParser()
        with self.assertRaises(UnsupportedPackageListType):
            _ = yp.load(config)

        tmp_input_file.close()

    def test_load_without_type(self):
        test_yaml = """rpms:
  - abattis-cantarell-fonts-0.0.25-1.el7.noarch.rpm
  - acl-2.2.51-14.el7.x86_64.rpm
  - acpica-tools-20160527-1.el7.x86_64.rpm
        """
        tmp_input_file = TempFiles(test_yaml)
        config = create_configuration_for_testing_yaml(tmp_input_file.name)

        yp = YamlParser()
        with self.assertRaises(MissingPackageListType):
            _ = yp.load(config)

        tmp_input_file.close()

    def test_load_with_sections(self):
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
        tmp_input_file = TempFiles(test_yaml)
        config = create_configuration_for_testing_yaml(tmp_input_file.name)

        yp = YamlParser()
        pkgs = yp.load(config)
        for section in ['rpms',
                        'rpms3rdparty',
                        'tarballs',
                        'bootfiles',
                        '3rdparty']:
            self.assertTrue(section in pkgs)
            self.assertEquals(3, len(pkgs[section]))

        tmp_input_file.close()

    def test_load_invalid_type(self):
        test_yaml = """type: centos
  - abattis-cantarell-fonts-0.0.25-1.el7.noarch.rpm
  - acl-2.2.51-14.el7.x86_64.rpm
  - acpica-tools-20160527-1.el7.x86_64.rpm
"""
        tmp_input_file = TempFiles(test_yaml)
        config = create_configuration_for_testing_yaml(tmp_input_file.name)

        yp = YamlParser()
        with self.assertRaises(UnsupportedPackageListType):
            _ = yp.load(config)

        tmp_input_file.close()
