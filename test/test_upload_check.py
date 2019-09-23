#!/usr/bin/env python

# Confidential Information of Forward Networks, Inc.
# Copyright (c) 2015 Forward Networks, Inc.  All rights reserved.

'''
This script exercises the check upload python libraries. Because
upload success or failure is tied to the actual snapshot, this test is
intended to be run against the snapshot located in
fwd-api-data/snapshots/linear-basic.zip. Please upload that snapshot
before running this test.
'''

from test_params import TestParams
import sys
try:
    from fwd_api import check
    from fwd_api.fwd_filter import (HostAliasFilter, InterfaceAliasFilter,
                                    PacketAliasFilter, EndpointFilter, Direction,
                                    NotFilter, PacketFilter, IcmpTypeField)
except:
    print('Error importing check from fwd_api. Check that you ran ' +
          'setup (see README).')
    sys.exit(-1)

from test_upload_alias import (LEFT_HOST_ALIAS_NAME, RIGHT_HOST_ALIAS_NAME,
                               LEFT_EDGE_PORT_ALIAS_NAME,
                               RIGHT_EDGE_PORT_ALIAS_NAME,
                               LEFT_SUBNET_ALIAS_NAME, RIGHT_SUBNET_ALIAS_NAME)


EXCLUDE_ICMP_TYPE = "135"


def gen_bi_exist_checks(from_to_a, from_to_b):
    '''Generate checks that a can send packets to b and b can send packets to a
    '''
    return [check.ExistenceCheck(from_to_a, from_to_b),
            check.ExistenceCheck(from_to_b, from_to_a, "Exist Reverse")]


def gen_bi_reach_checks(from_to_a, from_to_b):
    '''Generate checks that all IPs in a can send packets to all IPs in b and
    vice versa
    '''
    return [check.ReachabilityCheck(from_to_a, from_to_b),
            check.ReachabilityCheck(from_to_b, from_to_a, "Reach Reverse")]


def gen_bi_iso_checks(from_to_a, from_to_b):
    '''Generate checks that a cannot send packets to b and b cannot send
    packets to a
    '''
    return [check.IsolationCheck(from_to_a, from_to_b),
            check.IsolationCheck(from_to_b, from_to_a, "Iso Reverse")]


def add_checks(test_params):
    '''Add all checks for triangle topology

    @param {TestParams} test_params
    '''
    # Checks that traffic from left host can reach right host and vice
    # versa; both checks should pass
    left_host = EndpointFilter(HostAliasFilter(LEFT_HOST_ALIAS_NAME), [])
    right_host = EndpointFilter(HostAliasFilter(RIGHT_HOST_ALIAS_NAME), [])
    all_checks = gen_bi_exist_checks(left_host, right_host)

    # Alternate way to specify above checks: ingress traffic on left
    # router with left subnet should be able to exit right router
    # with right subnet addresses; both checks should pass
    left_and_sub = EndpointFilter(
        InterfaceAliasFilter(LEFT_EDGE_PORT_ALIAS_NAME),
        [PacketAliasFilter(LEFT_SUBNET_ALIAS_NAME),
         PacketAliasFilter(RIGHT_SUBNET_ALIAS_NAME, Direction.DST),
         NotFilter(PacketFilter([IcmpTypeField(EXCLUDE_ICMP_TYPE)]))])
    right_loc = InterfaceAliasFilter(RIGHT_EDGE_PORT_ALIAS_NAME)
    # Test when destination location filter is specified
    all_checks.append(
        check.ReachabilityCheck(left_and_sub, dst_location_filter=right_loc,
                                name='Reachability with dst location'))
    # Test when destination location filter is unspecified
    all_checks.append(
        check.ReachabilityCheck(left_and_sub,
                                name='Reachability no dst location'))

    # Checks that traffic on should not flow between both hosts: both
    # checks should fail
    all_checks += gen_bi_iso_checks(left_host, right_host)

    for c in all_checks:
        test_params.get_fwd().upload_check(c, test_params.get_snapshot_id())


if __name__ == '__main__':
    add_checks(TestParams.load_from_args())
