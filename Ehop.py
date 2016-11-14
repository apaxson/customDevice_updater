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

        conn = httplib.HTTPSConnection(self.host,context=ssl._create_unverified_context())
        conn.request(method, "/api/v1/" + path, headers=headers, body=body)

        resp = conn.getresponse()

<<<<<<< fc41b0098ea76219cf5d8a16754416fc76bb1bad
=======
        if resp.status >= 300:
            raise ValueError('Non-200 status code from API request', resp.status, resp.reason, resp.read())
>>>>>>> Removed SSL Cert check and changed return of api_request() to full response object.
        return resp
