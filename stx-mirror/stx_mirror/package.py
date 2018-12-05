#
# SPDX-License-Identifier: Apache-2.0
#

from collections import MutableMapping
from exceptions import *
from rpmUtils.miscutils import splitFilename

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

class PackageList(MutableMapping):
    """ """
    def __init__(self, *args, **kwargs):
        self.__dict__.update(*args, **kwargs)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def __delitem__(self, key):
        del self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)


class CentOSPackageList(PackageList):
    """ """
    def __init__(self, data):
        self.data = data
        for key in self.data:
            if key != 'type':
                self.__setitem__(key,
                                 self._to_centos_pkgs(self.data[key]))

    def _to_centos_pkgs(self, list_packages):
        return [CentOSPackage(i) for i in list_packages]


class CentOSPackage:
    """ """
    # TODO: Implement all this..
    def __init__(self, info):
        self.name = None
        self.url = None
        self.script = None
        self._basedir='output/stx-r1/CentOS/pike'
        if isinstance(info, dict):
            if 'name' not in info and 'url' not in info:
               raise UnsupportedPackageType
            if 'url' not in info:
               raise UnsupportedPackageType
            self.name = info['name']
            self.url = info['url']
            self.script = info['script']
        elif isinstance(info, str):
            url = urlparse(info)
            if url.scheme != '' and url.netloc != '':
                self.name = info.split('/')[-1]
                self.url = info
                self.script = None
            elif info.split('/')[-1].endswith(".rpm"):
                self.name = info
                self.url = None
                self.script = None
            else:
               raise UnsupportedPackageType
        else:
           raise UnsupportedPackageType

    def _get_arch(self, pkg):
        (_n, _v, _r, _e, _a) = splitFilename(pkg)
        return _a

    def _convert_package(self, pkg):
        (_n, _v, _r, _e, _a) = splitFilename(pkg)
        return '{}-{}-{}'.format(_n, _v, _r)

    def download(self):
       cmd = ''
       if self.name is not None and self.url is None and self.script is None:
            downloader = 'sudo -E yumdownloader -q -C --releasever=7'
            arch = self._get_arch(self.name)
            pkg = self._convert_package(self.name)
            if arch == 'src':
                package_dir = '--destdir {}/Source'.format(self._basedir)
                arch = '--source'
            else:
                package_dir = '--destdir {}/Binary/{}'.format(self._basedir, arch)
                arch = '-x \*i686 --archlist=noarch,x86_64'
            cmd = '{} {} {} {}'.format(downloader, arch, pkg, package_dir)
       elif self.name is not None and self.url is not None and self.script is None:
            #import urllib2
            #response = urllib2.urlopen(self.url)
            #html = response.read()
            pass
       elif self.name is not None and self.url is not None and self.script is not None:
            pass
       return cmd


    def _get_download_cmd():
        pass


