# Confidential Information of Forward Networks, Inc.
# Copyright (c) 2015 Forward Networks, Inc.  All rights reserved.

import json
import subprocess
import abc


class _Alias(object):
    '''Base class for all alias objects.
    '''

    __metaclass__ = abc.ABCMeta

    def __init__(self, alias_name):
        self.name = alias_name

    def get_name(self):
        return self.name

    @abc.abstractmethod
    def _to_alias_dict(self):
        '''Return json-izable dictionary representation of alias.
        '''

    def _get_upload_url_suffix_str(self, snapshot_id):
        return '/api/snapshots/%(snapshot_id)d/aliases/%(name)s' % {
            'snapshot_id': snapshot_id,
            'name': self.name
        }


class InterfaceAlias(_Alias):
    def __init__(self, alias_name, dev, port):
        '''
        @param {str} alias_name: The name of the alias to upload
        @param {str} dev: The name of the target device for the alias
        @param {str} port: The name of the device port for the alias
        '''
        super(InterfaceAlias, self).__init__(alias_name)
        self._dev = dev
        self._port = port
        if (self._dev is not None) and (self._port is None):
            self._port = '*'
        self._validate_args()

    def _validate_args(self):
        if (self._dev is None) and (self._port is not None):
            raise ValueError('If port is specified, dev must be as well')

    def _to_alias_dict(self):
        d = {
            "type": "INTERFACES",
            "name": self.name,
        }
        if self._dev is not None:
            d["values"] = [self._dev + ' ' + self._port]
        return d


class VlanInterfaceAlias(InterfaceAlias):
    def __init__(self, alias_name, **kwargs):
        '''
        @param {str} alias_name: The name of the alias to upload

        Keyword arguments:
        @param {str} dev: The name of the target device for the alias
        @param {str} port: The name of the device port for the alias
        @param {list} vlans: All vlans covered by this alias. Each
        element should be a string. Can also accept ranges. E.g.,
        "1-5".
        '''

        vlans = kwargs.get('vlans')
        self._vlans = []
        if vlans is not None:
            self._vlans = list(vlans)
        dev = kwargs.get('dev')
        port = kwargs.get('port')
        super(VlanInterfaceAlias, self).__init__(alias_name, dev, port)
        self._validate_args()

    def _validate_args(self):
        super(VlanInterfaceAlias, self)._validate_args()
        if (len(self._vlans) == 0) and (self._dev is None):
            raise ValueError('Either vlans or dev+iface name ' +
                             'must be specified')

    def _to_alias_dict(self):
        d = super(VlanInterfaceAlias, self)._to_alias_dict()
        if len(self._vlans) != 0:
            d['vlanIds'] = list(self._vlans)
        return d


class TrafficAlias(_Alias):
    def __init__(self, alias_name, traffic_dict):
        '''
        @param {str} alias_name: The name of the alias to upload
        @param {dict} traffic_dict: Keys are Forward
        TrafficAliasType-s. Values are lists.
        '''
        super(TrafficAlias, self).__init__(alias_name)
        self._traffic_dict = traffic_dict

    def _to_alias_dict(self):
        return {
            "type": "HEADERS",
            "name": self.name,
            "values": self._traffic_dict
        }


class IpV4TrafficAlias(TrafficAlias):
    def __init__(self, alias_name, ipv4_addr_list):
        '''
        @param {str} alias_name: The name of the alias to upload
        @param {list} ipv4_addr_list: Each element is a string containing
        an IPv4 address or subnet.
        '''
        traffic_dict = {
            'eth_type': ['0x800'],
            'ip_addr': ipv4_addr_list
        }
        super(IpV4TrafficAlias, self).__init__(alias_name, traffic_dict)


class IpV6TrafficAlias(TrafficAlias):
    def __init__(self, alias_name, ipv6_addr_list):
        '''
        @param {str} alias_name: The name of the alias to upload
        @param {list} ipv6_addr_list: Each element is a string
        containing an IPv6 address or subnet.
        '''
        traffic_dict = {
            'eth_type': ['0x86dd'],
            'ip_addr': ipv6_addr_list
        }
        super(IpV6TrafficAlias, self).__init__(alias_name, traffic_dict)


class VlanTrafficAlias(TrafficAlias):
    def __init__(self, alias_name, vlan_ids_list):
        '''
        @param {str} alias_name
        @param {str[]} vlan_ids_list
        '''
        traffic_dict = {
            'vlan_vid': list(vlan_ids_list)
        }
        super(VlanTrafficAlias, self).__init__(alias_name, traffic_dict)


class HostAlias(_Alias):
    def __init__(self, alias_name, hosts_list):
        '''
        @param {str} alias_name: The name of the alias
        @param {list} hosts_list: Each element is a string
        corresponding to a host name
        '''
        super(HostAlias, self).__init__(alias_name)
        self._hosts_list = hosts_list

    def _to_alias_dict(self):
        return {
            'type': 'HOSTS',
            'name': self.name,
            'values': self._hosts_list
        }
