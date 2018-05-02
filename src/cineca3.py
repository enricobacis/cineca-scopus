#!/usr/bin/env python

from contextlib import closing
from operator import itemgetter
from datetime import datetime
from argparse import ArgumentParser
from csv import DictWriter
from utils import read_cineca_file, csv_to_db
import sqlite3
import json
import re

FIELDS = ['Ateneo', 'Facoltà', 'Fascia', 'Genere', 'S.C.',
          'Servizio prestato in altro ateneo', 'Struttura di afferenza',
          'author', 'identifier', 'eid', 'title', 'aggregationType',
          'citedby-count', 'publicationName', 'isbn', 'issn', 'volume',
          'issueIdentifier', 'pageRange', 'pageNum', 'coverDate',
          'coverDisplayDate', 'doi', 'numAuthors']

QUERY = 'SELECT entries FROM articles WHERE author = ? AND ateneo = ?'

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

    # eid and identifier default to 0
    entry['eid'] = entry.get('eid', 0)
    entry['identifier'] = entry.get('identifier', 0)

    # validate coverDate (or default to 1900-01-01)
    date = entry.get('coverDate', '')
    try:
        datesplit = list(map(int, date.split('-')))
        if len(datesplit) == 3 and datesplit[1] == 0:
            date = '%d-%d-%s' % (datesplit[0], datesplit[1]+1, datesplit[2])
        datetime.strptime(date, '%Y-%m-%d')
    except: entry['coverDate'] = '1900-01-01'

    entry['author'] = entry['Cognome e Nome']
    entry['pageNum'] = pagenum(entry.get('pageRange', None))
    return entry


def mergedicts(*dicts):
    return {k:v for d in dicts for k,v in d.items()}


if __name__ == '__main__':

    from config import FILENAME, DBFILE, OUTFILE, PRODUCTSDB

    parser = ArgumentParser('convert scopus db to csv')
    parser.add_argument('--input', default=FILENAME, help='cineca input file')
    parser.add_argument('--db', default=DBFILE, help='database file')
    parser.add_argument('--output', default=OUTFILE, help='output csv file')
    parser.add_argument('--outdb', default=PRODUCTSDB, help='output db file')
    args = parser.parse_args()

    with open(args.output, 'w') as outfile:
        csvreader = [row.to_dict() for row in read_cineca_file(args.input)]
        authors = [(row['Cognome e Nome'], row['Ateneo'], row) for row in csvreader]
        authors.sort(key=itemgetter(0, 1))

        csvwriter = DictWriter(outfile, FIELDS, extrasaction='ignore')
        csvwriter.writeheader()

        with sqlite3.connect(args.db) as connection:
            with closing(connection.cursor()) as cursor:
                for author, ateneo, authordata in authors:
                    entries = cursor.execute(QUERY, (author,ateneo)).fetchall()
                    if not entries:
                        print('Empty entry added for %s' % author)
                        csvwriter.writerow(process(authordata))
                    else:
                        inserted = set()
                        for entry in json.loads(entries[0][0]):
                            ID = entry.get('dc:identifier', '')
                            print('%s\t%s' % (author, ID))
                            if ID in inserted:
                                print(' * duplicate ignored *')
                            else:
                                inserted.add(ID)
                                csvwriter.writerow(process(mergedicts(authordata, entry)))

    print('\n[*] Converting csv to sqlite3db ...')
    csv_to_db(args.output, args.outdb, 'products')
