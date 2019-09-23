#!/usr/bin/env python

# Confidential Information of Forward Networks, Inc.
# Copyright (c) 2015 Forward Networks, Inc.  All rights reserved.

'''
This script exercises the alias upload python libraries. Because
upload success or failure is tied to the actual snapshot, this test is
intended to be run against the snapshot located in
fwd-api-data/snapshots/large.zip. Please upload that snapshot
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

VLAN_DEV_AND_PORT_ALIAS_NAME = 'dev_port_vlan_alias'
VLAN_ONLY_ALIAS_NAME = 'vlan_only_alias'


def add_aliases(test_params):
    '''Add all aliases for the large topology

    @param {TestParams} test_params
    '''
    # Upload interface alias that includes device name, port name,
    # and vlan
    vlan_dev_and_port = alias.VlanInterfaceAlias(
        VLAN_DEV_AND_PORT_ALIAS_NAME, dev='tor-1-2', port='*',
        vlans=['22'])

    test_params.get_fwd()\
               .upload_alias(vlan_dev_and_port,
                             test_params.get_snapshot_id())

    # Upload interface alias that includes only vlans
    vlan_only = alias.VlanInterfaceAlias(
        VLAN_ONLY_ALIAS_NAME, vlans=['22'])

    test_params.get_fwd()\
               .upload_alias(vlan_only, test_params.get_snapshot_id())


if __name__ == '__main__':
    add_aliases(TestParams.load_from_args())
