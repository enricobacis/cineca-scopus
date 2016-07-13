from utils import read_csv, split_name, iterate_names
from scopus import ScopusClient

from config import APIKEY, FILENAME

if __name__ == '__main__':
    sc = ScopusClient(APIKEY)
    rows = read_csv(FILENAME)
    for row in rows:
        namefield = row['Cognome e Nome']
        name, surname = split_name(namefield)
        for na, su in iterate_names(name, surname):
            ids = sc.author_ids(na, su, 'Italy', 'COMP')
            if ids: break
        print('%s,%s,%s' % (name, surname, ' '.join(ids)))
