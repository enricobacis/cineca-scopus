import requests

class ScopusClient(object):

    _AUTHOR_API = 'http://api.elsevier.com/content/search/author'
    _SCOPUS_API = 'http://api.elsevier.com/content/search/scopus'
    _HEADERS = {'Accept': 'application/json'}

    def __init__(self, apiKey):
        self.apiKey = apiKey

    def _api(self, endpoint, query, parse=False):
        resp = requests.get(endpoint, headers=self._HEADERS,
                params={'apiKey': self.apiKey, 'query': query})
        return resp.json() if parse else resp

    def _is_empty(self, resp):
        return int(resp['search-results']['opensearch:totalResults']) == 0

    def _all_pages(self, resp):
        if not self._is_empty(resp):
            while True:
                yield resp
                try:
                    url = next(li['@href']
                               for li in resp['search-results']['link']
                               if li['@ref'] == 'next')
                    resp = requests.get(url, headers=self._HEADERS).json()
                except: break

    def authorSearch(self, query, parse=False):
        return self._api(self._AUTHOR_API, query, parse)

    def scopusSearch(self, query, parse=False):
        return self._api(self._SCOPUS_API, query, parse)

    def get_scopus_entries(self, same_author_ids):
        query = ' OR '.join('AU-ID(%s)' % ID for ID in same_author_ids)
        resp = self.scopusSearch(query, parse=True)
        return [entry for page in self._all_pages(resp)
                      for entry in page['search-results']['entry']]

    def get_authors(self, first, last, affil, subjabbr):
        query = ('authlast(%s) AND authfirst(%s) AND affil(%s) AND subjabbr(%s)'
                 % (last, first, affil, subjabbr))
        resp = self.authorSearch(query, parse=True)
        return [] if self._is_empty(resp) else resp['search-results']['entry']
