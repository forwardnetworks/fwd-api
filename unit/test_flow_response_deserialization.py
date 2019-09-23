#!/usr/bin/env python

import json
import os
import sys

from fwd_api.flow import FlowsResponse, FlowType
from fwd_api.path import AggregatedLinksPath, DeviceIfaceListPair, Hop

FLOWS_JSON = os.path.join(os.path.dirname(__file__),
                          '..', 'fwd-api-data', 'flows',
                          'example.json')

# Expected number of flows for flow response in FLOWS_JSON
EXPECTED_NUM_FLOWS = 10
# Expected flow types for flow response in FLOWS_JSON
EXPECTED_FLOW_TYPES = [FlowType.VALID,
                       FlowType.DROPPED,
                       FlowType.BLACKHOLE,
                       FlowType.BLACKHOLE,
                       FlowType.BLACKHOLE,
                       FlowType.DROPPED,
                       FlowType.VALID,
                       FlowType.VALID,
                       FlowType.VALID,
                       FlowType.VALID]

EXPECTED_LAST_FLOW_PATH = AggregatedLinksPath(
    [
        Hop(DeviceIfaceListPair('veos-0', ['et1', 'et3']),
            DeviceIfaceListPair('veos-0', ['et2'])),
        Hop(DeviceIfaceListPair('veos-1', ['et1']), None),
    ])


def test_deserialization():
    with open(FLOWS_JSON) as fd:
        json_dict = json.loads(fd.read())
    flows_response = FlowsResponse.from_json(json_dict)

    # Verify that total flows field is correct
    assert (flows_response.get_total_flows().get_total_flows() ==
            EXPECTED_NUM_FLOWS)

    # Verify that we have the expected number of individual flows
    flows_list = flows_response.get_flows_list()
    assert (len(flows_list) == EXPECTED_NUM_FLOWS)

    # Verify the flow types of those expected flows
    assert (map(lambda f: f.get_flow_type(), flows_list) ==
            EXPECTED_FLOW_TYPES)

    # Select one flow and verify its paths against a priori
    # known path of first flow. Choosing last flow because
    # it's the most complex and will execute the most logic
    assert flows_list[-1].get_unexploded_path() == EXPECTED_LAST_FLOW_PATH


if __name__ == '__main__':
    test_deserialization()
