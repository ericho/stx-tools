#
# SPDX-License-Identifier: Apache-2.0
#

from collections import MutableMapping

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
    def __init__(self, name):
        self.name = name
        self.url = None
        self.script = None

    def download():
        pass

    def _get_download_cmd():
        pass
