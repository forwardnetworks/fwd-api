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
    from fwd_api import search
except:
    print('Error importing search from fwd_api. Check that you ran ' +
          'setup (see README).')
    sys.exit(-1)


def get_flows(test_params):
    search_builder = search.SearchBuilder()
    search_builder.get_from_context().set_device('veos-0')

    flows_response = test_params.get_fwd()\
        .get_flows(search_builder, test_params.get_snapshot_id())

    assert flows_response.get_total_flows().get_total_flows() == 10


if __name__ == '__main__':
    get_flows(TestParams.load_from_args())
