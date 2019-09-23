# Confidential Information of Forward Networks, Inc.
# Copyright (c) 2015 Forward Networks, Inc.  All rights reserved.

'''
Utility library for trying to read in fwd.properties file to specify
parameters for connecting to server.
'''

import os
import sys
try:
    # Starting in Python 3, ConfigParser was renamed to
    # "configparser." Try importing both the Python 3 version and
    # Python 2 version.
    import ConfigParser as configparser
except:
    import configparser


class Properties(object):
    '''Wrapper for information required to connect to Forward server
    '''

    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password


class _FakeConfigFd(object):
    '''
    fwd.properties is not formatted in a way that a standard python
    library can read in its values. The closest reader seems to be
    ConfigParser. However, ConfigParser requires a section header that
    is not present in the fwd.properties file. This class wraps a file
    descriptor, automatically inserting this section header.
    '''

    DUMMY_SECTION_HEADER = 'dummy'

    def __init__(self, fd):
        self.fd = fd
        self.on_first_line = True

    def readline(self):
        if self.on_first_line:
            self.on_first_line = False
            return '[' + self.DUMMY_SECTION_HEADER + ']\n'
        return self.fd.readline()


def get_properties(filename=None):
    '''Generate Properties object

    @param {str} filename: If None, then try to generate Properties
    object from system-wide properties file in
    ~/.fwd/fwd.properties. Otherwise, generate Properties from
    filename.

    @return {Properties}
    '''

    if filename is not None:
        cfg = configparser.ConfigParser()
        with open(filename, 'r') as fd:
            cfg.readfp(_FakeConfigFd(fd))

        url = cfg.get(_FakeConfigFd.DUMMY_SECTION_HEADER, 'url')
        username = cfg.get(_FakeConfigFd.DUMMY_SECTION_HEADER, 'username')
        password = cfg.get(_FakeConfigFd.DUMMY_SECTION_HEADER, 'password')
        return Properties(url, username, password)

    system_wide_properties = os.path.join(os.path.expanduser('~'),
                                          '.fwd', 'fwd.properties')
    if not os.path.exists(system_wide_properties):
        print('\nError reading properties. Please specify properties ' +
              'or set the variables "url," "username," and "password" ' +
              'in ' + system_wide_properties + '\n')
        sys.exit(-1)

    return get_properties(system_wide_properties)
