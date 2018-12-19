#
# SPDX-License-Identifier: Apache-2.0
#

import unittest
from package import CentOSPackage
from stx_exceptions import *
from test_yaml_parser import TempFiles
from configuration import Configuration
import os
import mock
import pdb
import urllib2

def mocked_urllib2_urlopen(*args, **kwargs):
    class MockResponse:
        def __init__(self, data, retcode):
            self.data = data
            self.retcode = retcode
        def read(self):
            return self.data
    if args[0].startswith('http://'):
        return MockResponse('Mock downloaded URL {}\n'.format(args[0]), 0)
    else:
        return MockResponse('Mock downloaded URL FAIL {}\n'.format(args[0]), 1)

def mocked_komander_run(*args, **kwargs):
    class MockResponse:
        def __init__(self, data, retcode):
            self.cmd = data
            self.retcode = retcode
        def read(self):
            return self.cmd
    if args[0].find('doesntexist') == -1 :
        return MockResponse('Mock downloaded RPM {}\n'.format(args[0]), 0)
    else:
        return MockResponse('Mock downloaded RPM FAIL {}\n'.format(args[0]), 1)

def create_configuration_for_testing_centos_package():
        test_cfg = """[DownloadSettings]
base: output
release: stx-r1
distro: CentOS
openstack: pike
booturl: http://vault.centos.org/7.4.1708/os/x86_64/
maxthreads: 4
log: LogMirrorDownloader.log
input: ../manifests/manifest.yaml"""
        tmp_test_file = TempFiles(test_cfg)
        config = Configuration()
        config.load(tmp_test_file.name)
        tmp_test_file.close()
        return config


