class DeviceResponse(object):
    def __init__(self, name, id):
        """
        @param {str} name
        @param {int} id
        """
        self._name = name
        self._id = id

    @classmethod
    def from_json(cls, json_dict):
        return DeviceResponse(json_dict['name'], json_dict['id'])

    def get_name(self):
        return self._name

    def get_id(self):
        return self._id

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class DevicesResponse(object):

    def __init__(self, device_response_list):
        """
        @param {DeviceResponse[]} device_response_list
        """
        self._device_response_list = list(device_response_list)

    def get_device_response_list(self):
        return list(self._device_response_list)

    def get_device_response_by_name(self, device_name):
        """
        @return {DeviceResponse or None} if device does not exist
        """
        for device_response in self._device_response_list:
            if device_response.get_name() == device_name:
                return device_response
        return None

    @classmethod
    def from_json(cls, json_list):
        device_response_list = []
        for device_resp_dict in json_list:
            device_response_list.append(
                DeviceResponse.from_json(device_resp_dict))

        return DevicesResponse(device_response_list)
