#
# SPDX-License-Identifier: Apache-2.0
#

import os
import requests

from collections import MutableMapping
from stx_exceptions import *
from helpers import Komander

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


class PackageList(MutableMapping):
    """ """
    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.store.update(*args, **kwargs)

    def __setitem__(self, key, value):
        self.store[key] = value

    def __getitem__(self, key):
        return self.store[key]

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)


class Package:
    pass


class CentOSPackageList(PackageList):
    """ """

    def __init__(self, data, config):
        self.store = dict()
        self.config = config
        for key in data:
            if key != 'type':
                self.__setitem__(key,
                                 self._to_centos_pkgs(data[key], config))

    def _to_centos_pkgs(self, list_packages, config):
        return [CentOSPackage(i, config) for i in list_packages]

    def setup(self):
        self.config.log.info("Running setup, this may take some minutes.")
        # FIXME: Apparently there's no other way to create yum cache than
        # using sudo. The command below should be fixed in some way to not
        # force the usage of sudo.
        cmds = ['which yumdownloader',
        'sudo yum -c yum.conf makecache']
        for c in cmds:
            res = Komander.run(c)
            if res.retcode != 0:
                err_msg = "\'{}\'\n{}\n{}\nretcode: {}\n".format(res.cmd,
                                                                 res.stdout,
                                                                 res.stderr,
                                                                 res.retcode)
                self.config.log.error(err_msg)
                raise SetupError(err_msg)

    def prune(self):
        self.config.log.info("Start pruning")
        dir_lst = self._generate_dir_list()
        yaml_lst = self._generate_name_list()
        to_remove = [x for x in dir_lst if x not in yaml_lst]
        for x in to_remove:
            fname = os.path.basename(x)
            self.config.log.info("Not in YAML, removing: {}".format(fname))
            os.remove(x)

    def _generate_name_list(self):
        lst = self.values()
        flat_list = [item.pkg_file for sublist in lst for item in sublist]
        return flat_list

    def _generate_dir_list(self):
        lst = []
        path = self.config.base
        for root, _ ,f_names in os.walk(path):
            if f_names:
                lst.extend([os.path.join(root, f_name) for f_name in f_names])
        return lst


class CentOSPackage(Package):
    """ """

    bootfiles = ['grub.cfg',
                 'BOOTX64.EFI',
                 'grubx64.efi',
                 'unicode.pf2',
                 'squashfs.img',
                 'initrd.img',
                 'vmlinuz',
                 'efiboot.img',
                 'memtest',
                 'grub.conf',
                 'boot.msg',
                 'isolinux.bin',
                 'splash.png',
                 'isolinux.cfg',
                 'vesamenu.c32']

    def __init__(self, info, config):
        self.name = None
        self.url = None
        self.script = None
        self.config = config
        self._basedir = os.path.join(config.base, config.release,
                                     config.distro, config.openstack)
        if isinstance(info, dict):
            if 'name' not in info and 'url' not in info:
               raise UnsupportedPackageType('Missing name and url')
            if 'url' not in info:
               raise UnsupportedPackageType('Missing url')
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
        self.pkg_file = os.path.join(self._basedir,
                                     self._get_destdir(),
                                     self.name)

    def download(self):
        if os.path.exists(self.pkg_file):
            self.config.log.info("File exists, skipping: {}".format(self.name))
            return

        self.config.log.info("Downloading {}".format(self.name))

        if self.name is not None and self.url is None \
           and self.script is None:
            cmd = self._get_yumdownloader_command()
            results = Komander.run(cmd)
            if results.retcode != 0:
                err_msg = ("\'{}\'\n{}\n{}\nretcode: {}\n".format(results.cmd,
                                                                  results.stdout,
                                                                  results.stderr,
                                                                  results.retcode))
                self.config.log.error(err_msg)
                raise DownloadError(err_msg)
        if self.name is not None and self.url is not None:
            self._download_url()

            if self.script is not None:
                self._postprocessing()
        self._check_gpg_key()

    def _get_yumdownloader_command(self):
        downloader = 'yumdownloader -q -C -c yum.conf --releasever=7'
        package_dir = '--destdir {}/{}'.format(self._basedir,
                                               self._get_destdir())

        pkg, arch = self._get_package_and_arch()
        if arch == 'src':
            arch = '--source'
        else:
            arch = '-x \*i686 --archlist=noarch,x86_64'
        return '{} {} {} {}'.format(downloader, arch, pkg, package_dir)

    def _download_url(self):
        package_dir = os.path.join(self._basedir, self._get_destdir())

        if not os.path.exists(package_dir):
            try:
                os.makedirs(package_dir)
            except OSError as e:
                # Check for file exists error to avoid race
                # condition when the first threads creates this
                # directory.
                if e[0] != 17:
                    raise e

        try:
            filedata = requests.get(self.url, allow_redirects=True)
        except requests.exceptions.RequestException as e:
            raise DownloadError("DownloadError: {}".format(e))

        with open('{}/{}'.format(package_dir, self.name), 'wb') as f:
            f.write(filedata.content)

    def _get_package_and_arch(self):
        base, ext = os.path.splitext(self.name)
        _package, _arch = os.path.splitext(base)
        _arch = _arch.replace('.','')
        return _package, _arch

    def _get_destdir(self):
        if self.name.endswith('.rpm'):
            _, arch = self._get_package_and_arch()
            return "Source" if arch == 'src' else "Binary/{}".format(arch)
        elif self.name in self.bootfiles:
            # This is the special case for the bootfiles. It needs to be
            # stored at the same folder path as there are in the server.
            # We assume that this is a x86_64 image and start to retrieve
            # the path from there.
            start_idx = self.url.find('x86_64')
            end_idx = self.url.rfind('/')
            path = self.url[self.url.find('/', start_idx) + 1:end_idx]
            return "Binary/{}".format(path)
        else:
            return 'downloads'

    def _check_gpg_key(self):
        if os.path.exists(self.pkg_file):
            cmd = "rpm -K {}".format(self.pkg_file)
            res = Komander.run(cmd)
            if res.stdout.find('MISSING') != -1:
                self.config.log.info("Missing GPG Key {}".format(self.name))

    def _postprocessing(self):
        res = Komander.run(self.script)
        if res.retcode != 0:
            err_msg = "\'{}\'\n{}\n{}\nretcode: {}\n".format(res.cmd,
                                                             res.stdout,
                                                             res.stderr,
                                                             res.retcode)
            self.config.log.error(err_msg)
            raise SetupError(err_msg)
