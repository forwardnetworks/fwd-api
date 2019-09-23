#!/usr/bin/env python

import json
import os
import sys

try:
    from fwd_api.path import AggregatedLinksPath, DeviceIfaceListPair, Hop
except:
    print('Error importing from fwd_api. Check that you ran ' +
          'setup (see README).')
    sys.exit(-1)


def gen_test_path_a():
    """
    Return the following test path:

    Packet in a on a.a1 or a.a2; packet out a.a3; pacekt in b.b1.
    """
    return AggregatedLinksPath(
        [Hop(DeviceIfaceListPair('a', ['a1', 'a2']),
             DeviceIfaceListPair('a', ['a3'])),
         Hop(DeviceIfaceListPair('b', ['b1']))])


def gen_test_path_b():
    """
    Return the following test path:

    Packet in a on b.b1 or b.b2; packet out b.b3; pacekt in c.c1.
    """
    return AggregatedLinksPath(
        [Hop(DeviceIfaceListPair('b', ['b1', 'b2']),
             DeviceIfaceListPair('b', ['b3'])),
         Hop(DeviceIfaceListPair('c', ['c1']))])


def test_identical_paths_same_hash():
    a_paths = set([])
    b_paths = set([])
    for i in range(0, 10):
        a_paths.add(gen_test_path_a())
        b_paths.add(gen_test_path_b())
    assert len(a_paths) == 1
    assert len(b_paths) == 1


def test_different_paths_hash_differently():
    assert len(set([gen_test_path_a(), gen_test_path_b()])) == 2


if __name__ == '__main__':
    test_identical_paths_same_hash()
    test_different_paths_hash_differently()
