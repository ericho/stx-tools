#!/usr/bin/python
#
# SPDX-License-Identifier: Apache-2.0
#

import argparse
import os
import sys

import yaml

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


parser = argparse.ArgumentParser()
parser._action_groups.pop()
req_args = parser.add_argument_group('required arguments')
req_args.add_argument('-d', '--directory', nargs='?',
                      help='Directory to look for .lst files',
                      required=True)

CENTOS_URL = 'http://vault.centos.org/7.4.1708/os/x86_64'

rpms = []
_3rdparty = []
tarballs = []
other_dl = []

def is_url(line):
    url = urlparse(line)
    if url.scheme == '' and url.netloc == '':
        return False
    return True


def process_lst_file(lst_file):
    with open(lst_file, 'r') as f:
        for _, line in enumerate(f):
            line = line.rstrip()
            if line.count('#') == 1 and line[0] != '#':
                url = line.split('#')[1]
                _3rdparty.append(url)
            elif line.count('#') > 1 and line[0] != '#':
                fields = line.split('#')
                name = fields[0]
                script = fields[1]
                url = fields[2]
                if name.startswith('!'):
                    name = name[1:]
                d = {'name': name,
                     'script': script,
                     'url': url}
                tarballs.append(d)
            elif 'file:' in line:
                file_dl = line.split(':')[1]
                other_dl.append("{}/{}".format(CENTOS_URL, file_dl))
            elif line.endswith('.rpm') and not is_url(line):
                rpms.append(line)

def main():
    args = parser.parse_args()
    if not args.directory:
        print "ERROR: A directory should be provided."
        return 1

    for f in os.listdir(args.directory):
        if f.endswith('.lst'):
            process_lst_file('{}/{}'.format(args.directory, f))

    parsed_items = {'type': 'centos',
                    'rpms': rpms,
                    '3rdparty': _3rdparty,
                    'tarballs': tarballs,
                    'bootfiles': other_dl}


    print yaml.dump(parsed_items)

    return 0

if __name__ == '__main__':
    sys.exit(main())
