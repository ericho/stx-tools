#
# SPDX-License-Identifier: Apache-2.0
#

import os
import mock
import requests

from test_common import StxTest
from package import CentOSPackage, CentOSPackageList
from stx_exceptions import *
from test_yaml_parser import TempFiles, create_configuration_for_testing_yaml
from configuration import Configuration

def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, data, retcode):
            self.retcode = retcode
            self.content = data
    if args[0].startswith('http://'):
        return MockResponse('Mock downloaded URL\n{}\n'.format(args[0]), 0)
    else:
        return MockResponse('Mock downloaded URL FAIL\n{}\n'.format(args[0]), 1)

def mocked_komander_run(*args, **kwargs):
    class MockResponse:
        def __init__(self, data, retcode):
            self.cmd = data
            self.retcode = retcode
            self.stdout = ''
        def read(self):
            return self.cmd

    if 'anaconda-21' in args[0]:
        m = MockResponse('Mock downloaded RPM\n{}\n'.format(args[0]), 0)
        package_dir = 'output/stx-r1/CentOS/pike/Source'
        datatowrite = m.cmd
        if not os.path.exists(package_dir):
            os.makedirs(package_dir)
        with open('{}/{}'.format(package_dir,
                  'anaconda-21.48.22.121-1.el7.centos.src.rpm'),
                  'wb') as f:
            f.write(datatowrite)
        return m
    elif 'acl-2' in args[0]:
        m = MockResponse('Mock downloaded RPM\n{}\n'.format(args[0]), 0)
        package_dir = 'output/stx-r1/CentOS/pike/Binary/x86_64'
        datatowrite = m.cmd
        if not os.path.exists(package_dir):
            os.makedirs(package_dir)
        with open('{}/{}'.format(package_dir,
                  'acl-2.2.51-14.el7.x86_64.rpm'),
                  'wb') as f:
            f.write(datatowrite)
        return m
    elif args[0].find('doesntexist'):
        return MockResponse('Mock downloaded RPM FAIL\n{}\n'.format(args[0]), 1)

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

run_setup_retcode = 0

def mocked_komander(cmd, timeout=0):
    class MockResponse:
        def __init__(self, data, retcode):
            self.cmd = data
            self.retcode = retcode
            self.stderr = "Generic error"
            self.stdout = 'Generic stdout'
        def read(self):
            return self.cmd

    return MockResponse("Some generic cmd", run_setup_retcode)


class TestCentOSPackageList(StxTest):

    @mock.patch('package.Komander.run', side_effect=mocked_komander)
    def test_basic_setup(self, mocked_run):
        cfg = create_configuration_for_testing_centos_package()
        pkgs = CentOSPackageList([], cfg)
        try:
            pkgs.setup()
        except StxException as e:
            self.assertTrue(False, "Exception received {}".format(e))

    @mock.patch('package.Komander.run', side_effect=mocked_komander)
    def test_basic_setup_command_failed(self, mocked_run):
        cfg = create_configuration_for_testing_centos_package()
        pkgs = CentOSPackageList([], cfg)
        global run_setup_retcode
        run_setup_retcode = 1
        with self.assertRaises(SetupError):
            pkgs.setup()


