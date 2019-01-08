#
# SPDX-License-Identifier: Apache-2.0
#

from multiprocessing.pool import ThreadPool

from stx_exceptions import DownloadError, UnsupportedDownloadPackageType
from package import Package

MAXTHREADS = 4
TASK_TIMEOUT=300

class PackageResult:
    """ To contain the result of the execution of the task/process """
    def __init__(self):
        self.success = False
        self.e = None
        self.pkg = None


def download(pkg):
    if not isinstance(pkg, Package):
        raise UnsupportedDownloadPackageType

    result = PackageResult()
    try:
        pkg.download()
        result.success = True
    except DownloadError as e:
        result.success = False
        result.pkg = pkg
        result.e = e
    return result


def download_all(packages):
    pool = ThreadPool(MAXTHREADS)
    _res = []
    for list_packages in packages:
        for p in packages[list_packages]:
            _res.append(pool.apply_async(download, (p, )))
    return [r.get() for r in _res]
