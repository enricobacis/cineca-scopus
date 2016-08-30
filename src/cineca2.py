from collections import namedtuple
from contextlib import closing
from operator import itemgetter
from tabulate import tabulate
from scopus import ScopusClient
import os.path
import sqlite3
import json
import sys

from colorama import init, Fore
init(autoreset=True)

from config import APIKEY, FILENAME, DBFILE

if __name__ == '__main__':
    sc = ScopusClient(APIKEY)
    query = 'SELECT author, group_concat(id) FROM authors GROUP BY author'
    with sqlite3.connect(DBFILE) as connection:
        connection.execute('CREATE TABLE IF NOT EXISTS articles ('
                           'author PRIMARY KEY, data)')
        with closing(connection.cursor()) as cursor:
            for author, IDs in cursor.execute(query):
                print(author, IDs)
                entries = sc.get_scopus_entries(IDs.split(','))
                connection.execute('INSERT INTO articles VALUES (?, ?)',
                                   (author, json.dumps(entries)))
                print('Entries: %d' % len(entries))
