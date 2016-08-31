from contextlib import closing
from operator import itemgetter
from argparse import ArgumentParser
from csv import DictWriter, DictReader
import sqlite3
import json
import re

FIELDS = ['Ateneo', 'Facoltà', 'Fascia', 'Genere', 'S.C.',
          'Servizio prestato in altro ateneo', 'Struttura di afferenza',
          'author', 'identifier', 'eid', 'title', 'aggregationType',
          'citedby-count', 'publicationName', 'isbn', 'issn', 'volume',
          'issueIdentifier', 'pageRange', 'pageNum', 'coverDate',
          'coverDisplayDate', 'doi', 'numAuthors']

QUERY = 'SELECT entries FROM articles WHERE author = ?'

def pagenum(pageRange):
    try:
        page = list(map(int, pageRange.split('-')))
        return 1 if len(page) == 1 else page[1] - page[0]
    except:
        return None

def process(entry):
    for key, value in list(entry.items()):
        if ':' in key:
            del entry[key]
            key = key.partition(':')[2]
            entry[key] = value

    match = re.match('Author list of (\d+)', entry.get('message', ''))
    if match: entry['numAuthors'] = int(match.group(1))
    else: entry['numAuthors'] = len(entry.get('author', [])) or None

    entry['author'] = entry['Cognome e Nome']
    entry['pageNum'] = pagenum(entry.get('pageRange', None))
    return entry


def mergedicts(*dicts):
    return {k:v for d in dicts for k,v in d.items()}


if __name__ == '__main__':

    parser = ArgumentParser('convert scopus db to csv')
    parser.add_argument('INFILE', help='input csv file')
    parser.add_argument('DBFILE', help='database file')
    parser.add_argument('OUTFILE', help='output csv file')
    args = parser.parse_args()

    with open(args.INFILE) as infile, open(args.OUTFILE, 'w') as outfile:
        csvreader = DictReader(infile)
        authors = [(row['Cognome e Nome'], row) for row in csvreader]
        authors.sort(key=itemgetter(0))

        csvwriter = DictWriter(outfile, FIELDS, extrasaction='ignore')
        csvwriter.writeheader()

        with sqlite3.connect(args.DBFILE) as connection:
            with closing(connection.cursor()) as cursor:
                for author, authordata in authors:
                    entries = cursor.execute(QUERY, (author,)).fetchall()
                    if not entries:
                        print('Empty entry added for %s' % author)
                        csvwriter.writerow(process(authordata))
                    else:
                        for entry in json.loads(entries[0][0]):
                            csvwriter.writerow(process(mergedicts(authordata, entry)))
