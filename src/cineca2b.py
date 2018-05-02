#!/usr/bin/env python

from contextlib import closing
from scopus import ScopusClient
import sqlite3
import json

from colorama import init, Fore
init(autoreset=True)


if __name__ == '__main__':

    from config import APIKEY, DBFILE

    sc = ScopusClient(APIKEY)
    query = ('SELECT author, ateneo, group_concat(id) '
             'FROM authors GROUP BY author, ateneo')
    with sqlite3.connect(DBFILE) as connection:
        connection.execute('CREATE TABLE IF NOT EXISTS articles ('
                           'author, ateneo, num, entries)')
        with closing(connection.cursor()) as cursor:
            for author, ateneo, IDs in cursor.execute(query):
                try:
                    print(Fore.CYAN + ('\n%s, %s [%s]' % (author, ateneo, IDs)))
                    entrs = sc.get_scopus_entries(IDs.split(','), complete=True)
                    connection.execute('INSERT INTO articles VALUES (?,?,?,?)',
                            (author, ateneo, len(entrs), json.dumps(entrs)))
                    print(Fore.GREEN + ('Entries: %d' % len(entrs)))
                except KeyboardInterrupt:
                    print(Fore.RED + "\nBye bye :'(")
                    break