class TestCentOSPackage(unittest.TestCase):

    def test_new_package_basedir(self):
        conf = create_configuration_for_testing_centos_package()
        rpm = 'acl-2.2.51-14.el7.x86_64.rpm'
        pkg = CentOSPackage(rpm, conf)
        expected = os.path.join('output', 'stx-r1', 'CentOS', 'pike')
        self.assertEquals(expected, pkg._basedir)

    def test_new_package_with_rpm(self):
        conf = create_configuration_for_testing_centos_package()
        rpm = 'acl-2.2.51-14.el7.x86_64.rpm'
        pkg = CentOSPackage(rpm, conf)
        self.assertEquals(rpm, pkg.name)
        self.assertEquals(None, pkg.url)
        self.assertEquals(None, pkg.script)

    def test_new_package_with_url(self):
        conf = create_configuration_for_testing_centos_package()
        url = 'http://someurl.org/go-srpm-macros-2-3.el7.noarch.rpm'
        pkg = CentOSPackage(url, conf)
        self.assertEquals('go-srpm-macros-2-3.el7.noarch.rpm', pkg.name)
        self.assertEquals(url, pkg.url)
        self.assertEquals(None, pkg.script)

    def test_new_package_with_dict_full(self):
        conf = create_configuration_for_testing_centos_package()
        d = {
            'name': 'drbd-8.4.3.tar.gz',
            'url': 'http://www.linbit.com/downloads/drbd/8.4/archive/drbd-8.4.3.tar.gz',
            'script': 'myscript.sh'
        }
        pkg = CentOSPackage(d, conf)
        self.assertEquals(d['name'], pkg.name)
        self.assertEquals(d['url'], pkg.url)
        self.assertEquals(d['script'], pkg.script)

    def test_new_package_with_dict_no_script(self):
        conf = create_configuration_for_testing_centos_package()
        d = {
            'name': 'drbd-8.4.3.tar.gz',
            'url': 'http://www.linbit.com/downloads/drbd/8.4/archive/drbd-8.4.3.tar.gz',
        }
        pkg = CentOSPackage(d, conf)
        self.assertEquals(d['name'], pkg.name)
        self.assertEquals(d['url'], pkg.url)
        self.assertEquals(None, pkg.script)

    def test_new_package_with_unsupported_data(self):
        conf = create_configuration_for_testing_centos_package()
        d = 123124
        try:
            pkg = CentOSPackage(d, conf)
        except UnsupportedPackageType as e:
            self.assertTrue(True, "Exception received: {}".format(e))

    def test_new_package_with_large_url(self):
        conf = create_configuration_for_testing_centos_package()
        url = 'http://cbs.centos.org/kojifiles/packages/go-srpm-macros/2/3.el7/noarch/go-srpm-macros-2-3.el7.noarch.rpm'
        pkg = CentOSPackage(url, conf)
        self.assertEquals('go-srpm-macros-2-3.el7.noarch.rpm', pkg.name)
        self.assertEquals(url, pkg.url)
        self.assertEquals(None, pkg.script)

    def test_new_package_with_invalid_rpm(self):
        conf = create_configuration_for_testing_centos_package()
        rpm = 'acl-2.2.51-14.el7.x86_64'
        with self.assertRaises(UnsupportedPackageType):
            pkg = CentOSPackage(rpm, conf)

    def test_new_package_with_invalid_dict_only_script(self):
        conf = create_configuration_for_testing_centos_package()
        d = {
            'script': 'myscript.sh'
        }
        with self.assertRaises(UnsupportedPackageType):
            pkg = CentOSPackage(d, conf)

    def test_new_package_with_invalid_dict_only_name(self):
        conf = create_configuration_for_testing_centos_package()
        d = {
            'name': 'drbd-8.4.3.tar.gz',
        }
        with self.assertRaises(UnsupportedPackageType):
            pkg = CentOSPackage(d, conf)

    @mock.patch('package.Komander.run', side_effect=mocked_komander_run)
    def test_download_rpm_x86_success(self, mocked_run):
        conf = create_configuration_for_testing_centos_package()
        rpm = 'acl-2.2.51-14.el7.x86_64.rpm'
        pkg = CentOSPackage(rpm, conf)
        try:
            cmd = pkg.download()
        except Exception as e:
            self.assertTrue(False, 'Exception received: {}'.format(e))

    @mock.patch('package.Komander.run', side_effect=mocked_komander_run)
    def test_download_rpm_src_success(self, mocked_run):
        conf = create_configuration_for_testing_centos_package()
        rpm = 'anaconda-21.48.22.121-1.el7.centos.src.rpm'
        pkg = CentOSPackage(rpm, conf)
        try:
            cmd = pkg.download()
        except Exception as e:
            self.assertTrue(False, 'Exception received: {}'.format(e))

    @mock.patch('package.urllib2.urlopen', side_effect=mocked_urllib2_urlopen)
    def test_download_url_success(self, mock_urlopen):
        conf = create_configuration_for_testing_centos_package()
        url = 'http://cbs.centos.org/kojifiles/packages/go-srpm-macros/2/3.el7/noarch/go-srpm-macros-2-3.el7.noarch.rpm'
        pkg = CentOSPackage(url, conf)
        pkg.download()
        os.remove('output/stx-r1/CentOS/pike/Binary/noarch/go-srpm-macros-2-3.el7.noarch.rpm')

    @mock.patch('package.Komander.run', side_effect=mocked_komander_run)
    def test_download_rpm_x86_failure(self, mocked_run):
        conf = create_configuration_for_testing_centos_package()
        rpm = 'doesntexist-2.2.51-14.el7.x86_64.rpm'
        pkg = CentOSPackage(rpm, conf)
        try:
            cmd = pkg.download()
        except DownloadError as e:
            self.assertTrue(True, 'Exception received: {}'.format(e))

    @mock.patch('package.Komander.run', side_effect=mocked_komander_run)
    def test_download_rpm_src_failure(self, mocked_run):
        conf = create_configuration_for_testing_centos_package()
        rpm = 'anaconda-21.48.22.121-1.el7.centos.src.rpm'
        pkg = CentOSPackage(rpm, conf)
        try:
            cmd = pkg.download()
        except DownloadError as e:
            self.assertTrue(True, 'Exception received: {}'.format(e))

    @mock.patch('package.urllib2.urlopen', side_effect=urllib2.URLError('Mocked Error'))
    def test_download_url_failure(self, mock_urlopen):
        conf = create_configuration_for_testing_centos_package()
        url = 'hhhttp://cbs.centos.org/kojifiles/packages/go-srpm-macros/2/3.el7/noarch/go-srpm-macros-2-3.el7.noarch.rpm'
        pkg = CentOSPackage(url, conf)
        try:
            pkg.download()
        except DownloadError as e:
            self.assertTrue(True, 'Exception received: {}'.format(e))

    #
    # THIS TEST IS NOT WORKING YET
    #
    def test_download_dict(self):
        conf = create_configuration_for_testing_centos_package()
        d = {
            'name': 'drbd-8.4.3.tar.gz',
            'url': 'http://www.linbit.com/downloads/drbd/8.4/archive/drbd-8.4.3.tar.gz',
            'script': 'myscript.sh'
        }
        pkg = CentOSPackage(d, conf)
        self.assertEquals(d['name'], pkg.name)
        self.assertEquals(d['url'], pkg.url)
        self.assertEquals(d['script'], pkg.script)

