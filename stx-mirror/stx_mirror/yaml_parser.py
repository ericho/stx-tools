#
# SPDX-License-Identifier: Apache-2.0
#

import yaml
from package import CentOSPackageList
from package import CentOSPackage
from stx_exceptions import *
from configuration import Configuration

SUPPORTED_TYPES = {
    'centos': CentOSPackageList,
}

class YamlParser:
    """ """
    def __init__(self):
        pass

    def load(self, config):
        if not isinstance(config, Configuration):
            raise UnsupportedConfigurationType('YamlParser did not receive a valid Configuration')
        with open(config.input, 'r') as f:
            lines = f.read()
        try:
            data = yaml.load(lines)
        except yaml.YAMLError as e:
            raise

        return self._to_supported_object(data)

    def _to_supported_object(self, data):
        try:
            list_type = data['type']
        except KeyError as e:
            raise MissingPackageListType(e)

        try:
            l = SUPPORTED_TYPES[list_type](data)
        except KeyError as e:
            raise UnsupportedPackageListType(e)

        return l


