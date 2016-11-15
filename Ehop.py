import httplib
import ssl
import sys

class Ehop(object):

    def __init__(self, apikey='', host=''):
        self.apikey = apikey
        self.host = host

    def getKeys():
        global apikey
        global host
        with open('keys') as data_file:
            data = json.load(data_file)
            for key in data:
                self.host = key
                self.apikey = data[key]



    def api_request(self, method, path, body=''):
        headers = {'Accept': 'application/json',
                   'Authorization': "ExtraHop apikey=%s" % self.apikey}

        #gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)

        conn = httplib.HTTPSConnection(self.host,context=ssl._create_unverified_context())
        conn.request(method, "/api/v1/" + path, headers=headers, body=body)

        resp = conn.getresponse()

        if resp.status >= 300:
            raise ValueError('Non-200 status code from API request', resp.status, resp.reason, resp.read())
        return resp.read(), resp
