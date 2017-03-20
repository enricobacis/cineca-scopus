from collections import namedtuple
from operator import itemgetter
from tabulate import tabulate
from scopus import ScopusClient
from utils import *

import traceback
import os.path
import sqlite3
import json
import sys

from colorama import init, Fore
init(autoreset=True)

Entry = namedtuple('Entry', ['ID', 'affil_country', 'affil_city', 'affil_name',
                             'name', 'surname', 'documents', 'freqs'])

def get_frequency_for_area(entry):
    areas = entry['subject-area']
    if isinstance(areas, dict): areas = [areas]
    return ', '.join('%s: %s' % (a['@abbrev'], a['@frequency']) for a in areas)

def make_entry(entry):
    return Entry(
        ID=entry['dc:identifier'].partition(':')[2],
        affil_country=entry['affiliation-current']['affiliation-country'],
        affil_city=entry['affiliation-current']['affiliation-city'],
        affil_name=entry['affiliation-current']['affiliation-name'],
        name=entry['preferred-name']['given-name'],
        surname=entry['preferred-name']['surname'],
        documents=int(entry['document-count']),
        freqs=get_frequency_for_area(entry))

def entry_score(query, entry):
    return max(fuzzy_score(query, entry.affil_name),
               fuzzy_score(query, entry.affil_city))

def sorted_entries(entries, ateneo):
    entries = [(make_entry(e), e) for e in entries]
    entries = [(e[0], e[1], entry_score(ateneo, e[0])) for e in entries]
    key = lambda entry: (entry[2], entry[0].documents)
    return sorted(entries, key=key, reverse=True)

def get_entries(sc, namefield, **kwargs):
    for name, surname in iterate_names(*split_name(namefield)):
        entries = sc.get_authors(authfirst=name, authlast=surname, **kwargs)
        if entries: return entries
    return []

def show_entries(entries):
    print tabulate([[i, e[2]*100.] + list(e[0]) for i,e in enumerate(entries)],
                   headers=('idx', '% match') + Entry._fields, tablefmt="grid")

def user_select_entries(entries):
    while True:
        inp = raw_input(Fore.YELLOW + '\ncomma separated indexes: ')
        try:
            if not inp: return []
            chosen = map(int, inp.strip().split(','))
            if min(chosen)<0 or max(chosen)>=len(entries): raise ValueError
            print chosen
            return [entries[c] for c in chosen]
        except ValueError:
            print(Fore.RED + 'Indexes must be 0 <= idx < %d' % len(entries))

def init_db(dbfile):
    if os.path.isfile(dbfile):
        inp = raw_input(Fore.RED + "Database file already exists. " +
                        "Type 'yes' to append, anything else to quit: ")
        if inp.strip() != 'yes': sys.exit(0)

    with sqlite3.connect(dbfile) as connection:
        connection.execute('CREATE TABLE IF NOT EXISTS'
                           ' authors(author, ateneo, id UNIQUE, entry)')

def main(apikey, filename, dbfile):
    sc = ScopusClient(apikey)
    init_db(dbfile)
    default_ateneo = None
    extra_params = {'affil': 'Italy'}

    for row in read_cineca_file(filename):
        if 'Ateneo' not in row and not default_ateneo:
            default_ateneo = raw_input(Fore.YELLOW +
                    "No 'Ateneo' field, insert default value (e.g. Bergamo): ")
        namefield, ateneo = row['Cognome e Nome'], row.get('Ateneo', default_ateneo)

        try:
            print '\n%s\n\n%s\n' % ('='*80, row)
            entries = sorted_entries(get_entries(sc, namefield, **extra_params), ateneo)
            if len(entries) == 0:
                print(Fore.RED + '\nNo entries for this author\n')
                continue

            show_entries(entries)
            if len(entries) == 1 and entries[0][2] >= 0.6:
                print(Fore.GREEN + '\nSingle good entry for this author\n')
            else:
                entries = user_select_entries(entries)

            with sqlite3.connect(DBFILE) as connection:
                connection.executemany('INSERT INTO authors VALUES (?,?,?,?)',
                    ((namefield, ateneo, e[0].ID, json.dumps(e[1]))
                        for e in entries))

        except KeyboardInterrupt: break
        except Exception:
            traceback.print_exc()
            raw_input(Fore.RED + '\nERROR processing ' + namefield +
                          '. Press any key to continue..')

if __name__ == '__main__':
    from config import APIKEY, FILENAME, DBFILE
    main(APIKEY, FILENAME, DBFILE)
