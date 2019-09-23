import abc


class Filter(object):
    """Parent class for objects that restrict results returned by server
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def as_dict(self):
        """Return json-izable dictionary of a filter
        """


class _PacketField(object):
    """Parent class for all packet headers
    """
    def __init__(self, field_name, val):
        """
        @param {str} field_name
        @param {int or str} val
        """
        self._field_name = field_name
        self._val = val

    def add_clauses_to_packet_filter_dict(self, d):
        """Add any clauses for this field to the passed-in dictionary
        @param {dict} d
        """
        d[self._field_name] = [self._val]
        return d


class IpSrcField(_PacketField):
    def __init__(self, val):
        """
        @param {str} val
        """
        super(IpSrcField, self).__init__(
            'ipv6_src' if ':' in val else 'ipv4_src', val)


class IpDstField(_PacketField):
    def __init__(self, val):
        """
        @param {str} val
        """
        super(IpDstField, self).__init__(
            'ipv6_dst' if ':' in val else 'ipv4_dst', val)


class IpProtoField(_PacketField):
    def __init__(self, val):
        """
        @param {int} val
        """
        super(IpProtoField, self).__init__('ip_proto', val)


class L4SrcField(_PacketField):
    def __init__(self, val):
        """
        @param {int} val
        """
        super(L4SrcField, self).__init__('tp_src', val)


class L4DstField(_PacketField):
    def __init__(self, val):
        """
        @param {int} val
        """
        super(L4DstField, self).__init__('tp_dst', val)


class IcmpTypeField(_PacketField):
    def __init__(self, val):
        """
        @param {int} val
        """
        super(IcmpTypeField, self).__init__('icmp_type', val)


class _HeaderFilter(Filter):
    """Parent class for packet header value filters
    """
    pass


class PacketFilter(_HeaderFilter):
    """Filter for scoping searches to packets with particular headers
    """

    def __init__(self, packet_field_list):
        """
        @param {_PacketField[]} packet_field_list
        """
        self._packet_field_list = list(packet_field_list)

    def as_dict(self):
        """
        Example return:

        {
          "type": "PacketFilter",
          "values": {
            "tp_dst": ["80"],
            "ipv4_dst": ["10.100.0.2"]
          }
        }
        """
        return {
            'type': 'PacketFilter',
            'values': reduce(
                lambda d, f: f.add_clauses_to_packet_filter_dict(d),
                self._packet_field_list,
                {}),
        }


class Direction(object):
    """Indicates which directional headers a PacketAliasFilter constrains
    For example, whether an ip filter means ip source or ip destination.
    """
    SRC = 'SRC'
    DST = 'DST'

    @staticmethod
    def check_valid_direction(dir_str):
        if dir_str != Direction.SRC and dir_str != Direction.DST:
            raise ValueError('direction must be one of %s or %s' % (Direction.SRC, Direction.DST))


class PacketAliasFilter(_HeaderFilter):
    """Filter that references a packet headers alias by name
    """

    def __init__(self, alias_name, direction=None):
        """
        @param {str} alias_name
        @param direction one of Direction.SRC or Direction.DST, if not None
        """
        self._alias_name = alias_name
        if direction is not None:
            Direction.check_valid_direction(direction)
        self._direction = direction

    def as_dict(self):
        d = {
            'type': 'PacketAliasFilter',
            'value': self._alias_name,
        }
        if self._direction is not None:
            d['direction'] = self._direction
        return d


class LocationFilter(Filter):
    """Parent class for all filters that are applied at a particular
    place in the network
    """
    pass


class HostFilter(LocationFilter):
    """Filter referencing a specific host or set of hosts by name,
    IP address/block, or MAC address
    """

    def __init__(self, host_specifier):
        """
        @param {str} host_specifier
        """
        self._host_specifier = host_specifier

    def as_dict(self):
        return {
            'type': 'HostFilter',
            'values': [self._host_specifier],
        }


class DeviceFilter(LocationFilter):
    """Location filter restricting search to a specific device
    """
    def __init__(self, device_name):
        """
        @param {str} device_name
        """
        self._device_name = device_name

    def as_dict(self):
        return {
            'type': 'DeviceFilter',
            'values': [self._device_name],
        }


class IfaceFilter(LocationFilter):
    """Location filter restricting search to a device interface
    """
    def __init__(self, device_iface_pair):
        """
        @param {DeviceIfacePair} device_iface_pair
        """
        self._device_iface_pair = device_iface_pair

    def as_dict(self):
        return {
            'type': 'InterfaceFilter',
            'values': [self._device_iface_pair.as_fwd_repr()],
        }


class HostAliasFilter(LocationFilter):
    """Location filter that references a host alias by name
    """

    def __init__(self, alias_name):
        """
        @param {str} alias_name
        """
        self._alias_name = alias_name

    def as_dict(self):
        return {
            'type': 'HostAliasFilter',
            'value': self._alias_name,
        }


class DeviceAliasFilter(LocationFilter):
    """Location filter that references an interface alias by name
    """

    def __init__(self, alias_name):
        """
        @param {str} alias_name
        """
        self._alias_name = alias_name

    def as_dict(self):
        return {
            'type': 'DeviceAliasFilter',
            'value': self._alias_name,
        }


class InterfaceAliasFilter(LocationFilter):
    """Location filter that references an interface alias by name
    """

    def __init__(self, alias_name):
        """
        @param {str} alias_name
        """
        self._alias_name = alias_name

    def as_dict(self):
        return {
            'type': 'InterfaceAliasFilter',
            'value': self._alias_name,
        }


class NotFilter(Filter):
    """A filter that wraps and negates a location or headers filter
    """

    def __init__(self, clause):
        self._clause = clause

    def as_dict(self):
        return {
            'type': 'NotFilter',
            'clause': self._clause.as_dict(),
        }


class EndpointFilter(Filter):
    """Used in "from" or "to" field of a search or check
    """
    def __init__(self, location, headers):
        """
        @param {LocationFilter} location: Can be None
        @param {_HeaderFilter[]} headers: Can be None

        Note one of location or headers must be specified.
        """
        self._location = location
        self._headers = list(headers) if headers else None
        if self._location is None and self._headers is None:
            raise ValueError('Cannot create EndpointFilter with empty ' +
                             'location and headers')

    def as_dict(self):
        result = {
            'type': 'EndpointFilter'
        }
        if self._location:
            result['location'] = self._location.as_dict()
        if self._headers:
            result['headers'] = map(lambda h: h.as_dict(), self._headers)
        return result
