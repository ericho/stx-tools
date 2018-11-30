#
# SPDX-License-Identifier: Apache-2.0
#

class StxException(Exception):
    pass

class MissingPackageListType(StxException):
    pass

class UnsupportedPackageListType(StxException):
    pass
