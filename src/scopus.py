from itertools import chain
import requests

_HEADERS = {'Accept': 'application/json'}

class ScopusResponse(object):

    def __init__(self, data):
        self._data = data

    def __getitem__(self, key):
        return self._data['search-results'][key]

    def __iter__(self):
        while True:
            yield self
            self = self.next()

    def entries(self):
        return [] if self.is_empty() else self['entry']

    def is_empty(self):
        return int(self['opensearch:totalResults']) == 0

    def next_page_url(self):
        try: return next(l['@href'] for l in self['link'] if l['@ref']=='next')
        except: return None

    def next(self):
        url = self.next_page_url()
        if not url: raise StopIteration
        return ScopusResponse(requests.get(url, headers=_HEADERS).json())

    def all_entries(self):
        return list(chain.from_iterable(page.entries() for page in self))


class ScopusClient(object):

    _AUTHOR_API = 'http://api.elsevier.com/content/search/author'
    _SCOPUS_API = 'http://api.elsevier.com/content/search/scopus'

    def __init__(self, apiKey):
        self.apiKey = apiKey

    def _api(self, endpoint, query, extra_params=None):
        params = extra_params.copy() if extra_params else {}
        params.update({'apiKey':self.apiKey, 'query':query})
        resp = requests.get(endpoint, headers=_HEADERS, params=params)
        return ScopusResponse(resp.json())

    def authorSearch(self, query, extra_params=None):
        return self._api(self._AUTHOR_API, query, extra_params)

    def scopusSearch(self, query, complete=False, extra_params=None):
        extra_params = extra_params.copy() if extra_params else {}
        extra_params.update({'view': 'COMPLETE' if complete else 'STANDARD'})
        return self._api(self._SCOPUS_API, query, extra_params)

    def get_scopus_entries(self, same_author_ids, complete):
        query = ' OR '.join('AU-ID(%s)' % ID for ID in same_author_ids)
        return self.scopusSearch(query, complete).all_entries()

    def get_authors(self, first, last, affil, subjabbr):
        query = ('authlast(%s) AND authfirst(%s) AND affil(%s) AND subjabbr(%s)'
                 % (last, first, affil, subjabbr))
        return self.authorSearch(query).all_entries()
