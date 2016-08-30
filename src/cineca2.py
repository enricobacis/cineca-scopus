from contextlib import closing
from scopus import ScopusClient
import sqlite3
import json

from colorama import init, Fore
init(autoreset=True)

from config import APIKEY, DBFILE

if __name__ == '__main__':
    sc = ScopusClient(APIKEY)
    query = 'SELECT author, group_concat(id) FROM authors GROUP BY author'
    with sqlite3.connect(DBFILE) as connection:
        connection.execute('CREATE TABLE IF NOT EXISTS articles ('
                           'author PRIMARY KEY, num, entries)')
        with closing(connection.cursor()) as cursor:
            for author, IDs in cursor.execute(query):
                try:
                    print(Fore.CYAN + ('\n%s [%s]' % ( author, IDs)))
                    entries = sc.get_scopus_entries(IDs.split(','))
                    connection.execute('INSERT INTO articles VALUES (?,?,?)',
                            (author, len(entries), json.dumps(entries)))
                    print(Fore.GREEN + ('Entries: %d' % len(entries)))
                except KeyboardInterrupt:
                    print(Fore.RED + "\nBye bye :'(")
                    break
