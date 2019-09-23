#!/usr/bin/env python

# Confidential Information of Forward Networks, Inc.
# Copyright (c) 2015 Forward Networks, Inc.  All rights reserved.

'''
This script uploads a zipped snapshot file. You can test it with the
snapshot located in fwd-api-data/snapshots/linear-basic.zip.
'''

import argparse
import os
import sys
try:
    from fwd_api import fwd, properties
except:
    print('Error importing fwd from fwd_api. Check that you ran ' +
          'setup (see README).')
    sys.exit(-1)


def upload_snapshot(snapshot_zip_filename, snapshot_name, network_id,
                    properties, verbose):
    '''
    @param {str} snapshot_zip_filename: The fully-qualified name of
    the zipped snapshot to upload.
    @param {str} snapshot_name: How the snapshot should be named on
    the Forward server.
    @param {int} network_id: The id of the network to upload snapshot to.
    @param {properties.Properties}: Container object holding username,
    password, and url of Forward server.
    '''
    f = fwd.Fwd(properties.url, properties.username, properties.password,
                verbose, verify_ssl_cert=False)
    f.upload_snapshot(network_id, snapshot_zip_filename, snapshot_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--zip-filename',
                        help=('The fully-qualified name of the zipped ' +
                              'snapshot to upload'),
                        required=True, type=str)
    parser.add_argument('--snapshot-name',
                        help=('How the snapshot should be named on ' +
                              'the Forward server.'),
                        required=True, type=str)
    parser.add_argument('--network-id',
                        help='The id of the network to upload snapshot to',
                        required=True, type=int)
    parser.add_argument('--properties-file',
                        help=('Properties file containing server url, ' +
                              'username, and password (See ' +
                              'fwd.properties.example). If this option is' +
                              'not set, then the script looks in ' +
                              '~/.fwd/fwd.properties.'),
                        required=False, type=str)
    parser.add_argument('--verbose', action='store_true',
                        help='Whether to print commands to stdout as run')

    parsed = parser.parse_args()
    prop_file = None
    if parsed.properties_file is not None:
        prop_file = os.path.abspath(parsed.properties_file)
    props = properties.get_properties(prop_file)

    upload_snapshot(parsed.zip_filename, parsed.snapshot_name,
                    parsed.network_id, props, parsed.verbose)
