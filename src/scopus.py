import xml.etree.ElementTree as ET
import requests
import json

class ScopusClient(object):
    def __init__(self, apiKey):
        self.apiKey = apiKey

    def authorSearch(self, query, xml=False, parse=False):
        resp = requests.get('http://api.elsevier.com/content/search/author',
                params={
                    'apiKey': self.apiKey,
                    'query': query,
                    'suppressNavLinks': 'true'
                },
                headers={
                    'Accept': 'application/%s' % ('xml' if xml else 'json')
                })
        if parse:
            resp = ET.fromstring(resp.content) if xml else resp.json()
        return resp

    def get_entries(self, first, last, affil, subjabbr):
        query = ('authlast(%s) AND authfirst(%s) AND affil(%s) AND subjabbr(%s)'
                 % (last, first, affil, subjabbr))
        resp = self.authorSearch(query, parse=True)
        if int(resp['search-results']['opensearch:totalResults']) == 0:
            return []
        return resp['search-results']['entry']
