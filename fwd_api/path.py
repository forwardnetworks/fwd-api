class DeviceIfacePair(object):
    def __init__(self, device_name, iface_name):
        self._device_name = device_name
        self._iface_name = iface_name

    def as_fwd_repr(self):
        """
        The Forward server represents devivce+iface name pairs as
        single strings with a whitespace separator between them. This
        method converts the Python code's more structured
        representation to the single-string representation that the
        Forward server uses.

        @returns {str}
        """
        return self._device_name + ' ' + self._iface_name


class DeviceIfaceListPair(object):
    """Container object for a device name, iface name list
    """
    def __init__(self, device_name, iface_names_list):
        """
        @param {str} device_name
        @param {str[]} iface_names_list
        """
        self._device_name = device_name
        self._iface_names_list = list(iface_names_list)

    def as_dict(self):
        return {
            'device_name': self._device_name,
            'iface_names': list(self._iface_names_list),
            }

    def get_device_name(self):
        return self._device_name

    def get_iface_names_list(self):
        return list(self._iface_names_list)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash((self._device_name, tuple(self._iface_names_list)))


class Hop(object):
    """A device hop in a path
    """
    def __init__(self, ingress, egress=None):
        """
        @param {DeviceIfaceListPair} ingress
        @param {DeviceIfaceListPair} egress (note: can be None, e.g.,
        for DROPPED flows or receive flows)
        """
        self._ingress = ingress
        self._egress = egress

    def get_ingress(self):
        return self._ingress

    def get_egress(self):
        return self._egress

    def as_dict(self):
        return {
            'ingress': self._ingress.as_dict(),
            'egress': None if self._egress is None else self._egress.as_dict(),
            }

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash((self._ingress, self._egress))


class AggregatedLinksPath(object):
    """Wraps a series of device hops a flow traverses

    Note that we call this an "aggregated" path because it could
    actually represent multiple physical paths through the network due
    to port aggregation. For example, a single-hop flow to Device D's
    loopback received by Device D and that can arrive on port D.et1 or
    D.et2 actually traverses two paths: D.et1 -> D.lo and D.et2 ->
    D.lo. However, we represnet this as one aggregated path:
    D.[et1 or et2] -> D.lo.
    """
    def __init__(self, hop_list):
        """
        @param {Hop[]} hop_list
        """
        self._hop_list = list(hop_list)

    def get_hop_list(self):
        return list(self._hop_list)

    def as_dict(self):
        """
        Example response for a path that covered a flow that begins on
        dev.[et1 or et2], then gets forwarded out of dev.et3 and into
        dev2.et1, which consumes the packet:
        {
          "hops": [
            {
              "ingress": {
                "device_name": "dev",
                "iface_names": ["et1", "et2"]
              },
              "egress": {
                "device_name": "dev",
                "iface_names": ["et3"]
              }
            },
            {
              "ingress": {
                "device_name": "dev2",
                "iface_names": ["et1"]
              },
              "egress": null
            }
          ]
        }

        """
        # Returning as a dict instead of a list in case we want to
        # add additional information in the future to the path
        # (e.g., path type).
        return {
            'hops': map(lambda hop: hop.as_dict(), self._hop_list),
            }

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(tuple(self._hop_list))
