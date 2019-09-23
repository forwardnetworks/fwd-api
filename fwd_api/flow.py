from path import AggregatedLinksPath, DeviceIfaceListPair, Hop


class TotalFlows(object):
    """Container for number of flows
    """
    def __init__(self, total_flows, flows_type):
        """
        @param {int} total_flows
        @param {str} flows_type: E.g., EXACT.
        """
        self._total_flows = total_flows
        self._flows_type = flows_type

    def get_total_flows(self):
        return self._total_flows

    def get_flows_type(self):
        return self._flows_type

    @classmethod
    def from_json(cls, json_total_flows):
        return TotalFlows(json_total_flows['value'],
                          json_total_flows['type'])


class FlowsResponse(object):
    """Python-ized representation of server's json returned from call to
    'flows' endpoint.
    """
    def __init__(self, paged_flows, total_flows, flows_list):
        """
        @param {int} paged_flows
        @param {TotalFlows} total_flows
        @param {Flow[]} flows_list
        """
        self._paged_flows = paged_flows
        self._total_flows = total_flows
        self._flows_list = list(flows_list)

    @classmethod
    def from_json(cls, json_response):
        """
        @param {dict} json_response
        """
        paged_flows = json_response['pagedFlows']
        total_flows = TotalFlows.from_json(json_response['totalFlows'])
        flows_list = map(lambda f: Flow.from_json(f),
                         json_response['flows'])
        return FlowsResponse(paged_flows, total_flows,
                             flows_list)

    def get_flows_list(self):
        """
        @return {Flow[]}
        """
        return list(self._flows_list)

    def get_total_flows(self):
        """
        @return {TotalFlows}
        """
        return self._total_flows


class FlowType(object):
    VALID = 'VALID'
    BLACKHOLE = 'BLACKHOLE'
    DROPPED = 'DROPPED'
    UNREACHABLE = 'UNREACHABLE'
    INADMISSIBLE = 'INADMISSIBLE'
    LOOP = 'LOOP'

    VALUES = [VALID, BLACKHOLE, DROPPED, UNREACHABLE, INADMISSIBLE, LOOP]


class Flow(object):
    """Wrapper object for a flow returned by the server

    Note that this object represents only a subset of the flow
    information that the server returns.
    """
    INPUT_TABLE_SUFFIX = '.input'
    OUTPUT_TABLE_SUFFIX = '.output'

    def __init__(self, flow_type, unexploded_path):
        """
        @param {str} flow_type One of the members of FlowType
        @param {AggregatedLinksPath} unexploded_path
        """
        self._flow_type = flow_type
        self._unexploded_path = unexploded_path

    def get_flow_type(self):
        return self._flow_type

    def get_unexploded_path(self):
        """
        @returns {UnexploededPath}
        """
        return self._unexploded_path

    @staticmethod
    def _has_suffix(val, suffix):
        return val[-len(suffix):] == suffix

    @staticmethod
    def _is_input_table(table_name):
        return Flow._has_suffix(table_name,
                                Flow.INPUT_TABLE_SUFFIX)

    @staticmethod
    def _is_output_table(table_name):
        return Flow._has_suffix(table_name,
                                Flow.OUTPUT_TABLE_SUFFIX)

    @staticmethod
    def _is_external_table(table_name):
        return (Flow._is_input_table(table_name) or
                Flow._is_output_table(table_name))

    @classmethod
    def from_json(cls, flow_json):
        """
        @param {dict} flow_json
        """
        first_and_last_hops = []
        last_dev_name = None
        # Note that the following logic breaks if a device has a wire
        # connecting it to itself.
        hops_list = flow_json['hops']
        for i in range(0, len(hops_list)):
            hop = hops_list[i]
            if Flow._is_input_table(hop['table']):
                if i > 0:
                    first_and_last_hops.append(hops_list[i-1])
                first_and_last_hops.append(hop)
        final_hop = hops_list[-1]
        if Flow._is_output_table(final_hop['table']):
            if 'none' not in final_hop['out_ports']:
                first_and_last_hops.append(final_hop)

        unexploded_hop_list = []
        prev_pair = None
        for hop in first_and_last_hops:
            device_name = hop['parent']
            if Flow._is_input_table(hop['table']):
                device_port_names = hop['in_ports']
            elif Flow._is_output_table(hop['table']):
                device_port_names = hop['out_ports']
            else:
                assert False, 'Unexpected table hop named ' + hop['table']

            # device_port_names is a list containing strings. Each string
            # is a device name + iface name, separated by a space. The
            # following line of code just grabs the interface name.
            port_names = map(lambda dp: dp.split()[1],
                             device_port_names)

            pair = DeviceIfaceListPair(device_name, port_names)

            if prev_pair is None:
                prev_pair = pair
            else:
                unexploded_hop_list.append(Hop(prev_pair, pair))
                prev_pair = None

        # Test for a packet that just ingresses a final device
        if prev_pair is not None:
            unexploded_hop_list.append(Hop(prev_pair))

        return Flow(flow_json['flowType'],
                    AggregatedLinksPath(unexploded_hop_list))
