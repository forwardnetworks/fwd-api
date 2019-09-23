# Confidential Information of Forward Networks, Inc.
# Copyright (c) 2015 Forward Networks, Inc.  All rights reserved.

import json
import subprocess
import abc


class Check(object):
    '''Base class for all Forward checks.
    '''

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def to_check_dict(self):
        '''Return json-izable dictionary representation of check
        '''

    @staticmethod
    def get_upload_url_suffix_str(snapshot_id):
        return '/api/snapshots/%(snapshot_id)d/checks' % {
            'snapshot_id': snapshot_id,
        }

    @staticmethod
    def get_delete_url_suffix_str(snapshot_id, check_id):
        return '/api/snapshots/%(snapshot_id)d/checks/%(check_id)d' % {
            'snapshot_id': snapshot_id,
            'check_id': check_id,
        }


class _StructuredCheckBase(Check):

    def __init__(self, from_clause, to_clause, check_type, name=''):
        """
        @param {Filter} from_clause: Can be None
        @param {Filter} to_clause: Can be None

        Note at least one of from_clause or to_clause must be
        specified.
        """
        self._from_clause = from_clause
        self._to_clause = to_clause
        self._check_type = check_type
        self._name = name
        if self._from_clause is None and self._to_clause is None:
            raise ValueError('Cannot create check base with empty ' +
                             'from and to clauses')

    def to_check_dict(self):
        result = {
            'checkType': self._check_type,
            'name': self._name,
            'filters': {},
            'noiseTypes': [],
        }
        if self._from_clause:
            result['filters']['from'] = self._from_clause.as_dict()
        if self._to_clause:
            result['filters']['to'] = self._to_clause.as_dict()
        return result

    def get_from_filters(self):
        return self._from_clause.as_dict()

    def get_to_filters(self):
        return self._to_clause.as_dict()


class ExistenceCheck(_StructuredCheckBase):
    '''Check from-to existence
    '''

    def __init__(self, from_clause, to_clause, name=''):
        super(ExistenceCheck, self).__init__(from_clause, to_clause,
                                             'Existential', name)


class IsolationCheck(_StructuredCheckBase):
    '''Check from-to isolation
    '''

    def __init__(self, from_clause, to_clause, name=''):
        super(IsolationCheck, self).__init__(from_clause, to_clause,
                                             'Isolation', name)


class ReachabilityCheck(_StructuredCheckBase):
    '''Check from-to full IP reachability
    '''

    def __init__(self, src_endpoint_filter, dst_location_filter=None, name=''):
        """
        @param {EndpointFilter} src_endpoint_filter: Headers and location
        filters to apply at packet ingress.

        @param {LocationFilter} dst_location_filter [optional]:
        If specified, this check validates that delivered packets reach
        devices/interfaces/hosts matching this filter.

        @param {str} name [optional]: What to name the newly created check
        """
        super(ReachabilityCheck, self).__init__(
            src_endpoint_filter, dst_location_filter,
            'Reachability', name)


class NetworkCheckStatus(object):
    NONE = "NONE"
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"

    @classmethod
    def from_string(cls, string):
        if string == "NONE":
            return NetworkCheckStatus.NONE
        elif string == "PASS":
            return NetworkCheckStatus.PASS
        elif string == "FAIL":
            return NetworkCheckStatus.FAIL
        elif string == "ERROR":
            return NetworkCheckStatus.FAIL
        else:
            raise ValueError('invalid check status')


class NetworkCheckType(object):
    ISOLATION = "Isolation"
    REACHABILITY = "Reachability"
    EXISTENTIAL = "Existential"
    QUERY_STRING_BASED = "QueryStringBased"
    PREDEFINED = "Predefined"

    @classmethod
    def from_string(cls, string):
        if string == "Isolation":
            return NetworkCheckType.ISOLATION
        elif string == "Reachability":
            return NetworkCheckType.REACHABILITY
        elif string == "Existential":
            return NetworkCheckType.EXISTENTIAL
        elif string == "QueryStringBased":
            return NetworkCheckType.QUERY_STRING_BASED
        elif string == "Predefined":
            return NetworkCheckType.PREDEFINED
        else:
            raise ValueError('invalid check type')


class NetworkCheckResult(object):
    """Python-ized representation of server's json returned from call to
    post check endpoint.
    """
    def __init__(self, check_id, name, check_type, status, raw_json):
        """
        @param {long} check id
        @param {string} check name, may be None
        @param {NetworkCheckType} check type
        @param {NetworkCheckStatus} status
        @param {string} Raw json received from Forward server
        """
        self._check_id = check_id
        self._name = name
        self._check_type = check_type
        self._status = status
        self._raw_json = raw_json

    @classmethod
    def from_json(cls, json_response):
        """
        @param {dict} json_response
        """
        check_id = None
        name = None
        check_type = None
        status = None
        if "id" in json_response:
            check_id = long(json_response['id'])
        if "definition" in json_response:
            if "name" in json_response['definition']:
                name = json_response['definition']['name']
            if "checkType" in json_response['definition']:
                check_type = NetworkCheckType.from_string(json_response['definition']['checkType'])
        if "status" in json_response:
            status = NetworkCheckStatus.from_string(json_response['status'])
        return NetworkCheckResult(check_id, name, check_type, status, json_response)

    def get_check_id(self):
        return self._check_id

    def get_name(self):
        return self._name

    def get_check_type(self):
        return self._check_type

    def get_status(self):
        return self._status

    def get_response(self):
        """
        WARNING:
        Do not use this method similar to other methods in this class. This method is created only for the use of
        calling from Ansible modules which create/get check in Forward server.
        """
        return self._raw_json


class VlanExistenceCheck(Check):
    """
    Checks that a list of VLANs are defined on a list of interfaces. And interfaces where VLANs configured must be edge
    interfaces.
    """
    def __init__(self, interfaces, vlans):
        """
        @param {list} interfaces: A list of DeviceInterface objects containing interface names.
        @param {list} vlans: A list of integer VLANs.
        """
        super(VlanExistenceCheck, self).__init__()
        self._interfaces = interfaces
        self._vlans = vlans

    def to_check_dict(self):
        return {
            'checkType': 'Predefined',
            'predefinedCheckType': 'VLAN_EXISTENCE',
            'params': {
                'interfaces': self._interfaces,
                'vlans': self._vlans
            }
        }


class DeviceInterface(object):
    """
    Class represents an interface of a device.
    """
    def __index__(self, device_name, iface_name):
        self._device_name = device_name
        self._iface_name = iface_name

    def __str__(self):
        return self._device_name + ' ' + self._iface_name
