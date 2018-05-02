#!/usr/bin/env python

from contextlib import closing
from scopus import ScopusClient
from six import text_type
import os.path
import sqlite3
import pprint
import csv

from colorama import init, Fore
init(autoreset=True)


csvfields = ['authorId', 'scopusId', 'eid', 'title', 'issn', 'publicationName',
             'isbn', 'documenttype', 'authors', 'author-count', 'citedby-count',
             'pageRange', 'coverDate', 'coverDisplayDate', 'issueIdentifier',
             'volume', 'subtype', 'subtypeDescription']


def process_entry(entry, author_id):

    def tryor(fn, value_or, *args, **kwargs):
        try: return fn(*args, **kwargs)
        except: return value_or

    processed = {
        'authorId': author_id,
        'scopusId': entry.get('dc:identifier', '').lstrip('SCOPUS_ID:'),
        'eid': entry.get('eid', ''),
        'title': entry.get('dc:title', ''),
        'issn': entry.get('prism:issn', ''),
        'publicationName': entry.get('prism:publicationName', ''),
        'isbn': entry.get('prism:isbn', ''),
        'documenttype': entry.get('prism:aggregationType', ''),

        'authors': ', '.join('%s %s' % (author.get('given-name', ''),
                                        author.get('surname', ''))
                             for author in entry.get('author', [])),
        'author-count': tryor(int, 1, entry.get('author-count', {}).get('$', '1')),
        'citedby-count': tryor(int, 0, entry.get('citedby-count', '0')),
        'pageRange': entry.get('prism:pageRange', ''),
        'coverDate': entry.get('prism:coverDate', ''),
        'coverDisplayDate': entry.get('prism:coverDisplayDate', ''),
        'issueIdentifier': entry.get('prism:issueIdentifier', ''),
        'volume': entry.get('prism:volume', ''),
        'subtype': entry.get('subtype', ''),
        'subtypeDescription': entry.get('subtypeDescription', '')
    }

    return {k: text_type(v).encode('utf-8') for k,v in processed.items()}

if __name__ == '__main__':

    from config import APIKEY, DBFILE

    sc = ScopusClient(APIKEY)
    query = 'SELECT author, id FROM authors ORDER BY author'

    output_file = os.path.join(os.path.dirname(DBFILE), 'products.csv')

    with open(output_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csvfields)
        writer.writeheader()

        with sqlite3.connect(DBFILE) as connection:
            with closing(connection.cursor()) as cursor:

                for author, author_id in cursor.execute(query):
                    try:
                        print(Fore.CYAN + ('\n%s, [%s]' % (author, author_id)))
                        entries = sc.get_scopus_entries([author_id], complete=True)

                        for entry in entries:
                            processed = process_entry(entry, author_id)
                            # pprint.pprint(processed, indent=4)
                            writer.writerow(processed)

                        print(Fore.GREEN + ('Entries: %d' % len(entries)))

                    except KeyboardInterrupt:
                        print(Fore.RED + "\nBye bye :'(")
                        break
