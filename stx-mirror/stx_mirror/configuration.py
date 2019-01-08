import ConfigParser
import logging

from stx_exceptions import *

class Configuration:
    """ """
    def __init__(self):
        self.base = "./output"
        self.release = ""
        self.distro = ""
        self.openstack = ""
        self.booturl = "http://vault.centos.org/7.4.1708/os/x86_64/"
        self.maxthreads = 4
        self.logfile = "stx-mirror.log"
        self.input = "manifests/manifest.yaml"
        self.log = None

    def load(self, conf):
        _conf = ConfigParser.ConfigParser()
        try:
            _conf.read(conf)
        except ConfigParser.MissingSectionHeaderError as e:
            raise UnsupportedConfigurationType(e)

        sections = _conf.sections()
        if not sections:
            raise UnsupportedConfigurationType("Zero sections")
        if len(sections) > 1:
            raise UnsupportedConfigurationType("Too many sections")
        section = sections[0]

        options = _conf.options(section)
        if not options:
            raise UnsupportedConfigurationType("Zero options")

        if _conf.has_option(section, 'base'):
            self.base = _conf.get(section, 'base')

        if _conf.has_option(section, 'release'):
            self.release = _conf.get(section, 'release')
        else:
            raise MissingConfigurationValue('release is required')

        if _conf.has_option(section, 'distro'):
            self.distro = _conf.get(section, 'distro')
        else:
            raise MissingConfigurationValue('distro is required')

        if _conf.has_option(section, 'openstack'):
            self.openstack = _conf.get(section, 'openstack')
        else:
            raise MissingConfigurationValue('openstack version is required')

        if _conf.has_option(section, 'booturl'):
           self.booturl = _conf.get(section, 'booturl')

        if _conf.has_option(section, 'maxthreads'):
            try:
                self.maxthreads = int(_conf.get(section, 'maxthreads'))
            except ValueError as e:
                raise UnsupportedConfigurationValue(e)

        if _conf.has_option(section, 'log'):
            self.logfile = _conf.get(section, 'log')

        if _conf.has_option(section, 'input'):
            self.input = _conf.get(section, 'input')

        self.set_logger()

    def is_complete(self):
        if not self.base or not self.release or not self.distro \
            or not self.openstack or not self.booturl or not self.logfile:
            return False
        else:
            return True

    def set_logger(self):
        format = "%(asctime)s %(levelname)s - %(message)s"
        logging.basicConfig(level=logging.INFO,
                            filename=self.logfile,
                            filemode='w',
                            format=format)
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter(format))
        logging.getLogger().addHandler(console)
        self.log = logging.getLogger()
