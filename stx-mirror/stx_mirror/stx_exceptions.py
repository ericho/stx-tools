#
# SPDX-License-Identifier: Apache-2.0
#

class StxException(Exception):
    pass

class MissingPackageListType(StxException):
    pass

class UnsupportedPackageListType(StxException):
    pass

class MissingPackageType(StxException):
    pass

class UnsupportedPackageType(StxException):
    pass

class UnsupportedConfigurationType(StxException):
    pass

class UnsupportedConfigurationValue(StxException):
    pass

class MissingConfigurationValue(StxException):
    pass

class DownloadError(StxException):
    pass
