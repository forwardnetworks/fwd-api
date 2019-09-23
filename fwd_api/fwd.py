#!/usr/bin/env python
# encoding: utf-8
#
# Confidential Information of Forward Networks, Inc.
# Copyright (c) 2014 Forward Networks, Inc.  All rights reserved.
#
'''
Helper functions to run API calls and verify JSON output.

@author: Brandon Heller
         Sivasankar Radhakrishnan

@contact:    support@forwardnetworks.com
'''
import mimetypes
import os
import re
import ssl
import time
import json

import requests
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from requests.exceptions import (MissingSchema, ConnectionError, SSLError,
                                 InvalidURL)
from requests.packages.urllib3.poolmanager import PoolManager
from flow import FlowsResponse
from fwd_api.check import NetworkCheckResult, Check
from fwd_api.network import Network, Snapshot
from fwd_api.notification import Notification
from ifaces_response import IfacesResponse
from devices_response import DevicesResponse

try:
    # Suppress InsecureRequestWarning
    # http://stackoverflow.com/a/28002687/1784469
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except:
    pass


def truncate(s, first_n=1000, last_n=1000):
    if len(s) > (first_n + last_n):
        return s[:first_n] + " ... " + s[-last_n:-1]
    else:
        return s


# Needed to adapt to TLSv1, per bug:
# https://github.com/kennethreitz/requests/issues/1083#issuecomment-11853729
DEFAULT_POOLBLOCK = False


class MyAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=DEFAULT_POOLBLOCK):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize)


