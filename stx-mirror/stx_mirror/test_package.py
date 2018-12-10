#
# SPDX-License-Identifier: Apache-2.0
#

import unittest
from package import CentOSPackage
from stx_exceptions import *

class TestCentOSPackage(unittest.TestCase):

    def test_new_package_with_rpm(self):
        rpm = 'acl-2.2.51-14.el7.x86_64.rpm'
        pkg = CentOSPackage(rpm)
        self.assertEquals(rpm, pkg.name)
        self.assertEquals(None, pkg.url)
        self.assertEquals(None, pkg.script)

    def test_new_package_with_url(self):
        url = 'http://someurl.org/go-srpm-macros-2-3.el7.noarch.rpm'
        pkg = CentOSPackage(url)
        self.assertEquals('go-srpm-macros-2-3.el7.noarch.rpm', pkg.name)
        self.assertEquals(url, pkg.url)
        self.assertEquals(None, pkg.script)

    def test_new_package_with_dict(self):
        d = {
            'name': 'drbd-8.4.3.tar.gz',
            'url': 'http://www.linbit.com/downloads/drbd/8.4/archive/drbd-8.4.3.tar.gz',
            'script': 'myscript.sh'
        }
        pkg = CentOSPackage(d)
        self.assertEquals(d['name'], pkg.name)
        self.assertEquals(d['url'], pkg.url)
        self.assertEquals(d['script'], pkg.script)

    def test_new_package_with_large_url(self):
        url = 'http://cbs.centos.org/kojifiles/packages/go-srpm-macros/2/3.el7/noarch/go-srpm-macros-2-3.el7.noarch.rpm'
        pkg = CentOSPackage(url)
        self.assertEquals('go-srpm-macros-2-3.el7.noarch.rpm', pkg.name)
        self.assertEquals(url, pkg.url)
        self.assertEquals(None, pkg.script)

    def test_new_package_with_invalid_rpm(self):
        rpm = 'acl-2.2.51-14.el7.x86_64'
        with self.assertRaises(UnsupportedPackageType):
            pkg = CentOSPackage(rpm)

    def test_new_package_with_invalid_dict_only_script(self):
        d = {
            'script': 'myscript.sh'
        }
        with self.assertRaises(UnsupportedPackageType):
            pkg = CentOSPackage(d)

    def test_new_package_with_invalid_dict_only_name(self):
        d = {
            'name': 'drbd-8.4.3.tar.gz',
        }
        with self.assertRaises(UnsupportedPackageType):
            pkg = CentOSPackage(d)

    def test_download_rpm_x86(self):
        rpm = 'acl-2.2.51-14.el7.x86_64.rpm'
        pkg = CentOSPackage(rpm)
        cmd = pkg.download()
        self.assertEquals(cmd, "sudo -E yumdownloader -q -C --releasever=7 -x \*i686 --archlist=noarch,x86_64 acl-2.2.51-14.el7 --destdir output/stx-r1/CentOS/pike/Binary/x86_64")

    def test_download_rpm_src(self):
        rpm = 'anaconda-21.48.22.121-1.el7.centos.src.rpm'
        pkg = CentOSPackage(rpm)
        cmd = pkg.download()
        cmd_good="sudo -E yumdownloader -q -C --releasever=7 --source anaconda-21.48.22.121-1.el7.centos --destdir output/stx-r1/CentOS/pike/Source"
        self.assertEquals(cmd, cmd_good)

    def test_download_url(self):
        url = 'http://someurl.org/go-srpm-macros-2-3.el7.noarch.rpm'
        pkg = CentOSPackage(url)
        self.assertEquals('go-srpm-macros-2-3.el7.noarch.rpm', pkg.name)
        self.assertEquals(url, pkg.url)
        self.assertEquals(None, pkg.script)

    def test_download_dict(self):
        d = {
            'name': 'drbd-8.4.3.tar.gz',
            'url': 'http://www.linbit.com/downloads/drbd/8.4/archive/drbd-8.4.3.tar.gz',
            'script': 'myscript.sh'
        }
        pkg = CentOSPackage(d)
        self.assertEquals(d['name'], pkg.name)
        self.assertEquals(d['url'], pkg.url)
        self.assertEquals(d['script'], pkg.script)
