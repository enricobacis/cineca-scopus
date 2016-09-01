from collections import namedtuple
from operator import itemgetter
from tabulate import tabulate
from scopus import ScopusClient
from utils import read_csv, split_name, iterate_names, fuzzy_score
import os.path
import sqlite3
import json
import sys

from colorama import init, Fore
init(autoreset=True)

from config import APIKEY, FILENAME, DBFILE

Entry = namedtuple('Entry', ['ID', 'affil_country', 'affil_city', 'affil_name',
                             'name', 'surname', 'documents', 'comp'])

def get_frequency_for_area(entry, abbrev):
    try:
        area = entry['subject-area']
        if isinstance(area, dict): assert area['@abbrev'] == abbrev
        else: area = [a for a in area if a['@abbrev'] == abbrev][0]
        return int(area['@frequency'])
    except:
        return 0

def make_entry(entry):
    return Entry(
        ID=entry['dc:identifier'].partition(':')[2],
        affil_country=entry['affiliation-current']['affiliation-country'],
        affil_city=entry['affiliation-current']['affiliation-city'],
        affil_name=entry['affiliation-current']['affiliation-name'],
        name=entry['preferred-name']['given-name'],
        surname=entry['preferred-name']['surname'],
        documents=int(entry['document-count']),
        comp=get_frequency_for_area(entry, 'COMP'))

def entry_score(query, entry):
    return max(fuzzy_score(query, entry.affil_name),
               fuzzy_score(query, entry.affil_city))

def sorted_entries(entries, ateneo):
    entries = [(make_entry(e), e) for e in entries]
    entries = [(e[0], e[1], entry_score(ateneo,e[0])) for e in entries]
    key = lambda entry: (entry[2], entry[0].comp, entry[0].documents)
    return sorted(entries, key=key, reverse=True)

def get_entries(sc, namefield):
    for name, surname in iterate_names(*split_name(namefield)):
        entries = sc.get_authors(name, surname, 'Italy', 'COMP')
        if entries: return entries
    return []

def show_entries(entries, namefield, ateneo):
    headers = ('idx', '% match') + Entry._fields
    print '\n' + (' %s, %s ' % (namefield, ateneo)).center(80, '=') + '\n'
    print tabulate([[i, e[2]*100.] + list(e[0]) for i,e in enumerate(entries)],
                   headers=headers, tablefmt="grid")

def user_select_entries(entries, namefield, ateneo):
    while True:
        inp = raw_input(Fore.YELLOW + '\ncomma separated indexes: ')
        try:
            chosen = map(int, inp.strip().split(','))
            if min(chosen)<0 or max(chosen)>=len(entries): raise ValueError
            print chosen
            return [entries[c] for c in chosen]
        except ValueError:
            print(Fore.RED + 'Indexes must be between 0 and %d' % len(entries))

def init_db(dbfile):
    if os.path.isfile(dbfile):
        inp = raw_input(Fore.RED + "Database file already exists. " +
                        "Type 'yes' to append, anything else to quit: ")
        if inp.strip() != 'yes': sys.exit(0)

    with sqlite3.connect(dbfile) as connection:
        connection.execute(
                'CREATE TABLE IF NOT EXISTS authors(author, ateneo, id, entry)')

if __name__ == '__main__':
    sc = ScopusClient(APIKEY)
    init_db(DBFILE)
    for row in read_csv(FILENAME):
        namefield, ateneo = row['Cognome e Nome'], row['Ateneo']

        try:
            entries = sorted_entries(get_entries(sc, namefield), ateneo)
            show_entries(entries, namefield, ateneo)
            if len(entries) == 0:
                print(Fore.RED + '\nNo entries for this author\n')
                continue
            elif len(entries) == 1 and entries[0][2] >= 0.6:
                print(Fore.GREEN + '\nSingle good entry for this author\n')
            else:
                entries = user_select_entries(entries, namefield, ateneo)

            with sqlite3.connect(DBFILE) as connection:
                connection.executemany('INSERT INTO authors VALUES (?,?,?)',
                    ((namefield, ateneo, e[0].ID, json.dumps(e[1]))
                        for e in entries))

        except KeyboardInterrupt:
            break
        except:
            raw_input(Fore.RED + '\nERROR processing ' + namefield +
                      '. Press any key to continue..')
