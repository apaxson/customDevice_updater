from Ehop import Ehop
import json
import time
import re
import sys

class Discoverer(object):
    """An application disc"""


    def __init__(self,
                 apikey='',
                 host='',
                 lookback=-86400000,        # 1 day in milliseconds
                 device_cache_ttl=1800,     # 30 minutes in seconds
                 verbose=True):


        self.apikey       = apikey
        self.host         = host

        self.client       = Ehop(self.apikey, self.host)
        self.lookback     = lookback

        self.devices_cache      = []
        self.devices_cache_type = None
        self.devices_cache_ttl  = device_cache_ttl
        self.devices_cache_ts   = 0

        self.devices_cache_metric_category = None
        self.devices_cache_metric          = None

        self.verbose = verbose

    def get_devices_by_type(self, type):

        query = 'devices?' +                                \
                'limit=0&' +                                \
                'search_type=type&' +                       \
                'value='+ type + '&' +                      \
                'active_from=' + str(self.lookback) + '&' + \
                'active_until=0'


        return json.loads(self.client.api_request('GET',
                                       query))

    def get_device_metrics(self, device_id, metric_category, metric):

        body = {
                    "cycle": "auto",
                    "from": self.lookback,
                    "metric_category": metric_category.split('.')[2],
                    "metric_specs": [{"name": metric}],
                    "object_ids": [device_id],
                    "object_type": "device",
                    "until": 0
                }

        response = json.loads(self.client.api_request('POST',
                                                      'metrics/total',
                                                      json.dumps(body)))


        return response['stats'][0]['values'][0]

    def tag_device(self, device_id, tag_id):
        path = 'tags/'+ str(tag_id) + '/devices/' + str(device_id)
        self.client.api_request('POST',path)

    def tag_by_metric_identifier(self, metric_category, metric, key, tag):

        # Check that tag exists
        tag_id      = self._make_tag(tag)

        # Determine the device type required for the metric category
        device_type = self._process_metric_category(metric_category)

        # Reduce excess API calls be using cache of devices
        # If the cache is older than the cache TTL or looking at a different
        # type of device, update the device cache
        if ((device_type != self.devices_cache_type) or
            ((self.devices_cache_ts + self.devices_cache_ttl) < time.time())):

            self.devices_cache      = self.get_devices_by_type(device_type)
            self.devices_cache_ts   = time.time()
            self.devices_cache_type = device_type

            # If new devices, must update metrics.
            self.devices_cache_metric_category = metric_category
            self.devices_cache_metric          = metric

            # Populate device list with the metric
            for i in range(0, len(self.devices_cache)):
                if (self.verbose):
                    self._print_status_bar(i, len(self.devices_cache))
                
                device_id = self.devices_cache[i]['id']
                self.devices_cache[i]['device_metrics'] = self.get_device_metrics(device_id, metric_category, metric)

        elif ((self.devices_cache_metric_category != metric_category) or
            (self.devices_cache_metric != metric)):

            self.devices_cache_metric_category = metric_category
            self.devices_cache_metric          = metric

            # Populate device list with the metric
            for i in range(0, len(self.devices_cache)):
                if (self.verbose):
                    self._print_status_bar(i, len(self.devices_cache))

                device_id = self.devices_cache[i]['id']
                self.devices_cache[i]['device_metrics'] = self.get_device_metrics(device_id, metric_category, metric)

        # From this point, functionality can diverge.
        # A) Find known identifiers and tag accordingly.
        # B) Group all detail metrics and determine possible identifiers
        # This function will implement (A)

        for device in self.devices_cache:
            if (type(device['device_metrics']) is not list):
                raise ValueError('Expecting list (Topnset)',
                                 device['device_metrics'])


            for metric in device['device_metrics']:

                # If strict string matching
                if (key['type'] == 'string'):
                    if (key['value'] in metric['key']['str']):
                        self.tag_device(device['id'],tag_id)

                # If regex (used for case insensitive)
                elif (key['type'] == 'regex'):

                    # Regexs stored in forward slash notation
                    # Strip slashes and check for i flag
                    (regex_string,i_flag) = self._process_regex(key['value'])
                    if (i_flag):
                        if (re.search(regex_string, metric['key']['str'], re.I) != None):
                            self.tag_device(device['id'],tag_id)
                    else:
                        if (re.search(regex_string, metric['key']['str']) != None):
                            self.tag_device(device['id'],tag_id)
                else:
                    raise ValueError('Unexpected metric key type', key['type'], key['value'])

    def _print_status_bar(self, numerator, denominator):
        assert denominator > 0, 'Denominator cannot be zero'
        progress = float(numerator)/denominator
        sys.stdout.write("\r%.4f%%" % progress)
        sys.stdout.flush()


    def _process_regex(self, regex):
        assert (regex.index('/') == 0), 'Regex does not follow forward-slash notation: ' + regex
        last_slash = regex.rfind('/')

        assert (last_slash != 0), 'Regex does not follow forward-slash notation: ' + regex

        regex_string = regex[1:last_slash]
        flag_string  = regex[last_slash:]

        # i in regex flags indicates case insensitive
        return (regex_string, ('i' in flag_string))



    def _make_tag(self, tag):
        # Check that tag exist

        tags = json.loads(self.client.api_request('GET','tags'))
        for t in tags:
            if (t['name'] == tag):
                return t['id']

        # Tag does not exist
        body = {"name": tag}
        self.client.api_request('POST','tags', json.dumps(body))

        tags = json.loads(self.client.api_request('GET','tags'))
        for t in tags:
            if (t['name'] == tag):
                return t['id']

    def _process_metric_category(self, metric_category):
        # EH metrics take the form extrahop.[object_type].[metric_category]
        metric_components = metric_category.split('.')

        if (metric_components[0] != 'extrahop'):
            raise ValueError('Unexpected metric scope. Must follow form extrahop.device.[metric_category]',metric_category)
        elif (metric_components[1] != 'device'):
            raise ValueError('Tagging occurs at the device level. Must follow form extrahop.device.[metric_category]',metric_category)

        mc = metric_components[2].split('_')
        for i in range(0,len(mc)):
            # if mc[i] is server or client, the previous index holds the protocol
            if (mc[i] == 'server' or mc[i] == 'client'):
                return mc[i-1] + '_' + mc[i]

        raise ValueError('Unexpected metric category. Does not contain "server" or "client"',metric_category)
