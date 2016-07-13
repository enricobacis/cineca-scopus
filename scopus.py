import requests

class ScopusClient(object):
    def __init__(self, apiKey):
        self.apiKey = apiKey

    def authorSearch(self, query):
        resp = requests.get('http://api.elsevier.com/content/search/author',
                            {'apiKey': self.apiKey,
                             'query': query,
                             'suppressNavLinks': 'true'})
        return resp.json()

    def author_ids(self, first, last, affil, subjabbr):
        resp = self.authorSearch(
                'authlast(%s) AND authfirst(%s) AND affil(%s) AND subjabbr(%s)'
                % (last, first, affil, subjabbr))
        if int(resp['search-results']['opensearch:totalResults']) == 0:
            return []
        return [entry.get('dc:identifier', ':').split(':')[1]
                for entry in resp['search-results']['entry']]
