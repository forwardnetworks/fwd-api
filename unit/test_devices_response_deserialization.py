#!/usr/bin/env python

import json
import os
import sys

try:
    from fwd_api.devices_response import DevicesResponse, DeviceResponse
except:
    print('Error importing from fwd_api. Check that you ran ' +
          'setup (see README).')
    sys.exit(-1)

DEVICES_JSON = os.path.join(os.path.dirname(__file__),
                            '..', 'fwd-api-data', 'devices',
                            'example.json')

# We know a priori that the json in DEVICES_JSON should deserialize
# into the following device responses.
EXPECTED_DEVICES = [
    DeviceResponse('veos-0', 1),
    DeviceResponse('veos-1', 2),
    ]


def test_deserialization():
    with open(DEVICES_JSON) as fd:
        json_list = json.loads(fd.read())
    devices_response = DevicesResponse.from_json(json_list)
    device_response_list = devices_response.get_device_response_list()

    # Ensure that parsed responses equal expected responses
    assert device_response_list == EXPECTED_DEVICES


if __name__ == '__main__':
    test_deserialization()

