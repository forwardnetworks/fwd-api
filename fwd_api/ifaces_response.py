from path import DeviceIfacePair, DeviceIfaceListPair


class IfaceResponse(object):
    def __init__(self, primary_name, alias_names, member_ports):
        self._primary_name = primary_name
        self._alias_names = list(alias_names)
        self._member_ports = list(member_ports)

    @classmethod
    def from_json(cls, json_dict):
        return IfaceResponse(
            json_dict['name'],
            json_dict['aliases'],
            json_dict['memberPorts'] if 'memberPorts' in json_dict else [])

    def matches_name(self, name):
        return name in self._alias_names

    def get_member_ports(self, device_name):
        """
        @param {str} device_name
        @return DeviceIfaceListPair or None if no member ports are defined
        """
        if len(self._member_ports) == 0:
            return None
        return DeviceIfaceListPair(device_name, self._member_ports)

    def to_device_iface_pair(self, device_name):
        return DeviceIfacePair(device_name, self._primary_name)


class IfacesResponse(object):

    def __init__(self, iface_response_list):
        """
        @param {IfaceResponse[]} iface_response_list
        """
        self._iface_response_list = list(iface_response_list)

    def get_iface_response_list(self):
        return list(self._iface_response_list)

    def get_by_iface_name(self, iface_name):
        for iface_response in self._iface_response_list:
            if iface_response.matches_name(iface_name):
                return iface_response
        return None

    @classmethod
    def from_json(cls, json_dict):
        iface_response_list = []
        for iface_resp_dict in json_dict['interfaces']:
            iface_response_list.append(
                IfaceResponse.from_json(iface_resp_dict))

        return IfacesResponse(iface_response_list)
