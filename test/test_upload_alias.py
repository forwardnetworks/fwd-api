#!/usr/bin/env python

# Confidential Information of Forward Networks, Inc.
# Copyright (c) 2015 Forward Networks, Inc.  All rights reserved.

'''
This script exercises the alias upload python libraries. Because
upload success or failure is tied to the actual snapshot, this test is
intended to be run against the snapshot located in
fwd-api-data/snapshots/linear-basic.zip. Please upload that snapshot
before running this test.
'''

from test_params import TestParams
import sys
try:
    from fwd_api import alias
except:
    print('Error importing alias from fwd_api. Check that you ran ' +
          'setup (see README).')
    sys.exit(-1)

LEFT_HOST_ALIAS_NAME = 'left_host'
RIGHT_HOST_ALIAS_NAME = 'right_host'
LEFT_EDGE_PORT_ALIAS_NAME = 'edge_left'
RIGHT_EDGE_PORT_ALIAS_NAME = 'edge_right'
LEFT_SUBNET_ALIAS_NAME = 'left_subnet'
RIGHT_SUBNET_ALIAS_NAME = 'right_subnet'


def add_aliases(test_params):
    '''Add all aliases for the linear topology

    @param {TestParams} test_params
    '''
    left_host_alias = alias.HostAlias(LEFT_HOST_ALIAS_NAME, ['left'])
    right_host_alias = alias.HostAlias(RIGHT_HOST_ALIAS_NAME, ['right'])
    edge_port_left = alias.InterfaceAlias(LEFT_EDGE_PORT_ALIAS_NAME,
                                          'veos-0', 'et3')
    edge_port_right = alias.InterfaceAlias(RIGHT_EDGE_PORT_ALIAS_NAME,
                                           'veos-1', 'et3')
    left_subnet = alias.IpV4TrafficAlias(LEFT_SUBNET_ALIAS_NAME,
                                         ['18.0.0.2/31'])
    right_subnet = alias.IpV4TrafficAlias(RIGHT_SUBNET_ALIAS_NAME,
                                          ['18.0.0.4/31'])

    all_aliases = [left_host_alias, right_host_alias, edge_port_left,
                   edge_port_right, left_subnet, right_subnet]

    for al in all_aliases:
        test_params.get_fwd().upload_alias(al, test_params.get_snapshot_id())


if __name__ == '__main__':
    add_aliases(TestParams.load_from_args())
