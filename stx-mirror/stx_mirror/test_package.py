#
# SPDX-License-Identifier: Apache-2.0
#

import unittest
from package import CentOSPackage

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
