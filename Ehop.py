import httplib
import ssl
import sys

class Ehop(object):

    def __init__(self, apikey='', host=''):
        self.apikey = apikey
        self.host = host

    def api_request(self, method, path, body=''):
        headers = {'Accept': 'application/json',
                   'Authorization': "ExtraHop apikey=%s" % self.apikey}

        #gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)

        conn = httplib.HTTPSConnection(self.host)
        conn.request(method, "/api/v1/" + path, headers=headers, body=body)

        resp = conn.getresponse()

        if resp.status >= 300:
            raise ValueError('Non-200 status code from API request', resp.status, resp.reason, resp.read())
        return resp.read()
