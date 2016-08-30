from contextlib import closing
from argparse import ArgumentParser
from csv import DictWriter
import sqlite3
import json
import re

FIELDS = ['author', 'identifier', 'eid', 'title', 'aggregationType',
          'citedby-count', 'publicationName', 'isbn', 'issn', 'volume',
          'issueIdentifier', 'pageRange', 'pageNum', 'coverDate',
          'coverDisplayDate', 'doi', 'numAuthors']

QUERY = 'SELECT author, entries FROM articles ORDER BY author'


def pagenum(pageRange):
    try:
        page = list(map(int, pageRange.split('-')))
        return 1 if len(page) == 1 else page[1] - page[0]
    except:
        return None


def process(author, entry):
    for key, value in list(entry.items()):
        if ':' in key:
            del entry[key]
            key = key.partition(':')[2]
            entry[key] = value

    match = re.match('Author list of (\d+)', entry.get('message', ''))
    if match: entry['numAuthors'] = int(match.group(1))
    else: entry['numAuthors'] = len(entry.get('author', [])) or None

    entry['author'] = author
    entry['pageNum'] = pagenum(entry['pageRange'])
    return entry


if __name__ == '__main__':

    parser = ArgumentParser('convert scopus db to csv')
    parser.add_argument('DBFILE', help='database file')
    parser.add_argument('OUTFILE', help='output csv file')
    args = parser.parse_args()

    with open(args.OUTFILE, 'w') as csvfile:
        csvwriter = DictWriter(csvfile, FIELDS, extrasaction='ignore')
        csvwriter.writeheader()
        with sqlite3.connect(args.DBFILE) as connection:
            with closing(connection.cursor()) as cursor:
                for author, entries in cursor.execute(QUERY):
                    for entry in json.loads(entries):
                        csvwriter.writerow(process(author, entry))
