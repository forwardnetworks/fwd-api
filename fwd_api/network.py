

class Network(object):
    """
    Python-ized representation of Network info json returned from call to get snapshots endpoint.
    """
    def __init__(self, network_id, name, org_id, creator_id, snapshots):
        """
        @param {[Issue]} list of issue
        """
        self._network_id = int(network_id)
        self._name = name
        self._org_id = org_id
        self._creator_id = creator_id
        self._snapshots = snapshots

    @classmethod
    def from_json(cls, json_response):
        """
        @param {dict} json_response
        """
        snapshots = []
        if 'snapshots' in json_response:
            for snapshot_json in json_response['snapshots']:
                snapshots.append(Snapshot.from_json(snapshot_json))
        return Network(json_response['id'], json_response['name'], json_response['orgId'], json_response['creatorId'],
                       snapshots)

    def get_id(self):
        return self._network_id

    def get_name(self):
        return self._name

    def get_snapshots(self):
        return self._snapshots


class Snapshot(object):
    """
    Python-ized representation of Snapshot info.
    """
    def __init__(self, snapshot_id, creation_time):
        """
        @param {int} Snapshot ID
        @param {float} Snapshot creation time in milli-seconds.
        """
        self._snapshot_id = int(snapshot_id)
        self._creation_time = creation_time

    @classmethod
    def from_json(cls, json_response):
        """
        @param {dict} json_response
        """
        return Snapshot(json_response['id'], json_response['creationDateMillis'])

    def get_id(self):
        return self._snapshot_id

    def get_creation_time(self):
        return self._creation_time