class HTTPApi(object):
    '''Object to abstract access to an HTTP API, optionally with SSL.'''

    def __init__(self, url, username, password, verbose=False, verify=True,
                 verify_ssl_cert=True):
        """
        @param {string} url: base URL to which we should connect
        @param {string} username
        @param {string} password
        @param {boolean} verbose
        @param {boolean} verify
        @param {boolean} verify_ssl_cert: verify the provided SSL cert. Use
        with care!
        """
        self.url = url
        self.verbose = verbose
        self.verify = verify
        self.username = username
        self.password = password
        self.auth = HTTPBasicAuth(self.username, self.password)
        self.verify_ssl_cert = verify_ssl_cert
        mimetypes.init()

        # Use session adapter for TLSv1
        self.session = requests.Session()
        self.session.mount('https://', MyAdapter())

    def request(self, method, api_url_suffix, verbose=False, **kwargs):
        """Constructs and sends an http request of given method type

        @param {string} method: the http method to use
        @param {string} api_url_suffix: Appended to self.url
        @param {string} verbose: print request details to console.

        Other optional args:
        @param {dict} headers: dictionary of http headers to send with
        the request
        @files: dictionary of 'name': file-like-objects
        (or {'name': ('filename', fileobj)}) for multipart encoding
        upload.
        @param {dict} params: dictionary to be sent in the query
        string for the request
        @param {dict} data: dictionary, bytes, or file-like object to
        send in the body of the request
        @return: requests.Response object that contains the server's response
        to the http request
        """
        verbose = verbose or self.verbose
        # Wrap the API call with the base server url to create request address
        addr = self.url + api_url_suffix
        if verbose:
            print 'Calling [%s] %s' % (method.upper(), addr)

        # Set default Content-type and Accept headers
        headers = kwargs.get('headers')
        self.set_headers(headers, kwargs)

        # Allow redirects if this is not a PUT, POST, PATCH, or DELETE request
        if method.upper() not in ['PUT', 'POST', 'DELETE', 'PATCH']:
            kwargs.setdefault('allow_redirects', True)

        # Add authentication and SSL certification arguments
        kwargs.setdefault('auth', self.auth)
        kwargs.setdefault('verify', self.verify_ssl_cert)

        # Make the request
        try:
            r = self.session.request(method, addr, **kwargs)
        except (MissingSchema, InvalidURL) as e:
            raise Exception('Invalid URL %s: %s; please fix and try again.' %
                            (self.url, e))
        except SSLError as se:
            raise Exception('SSLError: %s.  Set VERIFY_SSL_CERT to False to '
                            'disable SSL certificate validation, then try '
                            'again.  This step is required when connecting '
                            'to numeric IPs, which cannot match certificates '
                            'that are defined for named URLs.' % se)
        except ConnectionError:
            raise Exception('Connection error to %s; please verify the URL '
                            'and your Internet connection and try again.' %
                            self.url)

        if verbose:
            print truncate(r.content)

        # Validate and return response
        if self.verify:
            self.verify_status_code(r)
        return r

    def get(self, api_url_suffix, headers=None, params=None, verbose=False):
        '''Constructs and sends an http GET request

        @api_url_suffix: the api call to make
        @verbose: print request details to console?
        @params: dictionary to be sent in the query string for the request
        @headers: dictionary of http headers to send with the request
        @return: requests.Response object that contains the server's response
            to the http request
        '''
        return self.request('get', api_url_suffix, verbose=verbose,
                            headers=headers, params=params)

    def post(self, api_url_suffix, data=None, headers=None, params=None,
             files=None, verbose=False):
        '''Constructs and sends an http POST request

        @api: the api call to make
        @data: dictionary, bytes, or file-like object to send in the body
            of the request
        @headers: dictionary of http headers to send with the request
        @params: dictionary to be sent in the query string for the request

        @param {dict} files: dictionary of 'name': file-like-objects
        (or {'name': ('filename', fileobj)}) for multipart encoding
        upload.

        @verbose: print request details to console?
        @return: requests.Response object that contains the server's response
            to the http request
        '''
        return self.request('post', api_url_suffix, verbose=verbose,
                            headers=headers, params=params, files=files,
                            data=data)

    def put(self, api_url_suffix, data=None, headers=None, params=None,
            verbose=False):
        '''Constructs and sends an http PUT request

        @api: the api call to make
        @data: dictionary, bytes, or file-like object to send in the body
            of the request
        @headers: dictionary of http headers to send with the request
        @params: dictionary to be sent in the query string for the request
        @verbose: print request details to console?
        @return: requests.Response object that contains the server's response
            to the http request
        '''
        return self.request('put', api_url_suffix, verbose=verbose,
                            headers=headers, params=params,
                            data=data)

    def patch(self, api, data=None, headers=None, params=None,
              verbose=False):
        '''Constructs and sends an http PATCH request

        @api: the api call to make
        @data: dictionary, bytes, or file-like object to send in the body
            of the request
        @headers: dictionary of http headers to send with the request
        @params: dictionary to be sent in the query string for the request
        @verbose: print request details to console?
        @return: requests.Response object that contains the server's response
            to the http request
        '''
        return self.request('patch', api, verbose=verbose,
                            headers=headers, params=params, data=data)

    def delete(self, api, headers=None, params=None, verbose=False):
        '''Constructs and sends an http DELETE request

        @api: the api call to make
        @verbose: print request details to console?
        @params: dictionary to be sent in the query string for the request
        @headers: dictionary of http headers to send with the request
        @return: requests.Response object that contains the server's response
            to the http request
        '''
        return self.request('delete', api, verbose=verbose,
                            headers=headers, params=params)

    def verify_status_code(self, r, err_prefix='', status_code=200):
        '''
        Verify the status code of the response. If status code does not match,
        raise exception with the received status code prefixed with err_prefix.

        @r: requests.response object obtained by issuing an http request
        @err_prefix: prefix to use for the error message
        @status_code: expected status code for the response r
        '''
        if r.status_code == status_code:
            return
        elif r.status_code == 401:
            raise Exception('%sUser authentication error; please check '
                            '"username", and "password" parameters and try '
                            'again.' % err_prefix)
        elif r.status_code == 404:
            raise Exception('%sURL not found %s' %
                            (err_prefix, r.url))
        elif r.status_code == 400:
            raise Exception('%sBad request to server %s; contents: %s' %
                            (err_prefix, r.url, r.content))
        elif r.status_code == 405:
            raise Exception('%sMethod not allowed; contents: %s' %
                            (err_prefix, r.content))
        elif r.status_code == 500:
            raise Exception('%sInternal server error to %s; contents:\n%s' %
                            (err_prefix, r.url, r.content))
        else:
            raise Exception('%sReceived http status code %d from server' %
                            (err_prefix, r.status_code))

    def set_headers(self, headers, kwargs):
        '''Hook to set initial header values.'''
        pass


