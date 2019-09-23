import fwd_filter


class SearchFields(object):
    IP_SRC = 'IP_SRC'
    IP_DST = 'IP_DST'
    IP_PROTO = 'IP_PROTO'
    L4_SRC = 'L4_SRC'
    L4_DST = 'L4_DST'


class Context(object):
    """Container for filtering either the from or to part of a query
    """

    def __init__(self):
        self._location = None
        self._fields = {}

    def set_device(self, device_name):
        """
        @param {str} device_name
        """
        self._location = fwd_filter.DeviceFilter(device_name)
        return self

    def set_iface(self, device_iface_pair):
        """
        @param {path.DeviceIfacePair} device_iface_pair
        """
        self._location = fwd_filter.IfaceFilter(device_iface_pair)
        return self

    def set_host(self, host_specifier):
        """
        Specifies a host or set of hosts by name, IP address/block,
        or MAC address.

        Note that compared to set_ip_src and set_ip_dst, this call
        implies a location: the set of edge ports that are discovered
        to have one or more matching hosts. If no hosts match the
        supplied host specifier, no paths will match the search query.

        @param {str} host_specifier
        """
        self._location = fwd_filter.HostFilter(host_specifier)
        return self

    def set_ip_src(self, ip_src):
        """
        Note that compared to set_host, this call is locationless: it
        requests Forward to inject a packet at any edge port of the
        network with the given source IP address, regardless of where
        that edge port is.

        @param {str} ip_src
        """
        self._fields[SearchFields.IP_SRC] = fwd_filter.IpSrcField(ip_src)
        return self

    def set_ip_dst(self, ip_dst):
        """
        See the note in set_ip_src about the distinction between this
        call and set_host.

        @param {str} ip_dst
        """
        self._fields[SearchFields.IP_DST] = fwd_filter.IpDstField(ip_dst)
        return self

    def set_ip_proto(self, ip_proto):
        """
        @param {int} ip_proto
        """
        self._fields[SearchFields.IP_PROTO] = fwd_filter.IpProtoField(ip_proto)
        return self

    def set_l4_src(self, l4_src):
        """
        @param {int} l4_src
        """
        self._fields[SearchFields.L4_SRC] = fwd_filter.L4SrcField(l4_src)
        return self

    def set_l4_dst(self, l4_dst):
        """
        @param {int} l4_dst
        """
        self._fields[SearchFields.L4_DST] = fwd_filter.L4DstField(l4_dst)
        return self

    def is_empty(self):
        return self._location is None and len(self._fields) == 0

    def as_dict(self):
        fields = self._fields.values()
        headers = [fwd_filter.PacketFilter(fields)] if fields else []
        return fwd_filter.EndpointFilter(self._location, headers).as_dict()


class SearchBuilder(object):
    def __init__(self):
        self._from_context = Context()
        self._to_context = Context()
        self._flow_types = None

    def get_from_context(self):
        """Return the "from" contet of a query.

        @return {Context}
        """
        return self._from_context

    def get_to_context(self):
        """Return the "to" contet of a query.

        @return {Context}
        """
        return self._to_context

    def add_flow_type(self, flow_type):
        """Restrict any query generated from this builder to flow_type
        """
        if self._flow_types is None:
            self._flow_types = []
        self._flow_types.append(flow_type)
        return self

    def build_query(self):
        """Generate a search dictionary, which the server will generate a
        response for

        @return {dict}
        """
        query_dict = {}
        if ((not self._from_context.is_empty()) or
            (not self._to_context.is_empty())):  # nopep8
            query_dict['filters'] = {}
        if not self._from_context.is_empty():
            query_dict['filters']['from'] = self._from_context.as_dict()
        if not self._to_context.is_empty():
            query_dict['filters']['to'] = self._to_context.as_dict()
        if self._flow_types is not None:
            query_dict['flowTypes'] = list(self._flow_types)
        return query_dict
