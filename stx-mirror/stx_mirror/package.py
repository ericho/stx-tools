#
# SPDX-License-Identifier: Apache-2.0
#

from collections import MutableMapping
from stx_exceptions import *
import os
import urllib2

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
    def __init__(self, data, config):
        self.data = data
        self.config = config
        for key in self.data:
            if key != 'type':
                self.__setitem__(key,
                                 self._to_centos_pkgs(self.data[key], config))

    def _to_centos_pkgs(self, list_packages, config):
        return [CentOSPackage(i, config) for i in list_packages]


class CentOSPackage:
    """ """
    def __init__(self, info, config):
        self.name = None
        self.url = None
        self.script = None
        self._basedir = os.path.join(config.base, config.release,
                                     config.distro, config.openstack)
        if isinstance(info, dict):
            if 'name' not in info and 'url' not in info:
               raise UnsupportedPackageType('Package is missing name and url')
            if 'url' not in info:
               raise UnsupportedPackageType('Package is missing url')
            self.name = info['name']
            self.url = info['url']
            if 'script' in info:
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
               raise UnsupportedPackageType('Package format error {}'.format(
                                             info))
        else:
           raise UnsupportedPackageType('Package format error {}'.format(
                                         info))

    def download(self):
       if self.name is not None and self.url is None and self.script is None:
            cmd = self._get_yumdownloader_command()
            return cmd
            # Execute cmd
       elif self.name is not None and self.url is not None and self.script is None:
            self._download_url()
       elif self.name is not None and self.url is not None and self.script is not None:
            self._download_url()
            self._postprocessing()

    def _get_yumdownloader_command(self):
        downloader = 'sudo -E yumdownloader -q -C --releasever=7'
        pkg, arch = self._get_package_and_arch()
        if arch == 'src':
            package_dir = '--destdir {}/Source'.format(self._basedir)
            arch = '--source'
        else:
            package_dir = '--destdir {}/Binary/{}'.format(self._basedir, arch)
            arch = '-x \*i686 --archlist=noarch,x86_64'
        cmd = '{} {} {} {}'.format(downloader, arch, pkg, package_dir)
        return cmd

    def _download_url(self):
        filedata = urllib2.urlopen(self.url)
        datatowrite = filedata.read()
        with open(self.name, 'wb') as f:
            f.write(datatowrite)

    def _get_package_and_arch(self):
        base, ext = os.path.splitext(self.name)
        _package, _arch = os.path.splitext(base)
        _arch = _arch.replace('.','')
        return _package, _arch

    def _postprocessing(self):
        pass