class HTTPJSONApi(HTTPApi):
    '''HTTP API with JSON-formatted responses.'''

    def set_headers(self, headers, kwargs):
        '''Set initial header values.

        Sets header 'Accept': 'application/json' by default, if no value is
        passed in for the 'Accept' header.

        Sets header 'Content-type': 'application/json' by default, if no
        value is passed in for a request that includes data.
        '''
        if headers is not None:
            header_keys = [lambda x: x.lower() for x in headers.iterkeys()]
            if 'accept' not in header_keys:
                headers['Accept'] = 'application/json'
            if (not kwargs.get('data') is None and
                    'content-type' not in header_keys):
                headers['Content-type'] = 'application/json'
        else:
            headers = {'Accept': 'application/json'}
            if not kwargs.get('data') is None:
                headers['Content-type'] = 'application/json'
            kwargs['headers'] = headers

    def verify_json_error(self, r, err_prefix=''):
        '''
        Verify that the response body in json format does not contain any error
        field. This function assumes that the input response object contains a
        valid json response. If an error is present, it raises an Exception
        with the error message from the json response prefixed with err_prefix.

        @r: requests.response object obtained by issuing an http request
        @err_prefix: prefix to use for the error message
        @return: converted JSON object
        '''
        json = r.json()
        if ('error' in json):
            raise Exception('%s%s' % (err_prefix, json['error']))
        return json

    def verify_json_response(self, r, err_prefix=''):
        '''
        Verify status code for response, then verify that there's no JSON
        error.

        @r: requests.response object obtained by issuing an http request
        @err_prefix: prefix to use for the error message
        @return: converted JSON object
        '''
        self.verify_status_code(r, err_prefix)
        return self.verify_json_error(r, err_prefix)


class DeviceState(object):
    """The current state of a device, as reported by the collector
    """
    def __init__(self, device_name, collection_status):
        """
        @param {str} device_name
        @param {str} collection_status
        """
        self._device_name = device_name
        self._collection_status = collection_status

    def get_collection_status(self):
        return self._collection_status

    def get_device_name(self):
        return self._device_name

    @classmethod
    def _from_json_dict(cls, json_dict):
        return cls(json_dict['deviceName'],
                   json_dict['collectionStatus'])


class CollectorStatus(object):
    '''Wraps collection state of a network
    '''

    def __init__(self, is_online, is_idle):
        '''
        @param {bool} is_online: True if the collector is connected
        @param {bool} is_idle: True if the collector is not currently
        undergoing a collection
        '''
        self.is_online = is_online
        self.is_idle = is_idle

    @classmethod
    def _from_server_json_resp(cls, json_resp):
        d = json.loads(json_resp)
        return cls(d['isOnline'], d['isIdle'])


