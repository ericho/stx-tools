#
# SPDX-License-Identifier: Apache-2.0
#

from test_common import StxTest
from configuration import Configuration
from stx_exceptions import *
from test_yaml_parser import TempFiles
import pdb


class TestConfiguration(StxTest):

    def test_load_configuration_file_exists(self):
        test_cfg = """[DownloadSettings]
base: ./output
release: stx-r1
distro: CentOS
openstack: pike
booturl: http://vault.centos.org/7.4.1708/os/x86_64/
maxthreads: 4
log: ./LogMirrorDownloader.log
input: ./manifest/manifest.yaml"""
        tmp_file = TempFiles(test_cfg)
        config = Configuration()
        try:
            config.load(tmp_file.name)
        except Exception as e:
            self.assertTrue(False, "Exception received: {}".format(e))
        tmp_file.close()

    def test_load_configuration_not_valid_zero_sections(self):
        test_cfg = """
base: ./output
release: stx-r1
distro: CentOS
openstack: pike
booturl: http://vault.centos.org/7.4.1708/os/x86_64/
maxthreads: 4
log: ./LogMirrorDownloader.log
input: ./manifest/manifest.yaml"""
        tmp_file = TempFiles(test_cfg)
        config = Configuration()
        try:
            config.load(tmp_file.name)
        except UnsupportedConfigurationType as e:
            self.assertTrue(True, "Exception received: {}".format(e))
        tmp_file.close()

    def test_load_configuration_not_valid_file_empty(self):
        test_cfg = """"""
        tmp_file = TempFiles(test_cfg)
        config = Configuration()
        try:
            config.load(tmp_file.name)
        except UnsupportedConfigurationType as e:
            self.assertTrue(True, "Exception received: {}".format(e))
        tmp_file.close()

    def test_load_configuration_file_does_not_exist(self):
        config = Configuration()
        try:
            config.load("unexistent.cfg")
        except UnsupportedConfigurationType as e:
            self.assertTrue(True, "Exception received: {}".format(e))

    def test_load_configuration_wrong_type_int(self):
        config = Configuration()
        try:
            config.load(234)
        except TypeError as e:
            self.assertTrue(True, "Exception received: {}".format(e))

    def test_load_configuration_wrong_type_var(self):
        test_cfg = """[DownloadSettings]
base: ./output
release: stx-r1
distro: CentOS
openstack: pike
booturl: http://vault.centos.org/7.4.1708/os/x86_64/
maxthreads: 4
log: ./LogMirrorDownloader.log
input: ./manifest/manifest.yaml"""
        bla = TempFiles(test_cfg)
        config = Configuration()
        try:
            config.load(bla)
        except TypeError as e:
            self.assertTrue(True, "Exception received: {}".format(e))

    def test_load_configuration_not_valid_cfg(self):
        test_cfg = """[DownloadSettings
base/output releasestx-r1 distro: CentOS openstack: pike booturl: http://vault.centos.org/7.4.1708/os/x86_64/ maxthreads: 4 log: ./LogMirrorDownloader.log input: ./manifest/manifest.yaml"""
        tmp_file = TempFiles(test_cfg)
        config = Configuration()
        try:
            config.load(tmp_file.name)
        except UnsupportedConfigurationType as e:
            self.assertTrue(True, "Exception received: {}".format(e))

        tmp_file.close()

    def test_load_configuration_not_valid_many_sections(self):
        test_cfg = """[DownloadSettings]
base: ./output
release: stx-r1
distro: CentOS
openstack: pike
booturl: http://vault.centos.org/7.4.1708/os/x86_64/
maxthreads: 4
log: ./LogMirrorDownloader.log
input: ./manifest/manifest.yaml
[DownloadSettingsPart2]
base: ./output
release: stx-r1
distro: CentOS
openstack: pike
booturl: http://vault.centos.org/7.4.1708/os/x86_64/
maxthreads: 4
log: ./LogMirrorDownloader.log
input: ./manifest/manifest.yaml"""
        tmp_file = TempFiles(test_cfg)
        config = Configuration()
        try:
            config.load(tmp_file.name)
        except UnsupportedConfigurationType as e:
            self.assertTrue(True, "Exception received: {}".format(e))
        tmp_file.close()

    def test_load_configuration_not_valid_zero_options(self):
        test_cfg = """[DownloadSettings]"""
        tmp_file = TempFiles(test_cfg)
        config = Configuration()
        try:
            config.load(tmp_file.name)
        except UnsupportedConfigurationType as e:
            self.assertTrue(True, "Exception received: {}".format(e))
        tmp_file.close()

    def test_configuration_variables(self):
        test_cfg = """[DownloadSettings]
base: ./mirror
release: stx-r30
distro: Ubuntu
openstack: pike
booturl: http://files.org/os/x86_64/
maxthreads: 16
log: ./Log.log
input: ./manifest/othermanifest.yaml"""
        tmp_file = TempFiles(test_cfg)
        config = Configuration()
        try:
            config.load(tmp_file.name)
        except Exception as e:
            self.assertTrue(False, "Exception received: {}".format(e))
        tmp_file.close()

        self.assertEquals(config.base, "./mirror")
        self.assertEquals(config.release, "stx-r30")
        self.assertEquals(config.distro, "Ubuntu")
        self.assertEquals(config.openstack, "pike")
        self.assertEquals(config.booturl, "http://files.org/os/x86_64/")
        self.assertEquals(config.maxthreads, 16)
        self.assertEquals(config.logfile, "./Log.log")
        self.assertEquals(config.input, "./manifest/othermanifest.yaml")

    def test_configuration_variables_error_maxthreads(self):
        test_cfg = """[DownloadSettings]
base: ./mirror
release: stx-r30
distro: Ubuntu
openstack: pike
booturl: http://files.org/os/x86_64/
maxthreads: four
log: ./Log.log
input: ./manifest/othermanifest.yaml"""
        tmp_file = TempFiles(test_cfg)
        config = Configuration()
        try:
            config.load(tmp_file.name)
        except UnsupportedConfigurationValue as e:
            self.assertTrue(True, "Exception received: {}".format(e))
        tmp_file.close()

    def test_configuration_variables_missing_base(self):
        test_cfg = """[DownloadSettings]
release: stx-r30
distro: Ubuntu
openstack: pike
booturl: http://files.org/os/x86_64/
maxthreads: 16
log: ./Log.log
input: ./manifest/othermanifest.yaml"""
        tmp_file = TempFiles(test_cfg)
        config = Configuration()
        config.load(tmp_file.name)
        tmp_file.close()
        self.assertEquals(config.base, "./output")
        self.assertEquals(config.release, "stx-r30")
        self.assertEquals(config.distro, "Ubuntu")
        self.assertEquals(config.openstack, "pike")
        self.assertEquals(config.booturl, "http://files.org/os/x86_64/")
        self.assertEquals(config.maxthreads, 16)
        self.assertEquals(config.logfile, "./Log.log")
        self.assertEquals(config.input, "./manifest/othermanifest.yaml")

    def test_configuration_variables_missing_release(self):
        test_cfg = """[DownloadSettings]
base: ./mirror
distro: Ubuntu
openstack: pike
booturl: http://files.org/os/x86_64/
maxthreads: 16
log: ./Log.log
input: ./manifest/othermanifest.yaml"""
        tmp_file = TempFiles(test_cfg)
        config = Configuration()
        try:
            config.load(tmp_file.name)
        except MissingConfigurationValue as e:
            self.assertTrue(True, "Exception received: {}".format(e))
        tmp_file.close()
