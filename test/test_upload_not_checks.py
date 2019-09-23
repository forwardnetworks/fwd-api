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
    from fwd_api.check import ExistenceCheck
    from fwd_api.fwd_filter import NotFilter, HostFilter

except:
    print('Error importing check from fwd_api. Check that you ran ' +
          'setup (see README).')
    sys.exit(-1)


def add_checks(test_params):
    '''Add not from and not to checks to linear topology

    @param {TestParams} test_params
    '''

    left = HostFilter('left')
    right = HostFilter('right')

    # Check that traffic should arrive at left from places other than
    # right
    test_params.get_fwd()\
               .upload_check(ExistenceCheck(left, NotFilter(right)),
                             test_params.get_snapshot_id())

    # Check that traffic should arrive at devices other than left
    # from right.
    test_params.get_fwd()\
               .upload_check(ExistenceCheck(NotFilter(left), right),
                             test_params.get_snapshot_id())


if __name__ == '__main__':
    add_checks(TestParams.load_from_args())