class Fwd(HTTPJSONApi):
    '''
    Object used for initiating connection to the forward server as a user and
    performing web calls.
    '''

    def __init__(self, url, username, password, verbose=True, verify=True,
                 verify_ssl_cert=True):
        '''
        @param {string} url: base URL to which we should connect
        @param {string} username
        @param {string} password
        @param {boolean} verbose
        @param {boolean} verify: Check that responses does not contain
        'error' in the JSON response.
        @param {boolean} verify_ssl_cert: verify the provided SSL cert? Use
        with care!
        '''
        super(Fwd, self).__init__(url=url, username=username,
                                  password=password, verbose=verbose,
                                  verify=verify,
                                  verify_ssl_cert=verify_ssl_cert)

    def upload_alias(self, alias, snapshot_id, verbose=True):
        '''Upload alias to snapshot

        @param {alias._Alias} alias: Alias to upload to server
        @param {int} snapshot_id: Id of snapshot to upload alias to.
        '''
        headers = {
            'Content-type': 'application/json'
        }
        self.put(alias.get_upload_url_suffix_str(snapshot_id),
                 data=json.dumps(alias._to_alias_dict()), verbose=verbose,
                 headers=headers)

    def upload_check(self, check, snapshot_id, verbose=True):
        '''Upload check to snapshot

        @param {check._Check} check: Check to upload to server
        @param {int} snapshot_id: Id of snapshot to upload check to.
        @return {NetworkCheckResult} check post result
        '''
        headers = {
            'Content-type': 'application/json'
        }
        response = self.post(Check.get_upload_url_suffix_str(snapshot_id),
                             data=json.dumps(check.to_check_dict()), verbose=verbose,
                             headers=headers)
        return NetworkCheckResult.from_json(response.json())

    def delete_check(self, snapshot_id, check_id, verbose=True):
        """Delete check from snapshot

        @param {int} snapshot_id: Id of snapshot from where check need to be deleted.
        @param {int} check_id: Id of the check need to be deleted.
        @return {int}: Status code of HTTP response.
        """
        headers = {
            'Content-type': 'application/json'
        }
        response = self.delete(Check.get_delete_url_suffix_str(snapshot_id, check_id),
                               verbose=verbose, headers=headers)
        return response.status_code is 200

    def get_check(self, snapshot_id, check_id, verbose=True):
        """Get check details

        @param {int} snapshot_id: Id of snapshot where check exists.
        @param {int} check_id: Id of the check for which details need to fetch.
        @return {NetworkCheckResult} check post result
        """
        url_suffix = '/api/snapshots/%d/checks/%d' % (snapshot_id, check_id)
        response = self.get(url_suffix, verbose=verbose)
        return NetworkCheckResult.from_json(response.json())

    def set_network_collector(self, network_id, username, verbose=True):
        '''Issue a request to associate a network with a collector with
        user username

        Note: that after issuing this call, you may have to wait for
        the collector and server to connect before issuing collection
        requests.

        @param {int} network_id: The id of the network to set the
        collector for.
        @param {str} username: The name of the user collector is
        configured for.
        '''
        headers = {
            'Content-type': 'application/json'
        }
        data = {
            'username': username
        }
        url_suffix = '/api/networks/%d/collector/user' % network_id

        self.put(url_suffix, data=json.dumps(data), verbose=verbose,
                 headers=headers)

        while True:
            status = self.get_collector_status(network_id, verbose)
            if status.is_online and status.is_idle:
                break
            time.sleep(.5)

    def get_collector_status(self, network_id, verbose=True):
        '''Get status of collector associated with network

        @param {int} network_id: The identifier of the network to get
        collector status for.

        @return {CollectorStatus}: The status of the collector
        attached to this network.
        '''
        url_suffix = '/api/networks/%d/collector/status' % network_id
        response = self.get(url_suffix, verbose=verbose)
        return CollectorStatus._from_server_json_resp(response.content)

    def non_blocking_collection_request(self, network_id, verbose=True):
        '''Send a request to server to collect a snapshot

        Note that this method requires the user to ensure that the
        collector is online and not otherwise already-collecting.

        @param {int} network_id: The identifier for the network to
        take snapshots for.
        '''
        url_suffix = '/api/networks/%d/startcollection' % network_id
        self.post(url_suffix, verbose=verbose)

    def blocking_collection_request(self, network_id, verbose=True):
        '''
        Block until we know that the collector is up, a request to the
        server has been issued, and the collector goes back to idle.

        Note: due to a couple of minor race conditions, this method
        may actually not guarantee that the collector receives the
        collection request or cannot process it. In the first of these
        cases, this method throws an exception. In the second, this
        method returns normally.

        @param {int} network_id: The identifier for the network to
        take snapshot for.
        '''
        # Wait until we know that the collector is up and idle
        while True:
            status = self.get_collector_status(network_id)
            if status.is_online and status.is_idle:
                break
            time.sleep(.5)

        self.non_blocking_collection_request(network_id, verbose)

        # The reason for this sleep is that the server does not
        # instantly update its status. This *hopefully* gives enough
        # time for the server to contact the collector and potentially
        # change its status.
        time.sleep(.5)

        # Wait until the collector goes back to up and idle: whatever
        # collection we issued has been processed
        while True:
            status = self.get_collector_status(network_id)
            if status.is_online and status.is_idle:
                break
            time.sleep(.5)

    def upload_data_sources(self, network_id, data_sources_filename,
                            verbose=True):
        '''Upload data sources file for collector

        @param {int} network_id: The id of the network to upload a
        data sources file to.
        @param {str} data_sources_filename: The name of the data
        sources file on the file system.
        '''
        url_suffix = '/api/networks/%d/dataSourcesFile' % network_id
        with open(data_sources_filename) as fd:
            contents = fd.read()
            self.put(url_suffix, data=contents, verbose=verbose)

    def upload_topo_list(self, network_id, topo_list_filename, verbose=True):
        '''Upload topo list file for collector

        @param {int} network_id: The id of the network to upload a
        topo list file to.
        @param {str} topo_list_filename: The name of the topo list file
        on the file system.
        '''
        headers = {
            'Content-type': 'application/json'
        }
        url_suffix = '/api/networks/%d/topology' % network_id

        with open(topo_list_filename, 'r') as fd:
            topo_contents = fd.read()

        self.put(url_suffix, data=topo_contents, verbose=verbose,
                 headers=headers)

    def create_network(self, network_name, verbose=False):
        '''
        Create a new network with the given name

        @network_name: Name of the network to create
        @return: ID of the network created
        '''
        params = {"name": network_name}
        r = self.post("/api/networks", params=params, verbose=verbose)

        err_prefix = "Error creating network: "
        self.verify_status_code(r, err_prefix)
        self.verify_json_error(r, err_prefix)

        json = r.json()
        return int(json["id"])

    def get_networks_info(self, verbose=True):
        '''Get networks details

        @return {list}: List of network objects.
        '''
        url_suffix = '/api/networks'
        response = self.get(url_suffix, verbose=verbose)
        result = []
        for network in response.json():
            result.append(Network.from_json(network))
        return result

    def get_flows(self, search_builder, snapshot_id, verbose=False):
        '''
        Note that this method will only return at most 100 flows,
        regardless of how many total flows are actually in the
        network. Compare FlowsResponse.get_total_flows to the length
        of the flows list in FlowsResponse.get_flows_list to determine
        if the network has more flows than were returned in this
        response.

        @return: FlowsResponse
        '''
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json, text/*',
        }
        r = self.post('/api/snapshots/%d/flows' % (snapshot_id),
                      data=json.dumps(search_builder.build_query()),
                      verbose=verbose, headers=headers)
        err_prefix = "Error getting flows: "
        self.verify_status_code(r, err_prefix)
        self.verify_json_error(r, err_prefix)
        return FlowsResponse.from_json(r.json())

    def take_snapshot(self, network_id, devices, verbose=False):
        """
        Take a snapshot for the given network id.

        @network_id: the network id to take the snapshot from
        @return: the id of uploaded snapshot
        """
        print ("Taking a snapshot for network ID %d..." % network_id)

        data = None
        if devices:
            data = json.dumps({'devices': devices})

        # Generate POST request to start a new collection
        r = self.post("/api/networks/%d/startcollection" % network_id,
                      data=data, verbose=verbose)

        err_prefix = "Error taking a new snapshot: "
        self.verify_status_code(r, err_prefix)
        self.verify_json_error(r, err_prefix)
        return r.status_code is 200

    def is_collection_inprogress(self, network_id, verbose=False):
        """
        Check collection progress for the specified network.

        @network_id: the network id for which collection progress need to check
        @return: True only if collection is inprogress.
        """

        # Generate GET request to get collection progress
        r = self.get("/api/networks/%d/collectionProgress" % network_id,
                     verbose=verbose)
        json_response = r.json()
        return 'inProgress' not in json_response or json_response['inProgress']

    def upload_snapshot(self, network_id, snapshot_zip_file, snapshot_name,
                        verbose=False):
        '''
        Uploads a snapshot zip file to the given network id.

        @network_id: the network id to upload snapshot to
        @snapshot_zip_file: the zip file containing the snapshot data
        @snapshot_name: the name of the snapshot
        @return: the id of uploaded snapshot
        '''
        print ("Uploading snapshot file %s to network ID %d..." %
               (snapshot_zip_file, network_id))

        # Get the content type for the snapshot file and create the files
        # dictionary for the request
        basename = os.path.basename(snapshot_zip_file)
        content_type = mimetypes.guess_type(snapshot_zip_file)[0]
        if content_type is None:
            content_type = "application/octet-stream"
        files = {'file': (basename, open(snapshot_zip_file, 'rb'),
                          content_type)}
        params = {"name": snapshot_name} if snapshot_name else None

        # Generate POST request to upload snapshot data
        start = time.time()
        r = self.post("/api/networks/%d/snapshots" % (network_id),
                      params=params, files=files, verbose=verbose)

        err_prefix = "Error uploading snapshot: "
        self.verify_status_code(r, err_prefix)
        self.verify_json_error(r, err_prefix)

        json = r.json()
        if not ("id" in json):
            raise Exception("%sDid not receive a snapshot ID from server" %
                            err_prefix)
        print "Upload completed in %0.2f seconds." % (time.time() - start)
        print "Network ID = %s. New snapshot ID = %s" % (network_id,
                                                         json["id"])

        return Snapshot.from_json(json)

    def get_snapshots_info(self, network_id, verbose=True):
        '''Get snapshots details

        @param {int} network_id: Network ID for which snapshots info need to get.
        @return {Network}: Network object.
        '''
        url_suffix = '/api/networks/%d/snapshots' % network_id
        response = self.get(url_suffix, verbose=verbose)
        return Network.from_json(response.json())

    def get_ifaces(self, snapshot_id, device_id, verbose=False):
        '''Get interfaces from device on target snapshot

        @param {int} snapshot_id
        @param {int} device_id
        @return {IfacesResponse}
        '''
        headers = {
            'Accept': 'application/json, text/*',
            }
        response = self.get('/api/snapshots/' + str(snapshot_id) +
                            '/devices/' + str(device_id) + '/interfaces',
                            verbose=verbose, headers=headers)
        return IfacesResponse.from_json(response.json())

    def get_devices(self, snapshot_id, verbose=False):
        '''Get devices from target snapshot

        @param {int} snapshot_id
        @return {DevicesResponse}
        '''
        headers = {
            'Accept': 'application/json, text/*',
            }
        response = self.get('/api/snapshots/' + str(snapshot_id) + '/devices/',
                            verbose=verbose, headers=headers)
        return DevicesResponse.from_json(response.json())

    def get_notifications(self, max=10, verbose=False):
        '''Gets up to max of the logged-in user's notifications
        '''
        headers = {
            'Accept': 'application/json, text/*',
            }
        response = self.get('/api/notifications?max=' + str(max), verbose=verbose, headers=headers)
        return Notification.from_json(response.json())

    def get_checks(self, snapshot_id, verbose=False):
        '''Gets all checks of a snapshot
        '''
        headers = {
            'Accept': 'application/json, text/*',
            }
        response = self.get('/api/snapshots/' + str(snapshot_id) + '/checks', verbose=verbose, headers=headers)
        checks = []
        for check in response.json():
            checks.append(NetworkCheckResult.from_json(check))
        return checks
