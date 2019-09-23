#!/usr/bin/env python

import json
import os
import sys

from fwd_api.ifaces_response import IfacesResponse
try:
    from fwd_api.ifaces_response import IfacesResponse
except:
    print('Error importing from fwd_api. Check that you ran ' +
          'setup (see README).')
    sys.exit(-1)

IFACES_JSON = os.path.join(os.path.dirname(__file__),
                           '..', 'fwd-api-data', 'ifaces',
                           'example.json')

# We know a priori that the ifaces contained in IFACES_JSON
# should have the following names
EXPECTED_IFACE_NAMES = ['et1', 'et2', 'ma1', 'et3', 'et4',
                        'et5', 'po20']


def test_deserialization():
    with open(IFACES_JSON) as fd:
        json_dict = json.loads(fd.read())
    ifaces_response = IfacesResponse.from_json(json_dict)
    iface_response_list = ifaces_response.get_iface_response_list()

    # Check that all expected interfaces exist
    assert len(iface_response_list) == len(EXPECTED_IFACE_NAMES)
    for expected_iface_name in EXPECTED_IFACE_NAMES:
        found = False
        for iface_response in iface_response_list:
            if iface_response.matches_name(expected_iface_name):
                found = True
                break
        assert found


if __name__ == '__main__':
    test_deserialization()



