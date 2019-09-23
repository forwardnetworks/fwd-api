#!/usr/bin/env python

# Confidential Information of Forward Networks, Inc.
# Copyright (c) 2015 Forward Networks, Inc.  All rights reserved.

'''
Set the collector on a network, upload topo list and data sources
files, and collect a snapshot.
'''

import argparse
import getpass
import os
import sys
import time
try:
    from fwd_api import fwd, properties
except:
    print('Error importing fwd from fwd_api. Check that you ran ' +
          'setup (see README).')
    sys.exit(-1)


def set_collector_take_snapshot(server_url, network_id,
                                data_sources_filename, topo_list_filename,
                                username, password, collector_name, verbose):
    f = fwd.Fwd(server_url, username, password, verbose, verify_ssl_cert=False)
    f.set_network_collector(network_id, collector_name)
    f.upload_topo_list(network_id, topo_list_filename, verbose=True)
    f.upload_data_sources(network_id, data_sources_filename, verbose=True)
    f.blocking_collection_request(network_id)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--network-id',
                        help='The id of the snapshot to apply the checks to',
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
    parser.add_argument('--data-sources-filename',
                        help='Data sources filename', required=True, type=str)
    parser.add_argument('--collector-name',
                        help='Collector user name (contact Forward support ' +
                             'if not known)',
                        required=True, type=str)
    parser.add_argument('--topo-list-filename', help='Topo list filename',
                        required=True, type=str)

    parsed = parser.parse_args()
    prop_file = None
    if parsed.properties_file is not None:
        prop_file = os.path.abspath(parsed.properties_file)
    props = properties.get_properties(prop_file)
    set_collector_take_snapshot(props.url, parsed.network_id,
                                parsed.data_sources_filename,
                                parsed.topo_list_filename, props.username,
                                props.password, parsed.collector_name,
                                parsed.verbose)