class TestCentOSPackage(StxTest):

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
        pkgdir = 'output/stx-r1/CentOS/pike/Binary/x86_64/acl-2.2.51-14.el7.x86_64.rpm'
        assert os.path.exists(pkgdir) == 1
        os.remove(pkgdir)


    @mock.patch('package.Komander.run', side_effect=mocked_komander_run)
    def test_download_rpm_src_success(self, mocked_run):
        conf = create_configuration_for_testing_centos_package()
        rpm = 'anaconda-21.48.22.121-1.el7.centos.src.rpm'
        pkg = CentOSPackage(rpm, conf)
        try:
            cmd = pkg.download()
        except Exception as e:
            self.assertTrue(False, 'Exception received: {}'.format(e))
        pkgdir = 'output/stx-r1/CentOS/pike/Source/anaconda-21.48.22.121-1.el7.centos.src.rpm'
        self.assertTrue(os.path.exists(pkgdir))
        os.remove(pkgdir)

    @mock.patch('package.requests.get', side_effect=mocked_requests_get)
    def test_download_url_success(self, mock_urlopen):
        conf = create_configuration_for_testing_centos_package()
        url = 'http://cbs.centos.org/kojifiles/packages/go-srpm-macros/2/3.el7/noarch/go-srpm-macros-2-3.el7.noarch.rpm'
        pkg = CentOSPackage(url, conf)
        pkg.download()
        pkgdir = 'output/stx-r1/CentOS/pike/Binary/noarch/go-srpm-macros-2-3.el7.noarch.rpm'
        self.assertTrue(os.path.exists(pkgdir))
        os.remove(pkgdir)

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
        rpm = 'doesntexist-21.48.22.121-1.el7.centos.src.rpm'
        pkg = CentOSPackage(rpm, conf)
        try:
            cmd = pkg.download()
        except DownloadError as e:
            self.assertTrue(True, 'Exception received: {}'.format(e))

    @mock.patch('package.requests.get', side_effect=requests.exceptions.RequestException('Mocked Error'))
    def test_download_url_failure(self, mock_urlopen):
        conf = create_configuration_for_testing_centos_package()
        url = 'hhhttp://cbs.centos.org/kojifiles/packages/go-srpm-macros/2/3.el7/noarch/go-srpm-macros-2-3.el7.noarch.rpm'
        pkg = CentOSPackage(url, conf)
        try:
            pkg.download()
        except DownloadError as e:
            self.assertTrue(True, 'Exception received: {}'.format(e))

    def test_name_to_destdir(self):
        conf = create_configuration_for_testing_centos_package()
        rpm = 'anaconda-21.48.22.121-1.el7.centos.x86_64.rpm'
        pkg = CentOSPackage(rpm, conf)
        self.assertEquals('Binary/x86_64', pkg._get_destdir())

        rpm = 'anaconda-21.48.22.121-1.el7.centos.noarch.rpm'
        pkg = CentOSPackage(rpm, conf)
        self.assertEquals('Binary/noarch', pkg._get_destdir())

        rpm = 'anaconda-21.48.22.121-1.el7.centos.src.rpm'
        pkg = CentOSPackage(rpm, conf)
        self.assertEquals('Source', pkg._get_destdir())

        url = 'http://cbs.centos.org/go-srpm-macros-2-3.el7.noarch.rpm'
        pkg = CentOSPackage(url, conf)
        self.assertEquals('Binary/noarch', pkg._get_destdir())

        url = 'http://www.linbit.com/downloads/drbd/8.4/archive/drbd-8.4.3.tar.gz'
        pkg = CentOSPackage(url, conf)
        self.assertEquals('downloads', pkg._get_destdir())

        url = 'http://launchpad.net/smart-1.4.1.tar.bz2'
        pkg = CentOSPackage(url, conf)
        self.assertEquals('downloads', pkg._get_destdir())

        url = 'http://vault.centos.org/7.4.1708/os/x86_64/EFI/BOOT/grub.cfg'
        pkg = CentOSPackage(url, conf)
        self.assertEquals(url, pkg.url)
        self.assertEquals('Binary/EFI/BOOT', pkg._get_destdir())

        url = 'http://vault.centos.org/7.4.1708/os/x86_64/EFI/BOOT/fonts/unicode.pf2'
        pkg = CentOSPackage(url, conf)
        self.assertEquals(url, pkg.url)
        self.assertEquals('Binary/EFI/BOOT/fonts', pkg._get_destdir())

        url = 'http://vault.centos.org/7.4.1708/os/x86_64/LiveOS/squashfs.img'
        pkg = CentOSPackage(url, conf)
        self.assertEquals(url, pkg.url)
        self.assertEquals('Binary/LiveOS', pkg._get_destdir())

        url = 'http://vault.centos.org/7.4.1708/os/x86_64/images/pxeboot/vmlinuz'
        pkg = CentOSPackage(url, conf)
        self.assertEquals(url, pkg.url)
        self.assertEquals('Binary/images/pxeboot', pkg._get_destdir())

        url = 'http://vault.centos.org/7.4.1708/os/x86_64/isolinux/vmlinuz'
        pkg = CentOSPackage(url, conf)
        self.assertEquals(url, pkg.url)
        self.assertEquals('Binary/isolinux', pkg._get_destdir())

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

